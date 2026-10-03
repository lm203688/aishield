#!/usr/bin/env node
"use strict";
/**
 * AIShield MCP Server
 *
 * OWASP MCP Top 10 aligned security scanner.
 * Core tools: scan / guardrail / prompt_check / banned_words / rug_pull / handshake / digest
 * Laya tools: laya_precheck (本地决策模型初筛) / laya_shadow_stats (影子判定台账)
 * Plus: evidence_* / chain_* / connector_* / contributor_* / agent_infra_* tool groups.
 *
 * Usage:
 *   npx aishield-mcp-server
 *
 * Env:
 *   AISHIELD_API_URL      — backend API URL (default: https://api.aishield.tools)
 *   AISHIELD_API_KEY      — optional API key for higher rate limits
 *   AISHIELD_LAYA_URL     — local Laya HTTP service (default: http://127.0.0.1:8188)
 *   AISHIELD_LAYA_SHADOW  — 'off' disables the shadow decision ledger (default: on)
 *   AISHIELD_LAYA_LEDGER  — shadow ledger JSONL path (default: see LAYA_LEDGER)
 */
Object.defineProperty(exports, "__esModule", { value: true });
const mcp_js_1 = require("@modelcontextprotocol/sdk/server/mcp.js");
const stdio_js_1 = require("@modelcontextprotocol/sdk/server/stdio.js");
const promises_1 = require("node:fs/promises");
const zod_1 = require("zod");
// 版本单一真源。由 scripts/sync_version.py 统一维护，CI 的版本一致性门禁会校验它，
// 因此这里不再手写数字 —— 硬编码的 '3.0.0' 曾与已发布的 4.2.x 差了一个大版本。
const SERVER_VERSION = '4.11.0';
const API_BASE = process.env.AISHIELD_API_URL || 'https://api.aishield.tools';
const API_KEY = process.env.AISHIELD_API_KEY || '';
// ── Laya 本地决策模型集成 (可选) ──
//
// Laya 421M 是非生成式决策模型 (ModernBERT + 决策头)，输出校准概率，
// 不生成文本、不支持 tools。适合做 agent 调用链路上的快速护栏初筛
// (越狱/注入/敏感数据/话题分类)，零成本、本地、~500ms/条。
//
// 启用方式: 启动本地 Laya HTTP 服务
//   python C:\Users\xing\.workbuddy\laya\laya_infer.py serve --port 8188
// 或通过环境变量 AISHIELD_LAYA_URL 覆盖地址。
//
// 失败降级: Laya 服务不可达时 aishield_laya_precheck 返回明确启动指引，
// 不影响 aishield 其他 7 个工具。
//
// 质量提示: 英文 checkpoint (en) 对中文 prompt 误报率高，中文请用 checkpoint=ml。
// harm_severity 置信度低 (0.03-0.38)，仅作参考。零样本不可直接投产。
const LAYA_URL = (process.env.AISHIELD_LAYA_URL || 'http://127.0.0.1:8188').replace(/\/$/, '');
// ── Laya Shadow 判定点 (借鉴 mu-agent 影子模式: 只记录, 不拦截, 不改任何行为) ──
//
// aishield_prompt_check / aishield_laya_precheck 运行时, 后台静默请求本地 Laya,
// 把「Laya 判定 vs 远程规则引擎判定」的配对结果追加进 JSONL 台账。
// 目的: 零成本攒一份自有配对标注数据, 供 Laya 温度校准/微调使用
// (零样本质量红线: ml checkpoint 对正常中文 jailbreak=1.0, harm_severity 不可用)。
//
// 安全性: 影子调用 8s 超时、全部异常就地吞掉、绝不向上抛错、绝不阻塞主判定 ——
// Laya 服务挂了也只是台账里多一条 shadow_error, 工具行为与 4.8.3 完全一致。
const LAYA_LEDGER = process.env.AISHIELD_LAYA_LEDGER || 'C:\\Users\\xing\\.workbuddy\\laya\\shadow_ledger.jsonl';
const LAYA_SHADOW_ON = (process.env.AISHIELD_LAYA_SHADOW || 'on').toLowerCase() !== 'off';
function layaShadowJudge(prompt, source, rules) {
    if (!LAYA_SHADOW_ON)
        return;
    const t0 = Date.now();
    fetch(`${LAYA_URL}/decide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: prompt, checkpoint: 'en', questions: 'guard', threshold: 0.5 }),
        signal: AbortSignal.timeout(8000),
    })
        .then(async (res) => {
        const entry = {
            ts: new Date().toISOString(),
            kind: 'shadow',
            source,
            checkpoint: 'en',
            questions: 'guard',
            prompt_head: String(prompt).slice(0, 200),
            rules: rules ?? null,
            laya_ok: res.ok,
            ms: Date.now() - t0,
        };
        if (res.ok) {
            const data = await res.json();
            const it = Array.isArray(data.items) ? data.items[0] : undefined;
            const r = it?.result || {};
            entry.laya = { answers: r.answers ?? null, latency_ms: r.ms ?? null };
        }
        await (0, promises_1.appendFile)(LAYA_LEDGER, JSON.stringify(entry) + '\n', 'utf8');
    })
        .catch(async (err) => {
        // 台账写失败也吞掉 —— 影子模式对主链路必须完全零影响。
        try {
            await (0, promises_1.appendFile)(LAYA_LEDGER, JSON.stringify({
                ts: new Date().toISOString(),
                kind: 'shadow_error',
                source,
                err: String(err?.message || err).slice(0, 160),
                ms: Date.now() - t0,
            }) + '\n', 'utf8');
        }
        catch {
            /* swallow */
        }
    });
}
// ── API Helper ──
async function apiCall(path, body, timeoutMs = 30000) {
    const url = `${API_BASE}${path}`;
    const headers = {
        'Content-Type': 'application/json',
        'User-Agent': `AIShield-MCP-Server/${SERVER_VERSION}`,
    };
    if (API_KEY)
        headers['Authorization'] = `Bearer ${API_KEY}`;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers,
            body: JSON.stringify(body),
            signal: controller.signal,
        });
        if (!res.ok) {
            const text = await res.text().catch(() => '');
            throw new Error(`AIShield API ${res.status}: ${text.slice(0, 200)}`);
        }
        return await res.json();
    }
    finally {
        clearTimeout(timer);
    }
}
// ── Audit response unwrapping ──
//
// /api/v1/audit 的成功响应形状是：
//   { success, score, badge_level, risk_level, report: { overall_score, findings, ... } }
// 顶层只有三个便捷字段，五维分数 / findings / owasp_coverage 全都在 report 里。
//
// 早期版本直接读 data.overall_score —— 这个键在顶层根本不存在，于是每次扫描都显示
// "Score: 0/100"、五维全 0、findings 为空；guardrail 更糟：score 恒为 0 就永远走到
// BLOCK 分支，对再干净的仓库也判"不要安装"。一个对什么都报警的安全工具，
// 和没有安全工具是一回事，甚至更坏 —— 用户会直接卸载它。
//
// 这里统一解包，同时兼容「扁平响应」的老部署（自建 API 可能还没升级）。
function unwrapAudit(data) {
    const hasNested = data && typeof data.report === 'object' && data.report !== null;
    const report = hasNested ? data.report : (data || {});
    // 顶层 score 优先（API 承诺与 report.overall_score 恒等），回退到嵌套值。
    const score = toNum(data?.score, toNum(report?.overall_score, 0));
    return { report, score };
}
function toNum(v, fallback) {
    return typeof v === 'number' && Number.isFinite(v) ? v : fallback;
}
// ── Create Server ──
const server = new mcp_js_1.McpServer({
    name: 'AIShield Security Scanner',
    version: SERVER_VERSION,
    description: 'OWASP MCP Top 10 + Agentic AI Top 10 aligned security scanner — 253 rules, 5-dimension scoring, tool poisoning & supply chain detection, per-finding file:line:col anchors with remediation',
});
// ══════════════════════════════════════════════════════════════
// Tool 1: Full Security Scan
// ══════════════════════════════════════════════════════════════
server.tool('aishield_scan', `AIShield安全扫描 — 扫描MCP Server/AI工具的安全风险。

对齐OWASP MCP Top 10 (2025 v0.1) 与 Agentic AI Top 10，253条规则覆盖两套风险分类。
5维评分: 安全(40%)/权限(20%)/数据处理(20%)/供应链(10%)/可靠性(10%)
返回: 评分 + 风险等级 + OWASP合规矩阵 + 修复建议
每条 finding 带 file:line:col 精确锚点 + 证据片段 + 稳定 rule_id + 具体修复动作`, {
    source_url: zod_1.z.string().describe('GitHub repo URL of the tool to scan'),
    tool_type: zod_1.z.enum(['mcp', 'skill', 'gpt', 'prompt']).default('mcp').describe('Tool type'),
    name: zod_1.z.string().optional().describe('Tool name (optional)'),
}, async ({ source_url, tool_type, name }) => {
    try {
        const data = await apiCall('/api/v1/audit', { source_url, tool_type, name });
        return formatScanResult(data);
    }
    catch (e) {
        return { content: [{ type: 'text', text: `AIShield scan failed: ${e.message}` }] };
    }
});
// ══════════════════════════════════════════════════════════════
// Tool 2: Pre-install Guardrail
// ══════════════════════════════════════════════════════════════
server.tool('aishield_guardrail', `AIShield安装前安全检查 — 在安装任何MCP/AI工具前调用此工具。

返回pass/block判定 + 评分 + OWASP合规矩阵。
建议在安装任何第三方MCP Server前自动调用此工具。`, {
    source_url: zod_1.z.string().describe('GitHub repo URL of the tool to check'),
    auto_block: zod_1.z.boolean().default(true).describe('If true, return block verdict for unsafe tools'),
}, async ({ source_url, auto_block }) => {
    try {
        const raw = await apiCall('/api/v1/audit', { source_url, tool_type: 'mcp', auto_block });
        const { report: data, score } = unwrapAudit(raw);
        const risk = raw?.risk_level || data.risk_level || 'unknown';
        const badge = raw?.badge_level || data.badge_level || 'none';
        let verdict;
        if (score >= 70) {
            verdict = '✅ PASS — Safe to install';
        }
        else if (score >= 55 && !auto_block) {
            verdict = '⚠️ WARN — Review recommended before installing';
        }
        else {
            verdict = '❌ BLOCK — Security risks detected, DO NOT install';
        }
        const owasp = data.owasp_coverage || {};
        const covered = (owasp.covered || []).join(', ') || 'None';
        const summary = [
            `AIShield Guardrail Verdict: ${verdict}`,
            ``,
            `Score: ${score}/100 | Risk: ${risk} | Badge: ${badge}`,
            `OWASP Categories Covered: ${covered} (${owasp.covered_count || 0}/10)`,
            `Findings: ${data.total_findings || 0} issues`,
            ``,
            `Recommendations:`,
            ...(data.recommendations || []).map((r) => `  • ${r}`),
        ].join('\n');
        return { content: [{ type: 'text', text: summary }] };
    }
    catch (e) {
        return { content: [{ type: 'text', text: `Guardrail check failed: ${e.message}. CAUTION: Do not install until verified.` }] };
    }
});
// ══════════════════════════════════════════════════════════════
// Tool 3: Prompt Injection Detection
// ══════════════════════════════════════════════════════════════
server.tool('aishield_prompt_check', `Prompt安全检测 — 检测用户输入的Prompt是否存在注入/越狱/数据外传风险。

支持中文和英文，覆盖: 越狱指令/身份切换/系统提示窃取/数据外传/角色扮演注入/零宽字符/Unicode编码`, {
    prompt: zod_1.z.string().min(10).describe('待检测的Prompt文本（至少10个字符）'),
}, async ({ prompt }) => {
    try {
        const data = await apiCall('/api/v1/prompt-check', { prompt });
        // 影子判定点: 后台记录 Laya 判定 vs 规则引擎判定的配对数据, 不阻塞不拦截。
        layaShadowJudge(prompt, 'prompt_check', { safe: data.safe, score: data.score, risk: data.risk });
        const safe = data.safe ? '✅ SAFE' : '❌ UNSAFE';
        const summary = [
            `Prompt安全检测结果: ${safe}`,
            `评分: ${data.score}/100 | 风险: ${data.risk || 'unknown'}`,
            ``,
            data.summary || '',
            ``,
            `发现的问题:`,
            ...(data.findings || []).map((f) => formatFinding(f)),
        ].join('\n');
        return { content: [{ type: 'text', text: summary }] };
    }
    catch (e) {
        return { content: [{ type: 'text', text: `Prompt检测失败: ${e.message}` }] };
    }
});
// ══════════════════════════════════════════════════════════════
// Tool 4: Chinese Banned Words Check
// ══════════════════════════════════════════════════════════════
server.tool('aishield_banned_words', `中文违禁词检测 — 检测文本中的违禁词/敏感词。

覆盖6大平台: 微信/抖音/小红书/B站/知乎/微博
返回: 违禁词列表 + 法律条文 + 罚款金额 + 替换建议`, {
    text: zod_1.z.string().describe('待检测文本'),
    platform: zod_1.z.enum(['douyin', 'xiaohongshu', 'wechat', 'weibo', 'bilibili', 'kuaishou', 'all']).default('all').describe('目标平台'),
}, async ({ text, platform }) => {
    try {
        const data = await apiCall('/api/v1/banned-words', { text, platform });
        return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
    }
    catch (e) {
        return { content: [{ type: 'text', text: `违禁词检测失败: ${e.message}` }] };
    }
});
// ══════════════════════════════════════════════════════════════
// Tool 5: Rug Pull Detection
// ══════════════════════════════════════════════════════════════
server.tool('aishield_rug_pull', `Rug Pull检测 — 检查MCP工具是否在版本更新中移除安全代码或新增可疑网络请求。

对比最近commit diff，检测: 安全代码删除、新增网络请求、权限扩大、大量代码删除。
返回风险等级(critical/high/medium/low/safe)和具体发现。`, {
    source_url: zod_1.z.string().describe('GitHub repo URL'),
}, async ({ source_url }) => {
    try {
        const data = await apiCall('/api/v1/rug-pull', { source_url });
        const risk = data.rug_pull_risk || 'unknown';
        const score = data.rug_pull_score || 0;
        const lines = [
            `AIShield Rug Pull Detection`,
            `${'═'.repeat(40)}`,
            `Risk: ${risk} | Score: ${score}/100`,
            `Commits analyzed: ${data.commits_analyzed || 0}`,
            `Findings: ${data.total_findings || 0}`,
        ];
        if (data.findings && data.findings.length > 0) {
            lines.push('', '── Findings ──');
            for (const f of data.findings.slice(0, 10)) {
                lines.push(formatFinding(f));
            }
        }
        return { content: [{ type: 'text', text: lines.join('\n') }] };
    }
    catch (e) {
        return { content: [{ type: 'text', text: `Rug pull check failed: ${e.message}` }] };
    }
});
// ══════════════════════════════════════════════════════════════
// Tool 6: MCP Handshake Verification
// ══════════════════════════════════════════════════════════════
server.tool('aishield_handshake', `MCP握手验证 — 分析MCP配置、检测npx自动安装风险、敏感环境变量、工具描述异常长度。

提取README/package.json中的MCP配置，分析: npx -y风险、敏感env变量、远程URL安全性、
工具描述长度（>500字符可能隐藏指令）。如果是HTTP类型MCP，尝试实际握手。`, {
    source_url: zod_1.z.string().describe('GitHub repo URL'),
}, async ({ source_url }) => {
    try {
        const data = await apiCall('/api/v1/handshake', { source_url });
        const status = data.handshake_status || 'unknown';
        const lines = [
            `AIShield MCP Handshake Verification`,
            `${'═'.repeat(40)}`,
            `Status: ${status}`,
            `Configs found: ${data.configs_found || 0}`,
            `Files analyzed: ${data.files_analyzed || 0}`,
            `Findings: ${data.total_findings || 0}`,
        ];
        if (data.findings && data.findings.length > 0) {
            lines.push('', '── Findings ──');
            for (const f of data.findings.slice(0, 10)) {
                lines.push(formatFinding(f));
            }
        }
        if (data.configs && data.configs.length > 0) {
            lines.push('', '── MCP Configs ──');
            for (const c of data.configs.slice(0, 3)) {
                lines.push(`  ${JSON.stringify(c).slice(0, 100)}`);
            }
        }
        return { content: [{ type: 'text', text: lines.join('\n') }] };
    }
    catch (e) {
        return { content: [{ type: 'text', text: `Handshake check failed: ${e.message}` }] };
    }
});
// ══════════════════════════════════════════════════════════════
// Tool 7: Compact Trust Digest
// ══════════════════════════════════════════════════════════════
//
// 一个 agent 每轮对话都要回答同一个问题「这个东西我能不能信」。完整裁决信封
// 里有一个字段能用、二十个字段用不上，每次都拉一遍等于把同一份不变的内容反复
// 塞进上下文。这个工具只回几百字节 + 一个内容指纹：指纹没变就不必再拉。
//
// 借的是 Cache-to-Cache 那条观察（紧凑的语义载体优于整份文本重传），落地为纯
// 工程压缩 —— 不动模型内部，不需要任何模型侧配合。
server.tool('aishield_digest', `AIShield紧凑信任摘要 — 几百字节拿到结论，适合每轮都要判断"能不能信"的 agent。

输入三选一:
  configs     — {path: 文件内容} 的 MCP 客户端配置映射（静态分析，绝不执行其中命令）
  source_url  — 只要一个远程仓库 URL，取现成的信任裁决
  scan_result — 已有扫描结果，只做压缩

返回: 分数 + 风险等级 + 严重度分布 + 首 N 条 + content fingerprint。
指纹对同一份配置恒定不变 —— 存下来，下一轮先比指纹，没变就不必重复拉取。
风险等级绝不比实际找到的最严重 finding 更轻（有 high 就不会报 safe），摘要里也不会出现明文凭证。`, {
    source_url: zod_1.z.string().optional().describe('GitHub repo URL — return the current verdict as a digest'),
    configs: zod_1.z.record(zod_1.z.any()).optional().describe('{path: file content} MCP client config map (static analysis only)'),
    scan_result: zod_1.z.record(zod_1.z.any()).optional().describe('An existing scan result to compress'),
    max_findings: zod_1.z.number().int().min(0).max(20).default(3).describe('How many top findings to include'),
}, async ({ source_url, configs, scan_result, max_findings }) => {
    try {
        const body = { max_findings: max_findings ?? 3 };
        if (configs)
            body.configs = configs;
        else if (scan_result)
            body.scan_result = scan_result;
        else if (source_url)
            body.source_url = source_url;
        else {
            return {
                content: [{ type: 'text', text: 'Provide one of: configs, scan_result, source_url' }],
            };
        }
        const d = await apiCall('/api/v1/trust/digest', body);
        const counts = d.severity_counts || {};
        const lines = [
            `AIShield Trust Digest (${d.schema || 'aishield-digest/v1'})`,
            `${'─'.repeat(44)}`,
            `Score:   ${d.score === null || d.score === undefined ? 'n/a' : d.score} / 100`,
            `Risk:    ${d.risk || 'unknown'}${d.worst_severity ? `  (worst finding: ${d.worst_severity})` : ''}`,
            `Subject: ${d.subject || 'n/a'}`,
            `Findings: ${d.findings_total === null || d.findings_total === undefined ? 'n/a' : d.findings_total}  ${JSON.stringify(counts)}`,
            `Fingerprint: ${d.fingerprint || 'n/a'}`,
        ];
        if (Array.isArray(d.top) && d.top.length > 0) {
            lines.push('', '── Top ──');
            for (const t of d.top) {
                lines.push(`  [${t.severity || '?'}] ${t.type || '?'}${t.owasp ? ' (' + t.owasp + ')' : ''}`);
            }
        }
        lines.push('', 'Cache on the fingerprint: same fingerprint = same verdict, no need to re-fetch.');
        return { content: [{ type: 'text', text: lines.join('\n') }] };
    }
    catch (e) {
        return { content: [{ type: 'text', text: `Digest failed: ${e.message}` }] };
    }
});
// ══════════════════════════════════════════════════════════════
// Tool 8: Laya 本地决策模型快速初筛 (可选, 需本地 Laya 服务)
//
// 与远程 aishield 扫描互补: 本地 421M 非生成式决策模型，输出校准概率，
// ~500ms/条、零成本、数据不出本地。适合做 agent 调用链路上的快速护栏初筛。
// 失败降级: Laya 服务不可达时返回明确启动指引，不影响其他 7 个工具。
// ══════════════════════════════════════════════════════════════
server.tool('aishield_laya_precheck', `本地 Laya 421M 决策模型快速初筛 — 对 prompt 做越狱/注入/敏感数据/话题分类判定。

与远程 aishield 扫描互补: 本地、零成本、~500ms/条、数据不出本地。
适合做 agent 调用链路上的快速护栏初筛 (提交前确认、离线批筛)。

注意:
  - 非生成式模型，只输出校准概率，不生成文本
  - 英文 checkpoint (en) 对中文 prompt 误报率高，中文请用 checkpoint=ml
  - harm_severity 置信度低 (0.03-0.38)，仅作参考
  - 零样本不可直接投产，落地前需在自有集上微调/温度校准
  - 需要本地 Laya HTTP 服务运行 (默认 http://127.0.0.1:8188，可用 AISHIELD_LAYA_URL 覆盖)

返回: 每个问题的校准概率 + 置信度 + 是否超阈值`, {
    prompt: zod_1.z.string().min(1).describe('待检测的文本 (prompt 或任意字符串)'),
    checkpoint: zod_1.z.enum(['en', 'ml']).default('en').describe('checkpoint: en=英文, ml=多语言(中文用)'),
    questions: zod_1.z.enum(['guard', 'email', 'triage', 'moderation', 'router']).default('guard').describe('问题预设'),
    threshold: zod_1.z.number().min(0).max(1).default(0.5).describe('判定阈值'),
}, async ({ prompt, checkpoint, questions, threshold }) => {
    try {
        const res = await fetch(`${LAYA_URL}/decide`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: prompt, checkpoint, questions, threshold }),
            signal: AbortSignal.timeout(30000),
        });
        if (!res.ok) {
            const text = await res.text().catch(() => '');
            return {
                content: [{
                        type: 'text',
                        text: `Laya HTTP ${res.status}: ${text.slice(0, 300)}`,
                    }],
            };
        }
        const data = await res.json();
        // 显式调用同样入台账 (kind=shadow, source=explicit_precheck), 供校准数据集积累。
        layaShadowJudge(prompt, 'explicit_precheck');
        return { content: [{ type: 'text', text: formatLayaResult(data, threshold) }] };
    }
    catch (e) {
        const msg = e?.message || String(e);
        return {
            content: [{
                    type: 'text',
                    text: `Laya 本地服务不可达 (${LAYA_URL}): ${msg}\n\n` +
                        `启动方法:\n` +
                        `  python C:\\Users\\xing\\.workbuddy\\laya\\laya_infer.py serve --port 8188\n\n` +
                        `或通过环境变量覆盖地址:\n` +
                        `  AISHIELD_LAYA_URL=http://host:port`,
                }],
        };
    }
});
// ══════════════════════════════════════════════════════════════
// Tool: Laya Shadow Ledger Stats (影子判定台账统计)
// ══════════════════════════════════════════════════════════════
server.tool('aishield_laya_shadow_stats', `查看 Laya 影子判定台账统计 — 影子模式在 aishield_prompt_check / laya_precheck 运行时
后台静默记录「Laya 判定 vs 规则引擎判定」的配对数据 (只记录、不拦截)。

用途: 积累自有标注数据集, 供 Laya 温度校准/微调前评估质量红线修复进度。
返回: 总条数 / 影子命中率 / Laya 可用率 / 平均延迟 / 与规则引擎一致率 / 最近条目预览。`, {}, async () => {
    let raw;
    try {
        raw = await (0, promises_1.readFile)(LAYA_LEDGER, 'utf8');
    }
    catch {
        return {
            content: [{
                    type: 'text',
                    text: [
                        'Laya 影子台账: 空 (尚无记录)',
                        '',
                        `台账路径: ${LAYA_LEDGER}`,
                        '影子模式在 aishield_prompt_check / aishield_laya_precheck 每次运行时自动积累,',
                        '需要本地 Laya 服务在线 (start_laya.bat / laya_infer.py serve --port 8188)。',
                        `当前开关: ${LAYA_SHADOW_ON ? 'on' : 'off'} (AISHIELD_LAYA_SHADOW=off 可关闭)`,
                    ].join('\n'),
                }],
        };
    }
    const entries = [];
    for (const line of raw.split('\n')) {
        const s = line.trim();
        if (!s)
            continue;
        try {
            entries.push(JSON.parse(s));
        }
        catch { /* 跳过坏行 */ }
    }
    const shadows = entries.filter((e) => e.kind === 'shadow');
    const errors = entries.filter((e) => e.kind === 'shadow_error');
    const okShadows = shadows.filter((e) => e.laya_ok);
    const latencySamples = okShadows.map((e) => e.ms).filter((v) => typeof v === 'number');
    const meanMs = latencySamples.length
        ? Math.round(latencySamples.reduce((a, b) => a + b, 0) / latencySamples.length)
        : null;
    // 与规则引擎一致率: 规则 safe=false 视为 flagged;
    // Laya jailbreak/prompt_injection 任一 P>=0.5 视为 flagged。
    let paired = 0;
    let agree = 0;
    for (const e of okShadows) {
        const rules = e.rules;
        const answers = e.laya?.answers || {};
        if (!rules || typeof rules.safe !== 'boolean')
            continue;
        const rulesFlagged = rules.safe === false;
        const layaFlagged = (typeof answers.jailbreak?.p === 'number' && answers.jailbreak.p >= 0.5) ||
            (typeof answers.prompt_injection?.p === 'number' && answers.prompt_injection.p >= 0.5);
        paired += 1;
        if (rulesFlagged === layaFlagged)
            agree += 1;
    }
    const lines = [
        'Laya 影子判定台账统计',
        '─'.repeat(44),
        `台账路径: ${LAYA_LEDGER}`,
        `总条数: ${entries.length} (影子 ${shadows.length} / 错误 ${errors.length})`,
        `Laya 可用率: ${shadows.length ? Math.round((okShadows.length / shadows.length) * 100) + '%' : 'n/a'}`,
        `平均影子延迟: ${meanMs !== null ? meanMs + 'ms' : 'n/a'}`,
        `与规则引擎一致率: ${paired ? `${agree}/${paired} (${Math.round((agree / paired) * 100)}%)` : '尚无配对数据'}`,
        '',
    ];
    const recent = shadows.slice(-3).reverse();
    if (recent.length) {
        lines.push('最近条目:');
        for (const e of recent) {
            const rulesTxt = e.rules ? `rules_safe=${e.rules.safe}` : 'rules=n/a';
            lines.push(`  [${e.ts}] ${e.source} ${rulesTxt} ${String(e.prompt_head || '').slice(0, 60)}`);
        }
    }
    else {
        lines.push('尚无影子条目 — 跑一次 aishield_prompt_check 即开始积累。');
    }
    return { content: [{ type: 'text', text: lines.join('\n') }] };
});
// ══════════════════════════════════════════════════════════════
// Tool: Laya Semantic Gate (Allow/Ask/Deny 三档门禁, Jev Harness 白皮书式双层设计)
// ══════════════════════════════════════════════════════════════
// 第一层: 确定性规则 (只有这层能给出 DENY)。覆盖经典破坏性/渗透命令形态,
// 命令名黑白名单拦不住的语义漏洞交给第二层。
const GATE_RULES = [
    { name: 'rm_rf_root_home', re: /\brm\s+(?:-[a-zA-Z]+\s+)+(?:["']?)((?:\/|~|\$HOME|%USERPROFILE%))(?:\s|$|\/)/i, reason: '递归强删根/家目录' },
    { name: 'ps_remove_root', re: /Remove-Item\s+[^;\n]*-Recurse[^;\n]*-Force[^;\n]*[c-zC-Z]:\\\s*$/i, reason: 'PowerShell 递归强删盘符根路径' },
    { name: 'windows_rmdir', re: /\b(rd|rmdir)\s+\/s\/q\s+[c-zC-Z]:\\?\s*$/i, reason: 'Windows 递归静默删盘' },
    { name: 'del_tree', re: /\bdel\s+\/[sfq]{2,}\s+[c-zC-Z]:\\/i, reason: 'Windows 批量强删系统盘路径' },
    { name: 'mkfs_dd', re: /\b(mkfs(\.\w+)?|dd\s+if=\/dev\/(zero|random)\s+of=\/dev\/[shv]d)/i, reason: '文件系统/裸设备覆写' },
    { name: 'fork_bomb', re: /:\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:/, reason: 'fork 炸弹' },
    { name: 'chmod777_root', re: /\bchmod\s+-R\s+777\s+\/(\s|$)/i, reason: '根目录全开权限' },
    { name: 'pipe_remote_shell', re: /\b(curl|wget|fetch)\b[^|]*\|\s*(sudo\s+)?(ba|z|da|k)?sh\b/i, reason: '远端脚本直接管道进 shell (供应链执行)' },
    { name: 'ps_iex_download', re: /Invoke-(WebRequest|Expression)\b.*(\|\s*)?(iex|Invoke-Expression)\b/i, reason: 'PowerShell 下载即执行' },
    { name: 'eval_decoded', re: /\beval\s*\(\s*(atob|base64\s+-d|decode)\b/i, reason: '解码后 eval 执行' },
    { name: 'ssh_key_read', re: /\b(cat|type|Get-Content|less|more)\b[^;&|]*\.ssh[/\\]id_rsa/i, reason: '读取 SSH 私钥' },
    { name: 'cred_exfil_pipe', re: /(\.env|credentials?\.json|id_rsa|AWS_SECRET|PRIVATE\s+KEY)[^;&|]*\|\s*(curl|wget|nc\b|Invoke-WebRequest)/i, reason: '凭证管道外发' },
    { name: 'secret_to_webhook', re: /(AWS_SECRET_ACCESS_KEY|API_KEY|PRIVATE KEY)[^\n]{0,80}(https?:\/\/|webhook\.site|telegram|pastebin)/i, reason: '密钥拼接外发 URL' },
    { name: 'history_wipe', re: /\b(shred|wipe)\s+-[a-zA-Z]*u?[a-zA-Z]*\s+(\/var\/log|~\/\.bash_history)/i, reason: '销毁审计日志' },
];
// P1 校准产物 (calibrate_laya.py, 2026-09-29, seed n=48/ckpt):
// checkpoint 的 temperature_by_options 按"选项数"做键, 所有 noul 问题共享一个温度,
// 逐问题校准只能放在消费层后验应用。数值来自 calibration_report_{en,ml}.json 的 best_T。
// 应用后: en jailbreak NLL -29.3%, 校准后 P>=0.9 预测 100% 准确 (57.5% 覆盖);
//         ml jailbreak/injection 温度只能修置信度诚实度 (NLL -76%/-70%), 修不了 acc@0.5=0.75/0.85。
const CAL_T = {
    en: { jailbreak: 2.6, prompt_injection: 1.0 },
    ml: { jailbreak: 5.0, prompt_injection: 5.0 },
};
function calibrateP(p, T) {
    const eps = 1e-6;
    const v = Math.min(Math.max(p, eps), 1 - eps);
    return 1 / (1 + Math.exp(-Math.log(v / (1 - v)) / T));
}
server.tool('aishield_laya_gate', `命令/脚本三档语义门禁 (Allow/Ask/Deny) — Jev Harness 白皮书式双层设计。

第一层 (确定性规则): 13 条经典破坏形态正则 (递归删盘/fork 炸弹/远端脚本管道执行/SSH 私钥读取/
凭证外发等) — 只有这层能给出 DENY。
第二层 (Laya 语义判定): 规则未命中时, 用本地 Laya 对命令全文做越狱/注入语义判定 —
校准完成前只贡献 ASK (升级人工确认) 信号, 永不自动 DENY (置信度×后果分级原则)。

返回: verdict (ALLOW/ASK/DENY) + 命中规则/Laya 概率 + 延迟。
需要本地 Laya 服务在线 (AISHIELD_LAYA_URL, 默认 http://127.0.0.1:8188);
服务离线时按 fail_mode 处理: warn=放行但标注语义层不可用, closed=一律 ASK。`, {
    command: zod_1.z.string().min(1).describe('待检命令或脚本全文'),
    fail_mode: zod_1.z.enum(['warn', 'closed']).default('warn').describe('Laya 离线时: warn=放行+标注, closed=一律 ASK'),
    ask_threshold: zod_1.z.number().min(0).max(1).default(0.9).describe('校准后概率达到该值即升级 ASK (默认 0.9: 校准曲线上 P>=0.9 精度 100%)'),
}, async ({ command, fail_mode, ask_threshold }) => {
    const t0 = Date.now();
    // ── 第一层: 确定性规则 (可 DENY) ──
    for (const rule of GATE_RULES) {
        if (rule.re.test(command)) {
            return {
                content: [{
                        type: 'text',
                        text: [
                            `⛔ DENY — 命中确定性规则 [${rule.name}]`,
                            `原因: ${rule.reason}`,
                            `延迟: ${Date.now() - t0}ms (纯规则, 未调用 Laya)`,
                            ``,
                            `该命令匹配已知破坏性/渗透形态, 无论语义判定结果如何一律拒绝。`,
                            `如是误报, 请修改命令写法绕开该形态后重试, 或人工审核后执行。`,
                        ].join('\n'),
                    }],
            };
        }
    }
    // ── 第二层: Laya 语义判定 (只 ASK, 不 DENY) ──
    // CJK 检测: 含中文字符用 ml checkpoint, 否则 en
    const hasCJK = /[\u4e00-\u9fff]/.test(command);
    const checkpoint = hasCJK ? 'ml' : 'en';
    try {
        const res = await fetch(`${LAYA_URL}/decide`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: command, checkpoint, questions: 'guard', threshold: 0.5 }),
            signal: AbortSignal.timeout(10000),
        });
        if (!res.ok)
            throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const it = Array.isArray(data.items) ? data.items[0] : undefined;
        const answers = it?.result?.answers || {};
        // 后验温度校准 (P1 产物), ASK 阈值作用在校准后的概率上
        const tMap = CAL_T[checkpoint] || {};
        const pj = calibrateP(answers.jailbreak?.p ?? 0, tMap.jailbreak ?? 1.0);
        const pi = calibrateP(answers.prompt_injection?.p ?? 0, tMap.prompt_injection ?? 1.0);
        const rawJ = answers.jailbreak?.p ?? 0;
        const rawI = answers.prompt_injection?.p ?? 0;
        const maxP = Math.max(pj, pi);
        const layaMs = it?.result?.ms ?? null;
        layaShadowJudge(command, 'gate', { safe: maxP < ask_threshold, score: maxP, risk: maxP >= ask_threshold ? 'escalate' : 'ok' });
        const verdict = maxP >= ask_threshold ? 'ASK' : 'ALLOW';
        const lines = [
            `${verdict === 'ASK' ? '⚠️' : '✅'} ${verdict} — 规则层未命中, Laya 语义判定 (已校准)`,
            `checkpoint=${checkpoint}  jailbreak P=${pj.toFixed(4)} (raw ${rawJ.toFixed(4)})  prompt_injection P=${pi.toFixed(4)} (raw ${rawI.toFixed(4)})  (ask 阈值 ${ask_threshold})`,
            `延迟: 规则 ${Date.now() - t0 - (layaMs ?? 0)}ms + Laya ${layaMs ?? '?'}ms`,
        ];
        if (verdict === 'ASK') {
            lines.push('', `语义判定置信度达到升级阈值, 建议人工确认后再执行。`, `注: 校准完成前 Laya 信号只用于 ASK 升级, 不用于自动 DENY。`);
        }
        else {
            lines.push('', `注: 通过 = 规则层无命中且语义判定低风险; Laya 校准仍在进行 (影子台账持续积累), 高后果操作请保持人工复核习惯。`);
        }
        return { content: [{ type: 'text', text: lines.join('\n') }] };
    }
    catch (e) {
        const msg = e?.message || String(e);
        if (fail_mode === 'closed') {
            return {
                content: [{
                        type: 'text',
                        text: `⚠️ ASK — Laya 服务不可达 (${msg.slice(0, 120)}), fail_mode=closed 升级人工确认。\n启动: start_laya.bat 或 laya_infer.py serve --port 8188`,
                    }],
            };
        }
        return {
            content: [{
                    type: 'text',
                    text: [
                        `✅ ALLOW (语义层不可用) — 规则层未命中, 但 Laya 离线: ${msg.slice(0, 120)}`,
                        `延迟: ${Date.now() - t0}ms (仅规则层)`,
                        ``,
                        `⚠️ 本次判定未经语义第二层, 仅靠确定性规则。高后果操作请人工复核。`,
                        `启动 Laya: start_laya.bat 或 laya_infer.py serve --port 8188 (AISHIELD_LAYA_URL 可覆盖)`,
                    ].join('\n'),
                }],
        };
    }
});
// Helper: 格式化 Laya 决策结果
function formatLayaResult(data, threshold) {
    const lines = [];
    lines.push('Laya 本地决策模型初筛结果');
    lines.push('─'.repeat(44));
    const items = Array.isArray(data.items) ? data.items : (data.results || []);
    if (items.length === 0) {
        lines.push('(no results)');
        return lines.join('\n');
    }
    for (const it of items) {
        if (it.text)
            lines.push(`Text: ${it.text}`);
        const r = it.result || it;
        if (r.ms !== undefined)
            lines.push(`Latency: ${r.ms.toFixed(1)}ms`);
        const answers = r.answers || {};
        if (Object.keys(answers).length > 0) {
            lines.push('');
            for (const [q, a] of Object.entries(answers)) {
                const aObj = a;
                if (aObj.p !== undefined) {
                    const over = aObj.p >= threshold ? ' [OVER THRESHOLD]' : '';
                    lines.push(`  ${q}: P=${aObj.p.toFixed(4)}  conf=${(aObj.conf ?? 'n/a').toString()}${over}`);
                }
                else if (aObj.score !== undefined) {
                    lines.push(`  ${q}: score=${aObj.score.toFixed(3)}  conf=${(aObj.conf ?? 'n/a').toString()}`);
                }
                else if (aObj.choice !== undefined) {
                    lines.push(`  ${q}: choice="${aObj.choice}"  conf=${(aObj.conf ?? 'n/a').toString()}`);
                }
            }
        }
    }
    lines.push('');
    lines.push('Note: Laya 零样本不可直接投产。harm_severity 置信度低，仅供参考。');
    return lines.join('\n');
}
// ── Helper ──
function formatScanResult(raw) {
    const { report: data, score } = unwrapAudit(raw);
    const badge = raw?.badge_level || data.badge_level || 'none';
    const risk = raw?.risk_level || data.risk_level || 'unknown';
    const lines = [
        `AIShield Security Scan Report`,
        `${'═'.repeat(50)}`,
        `Tool: ${data.name || 'N/A'}`,
        `Score: ${score}/100 | Risk: ${risk} | Badge: ${badge}`,
        `Rules: ${data.rules_count || 0} | Findings: ${data.total_findings || 0}`,
        `Scanned: ${data.scanned_at || 'N/A'} | Engine: v${data.scanner_version || '4.0'}`,
        ``,
        `── 5-Dimension Scores ──`,
        `  Security:      ${data.security_score || 0}/100 (40%)`,
        `  Permissions:   ${data.permissions_score || 0}/100 (20%)`,
        `  Data Handling: ${data.data_handling_score || 0}/100 (20%)`,
        `  Supply Chain:  ${data.supply_chain_score || 0}/100 (10%)`,
        `  Reliability:   ${data.reliability_score || 0}/100 (10%)`,
        ``,
        `── OWASP MCP Top 10 Coverage ──`,
    ];
    const owasp = data.owasp_coverage || {};
    const covered = new Set(owasp.covered || []);
    for (let i = 1; i <= 10; i++) {
        const cat = `MCP${String(i).padStart(2, '0')}`;
        const mark = covered.has(cat) ? '✅' : '⬜';
        lines.push(`  ${mark} ${cat}`);
    }
    if (data.findings && data.findings.length > 0) {
        lines.push('');
        lines.push(`── Findings (${data.findings.length}) ──`);
        // Show critical and high only
        const important = data.findings.filter((f) => f.severity === 'critical' || f.severity === 'high');
        for (const f of important.slice(0, 15)) {
            lines.push(formatFinding(f));
        }
        if (important.length > 15) {
            lines.push(`  ... and ${important.length - 15} more`);
        }
    }
    if (data.recommendations && data.recommendations.length > 0) {
        lines.push('');
        lines.push('── Recommendations ──');
        for (const r of data.recommendations) {
            lines.push(`  • ${r}`);
        }
    }
    lines.push('');
    lines.push(`Badge: [![AIShield](https://img.shields.io/badge/AIShield-${badge}-${badge === 'gold' ? 'FFD700' : badge === 'silver' ? 'C0C0C0' : badge === 'bronze' ? 'CD7F32' : '999'})}](https://aishield.tools)`);
    return { content: [{ type: 'text', text: lines.join('\n') }] };
}
// Helper: render a finding with a precise anchor — file:line:col + evidence snippet
// + stable rule id + a concrete fix action. HeyClicky-style: point the user AT the
// exact element, don't just say "you have a vulnerability".
//
// rule_id takes priority over type: for static-pattern findings the type is always
// the useless constant "dangerous_pattern", while rule_id (MCP05-012 / GEN-9A3F) is
// what you actually look a rule up by. type is only a fallback for findings that
// predate the anchor fields.
//
// remediation is per-finding: the global `recommendations` list is only a handful of
// generic sentences and cannot be mapped back to a specific finding.
function formatFinding(f) {
    const sev = String(f?.severity || 'info').toUpperCase();
    const anchorParts = [f?.file, f?.lines].filter(Boolean);
    if (f?.col)
        anchorParts.push(`c${f.col}`);
    if (f?.commit_sha)
        anchorParts.push(`commit ${String(f.commit_sha).slice(0, 8)}`);
    const loc = anchorParts.join(':');
    let s = `  [${sev}] ${f?.description || '(no description)'}`;
    if (loc)
        s += `  @ ${loc}`;
    const rule = f?.rule_id || f?.type;
    if (rule)
        s += `  [${rule}]`;
    if (f?.evidence)
        s += `\n      ↳ ${String(f.evidence).slice(0, 160)}`;
    if (f?.remediation)
        s += `\n      ↪ Fix: ${String(f.remediation).slice(0, 200)}`;
    return s;
}
// ══════════════════════════════════════════════════════════════
// Ecosystem Activation Tools (v4.5.0+)
// ──────────────────────────────────────────────────────────────
// 5 支柱统一服务 API 代理：Discovery / Certification / Composition /
// Execution / Attestation。所有工具通过 api.aishield.tools 转发，
// 支持零依赖 HMAC 回退或 Ed25519 全异步签名。
//
// 与扫描/防护工具体系并行——扫描工具做"入站安全门"，生态工具做
// "跨 agent 治理 + 认证 + 证据"。R4-深化对齐 CyberGuard v0.13.0
// (GOAI 2026 Agent Infra 季军) 的证据规范。
//
// 命名规范：所有生态工具均以 `aishield_` 前缀命名，与扫描/防护工具
// 统一在同一个命名空间下，避免与第三方 MCP 工具冲突。
// ══════════════════════════════════════════════════════════════
// Helper: 通用 API 代理工具工厂，返回格式化的 JSON 响应文本。
// 所有生态工具都走这条通道，避免为每个端点手写 fetch + 错误处理。
//
// 后端分两类端点：
//   - handle_post(path, data): 需要请求体
//   - handle_get(path, query): 只吃 query string (leaderboard/snapshot/sandbox matrix 等)
// 本 helper 走 POST 通道；callEcoGet 走 GET 通道，query 参数通过 URL 拼接。
async function callEco(path, body) {
    try {
        const data = await apiCall(path, body);
        const header = `▶ ${path}\n`;
        return {
            content: [{
                    type: 'text',
                    text: header + JSON.stringify(data, null, 2),
                }],
        };
    }
    catch (e) {
        return {
            content: [{
                    type: 'text',
                    text: `✖ Ecosystem API call failed: ${e.message}\nEndpoint: ${path}`,
                }],
        };
    }
}
// Helper: GET 版代理，用于只读查询端点 (leaderboard/snapshot/sandbox matrix 等)。
async function callEcoGet(path) {
    try {
        const url = `${API_BASE}${path}`;
        const headers = {
            'User-Agent': `AIShield-MCP-Server/${SERVER_VERSION}`,
        };
        if (API_KEY)
            headers['Authorization'] = `Bearer ${API_KEY}`;
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 30000);
        try {
            const res = await fetch(url, { method: 'GET', headers, signal: controller.signal });
            if (!res.ok) {
                const text = await res.text().catch(() => '');
                throw new Error(`AIShield API ${res.status}: ${text.slice(0, 200)}`);
            }
            const data = await res.json();
            return {
                content: [{
                        type: 'text',
                        text: `▶ GET ${path}\n` + JSON.stringify(data, null, 2),
                    }],
            };
        }
        finally {
            clearTimeout(timer);
        }
    }
    catch (e) {
        return {
            content: [{
                    type: 'text',
                    text: `✖ Ecosystem API GET failed: ${e.message}\nEndpoint: ${path}`,
                }],
        };
    }
}
// ── Agent Card: 签名 / 验证 / 身份导出 ──
server.tool('aishield_sign_agent_card', `对 Agent Card 做 Ed25519 或 HMAC-SHA256 签名，产出可跨系统验证的 agent 身份凭证。

签名算法选择：
  - Ed25519（首选）：非对称，可离线验证，适合公开分发的 Agent Card
  - HMAC-SHA256（零依赖回退）：对称，需要共享 secret，适合私有部署

输入 card 字段：name / version / capabilities / endpoint / maintainer / trust_score / issued_at / expires_at。
返回 signature (base64url) + algorithm + signed_at + public_key。`, {
    card: zod_1.z.record(zod_1.z.any()).describe('Agent Card 对象 (name/version/capabilities/endpoint 等)'),
    public_key_b64: zod_1.z.string().optional().describe('Ed25519 公钥 (base64url，可选，用于验证)'),
    trust_score: zod_1.z.number().min(0).max(100).optional().describe('信任分 0-100'),
}, ({ card, public_key_b64, trust_score }) => callEco('/api/v1/agent-card/sign', { card, public_key: public_key_b64, trust_score }));
server.tool('aishield_verify_agent_card', `验证 Agent Card 的签名完整性，检测内容被篡改。

签名算法自动识别 (Ed25519 / HMAC)。篡改任一字段后重算的 signature 会与原值不匹配，
返回 signature_valid: false + 篡改检测摘要。

关键场景：安装第三方 agent 前，用它核对 agent card 是否被中间人修改过。`, {
    card: zod_1.z.record(zod_1.z.any()).describe('带 signature 的 Agent Card 对象'),
    public_key_b64: zod_1.z.string().optional().describe('Ed25519 公钥 (base64url)'),
}, ({ card, public_key_b64 }) => callEco('/api/v1/agent-card/verify', { card, public_key: public_key_b64 }));
server.tool('aishield_export_identity', `从 Agent Card 导出三态身份凭证：Ed25519 签名卡片 + KYA SD-JWT + Web Bot Auth header。

对齐标准：
  - KYA SD-JWT (Keyed Agent) — 可分割声明集合，支持委托链
  - Web Bot Auth (RFC draft, GoDaddy+Cloudflare 2026-04) — HTTP header bot 身份
  - ERC-8004 — Ethereum 钱包身份绑定（独立走 wrap_erc8004）

适合 agent 首次上架或跨平台迁移时批量导出身份包。`, {
    card: zod_1.z.record(zod_1.z.any()).describe('Agent Card 对象'),
    trust_score: zod_1.z.number().min(0).max(100).optional().describe('信任分'),
}, ({ card, trust_score }) => callEco('/api/v1/agent-card/identity', { card, trust_score }));
// ── Specialist Registry: 专业 agent 注册 ──
server.tool('aishield_register_specialist', `注册专业 agent 到 8 域 Registry (90 天 TTL)。

支持的域：legal / medical / finance / education / engineering / design / research / civic。
注册成功后 agent 会获得 agent_id，其他 agent 可通过 list_specialists 查询、跨域协作。

超过 90 天需调用 renew 续期，否则进入 lapsed 状态；被撤销的 agent 永久不可再注册同域。`, {
    agent_id: zod_1.z.string().optional().describe('agent ID (不填自动生成)'),
    domain: zod_1.z.enum(['legal', 'medical', 'finance', 'education', 'engineering', 'design', 'research', 'civic']).describe('专业域'),
    agent_card: zod_1.z.record(zod_1.z.any()).optional().describe('关联的 Agent Card (可选)'),
    description: zod_1.z.string().optional().describe('专业描述'),
    capabilities: zod_1.z.array(zod_1.z.string()).optional().describe('能力标签'),
    ttl_days: zod_1.z.number().min(1).max(365).default(90).describe('有效期（天）'),
}, ({ agent_id, domain, agent_card, description, capabilities, ttl_days }) => callEco('/api/v1/specialist/agents', { agent_id, domain, agent_card, description, capabilities, ttl_days }));
// ── ERC-8004: 钱包身份绑定 ──
server.tool('aishield_wrap_erc8004', `将以太坊钱包地址包装成 ERC-8004 agent 身份。

ERC-8004 是 Ethereum Foundation 2024 年底提出的 agent 身份标准，agent 通过钱包
地址获得链上可验证身份，可组合 on-chain 权限与治理角色。

地址格式：0x + 40 位十六进制。chain_id 常见：1=主网, 5=Goerli, 8453=Base, 42161=Arbitrum。`, {
    wallet_address: zod_1.z.string().regex(/^0x[0-9a-fA-F]{40}$/).describe('以太坊钱包地址'),
    chain_id: zod_1.z.number().default(1).describe('Chain ID'),
}, ({ wallet_address, chain_id }) => callEco('/api/v1/identity/erc8004/wrap', { wallet_address, chain_id }));
// ── Responsibility Chain ──
server.tool('aishield_chain_create', `创建责任链 (HMAC-SHA256 链式追加结构)。

责任链用于记录 agent 间的责任转移 / 委托 / 协作事件，形成不可篡改的审计轨迹。
链头带 HMAC 摘要，每次 append 都引用前一条的 HMAC，任何篡改都会导致后续所有 HMAC 失效。

返回 chain_id 后，用 chain_append 追加事件、chain_trace 追踪某个 output_ref 的完整链路。`, {
    chain_id: zod_1.z.string().optional().describe('自定义链 ID (不填自动生成)'),
}, ({ chain_id }) => callEco('/api/v1/chain', { chain_id }));
server.tool('aishield_chain_append', `向责任链追加一条记录。

每条记录包含 actor_id / action / target / payload / ts，自动生成 HMAC 摘要链。
append 后立即返回 verify 结果——如果链被外部修改过，verify 会返回 false。`, {
    chain_id: zod_1.z.string().describe('责任链 ID'),
    actor_id: zod_1.z.string().describe('执行者 ID'),
    action: zod_1.z.string().describe('动作描述'),
    target: zod_1.z.record(zod_1.z.any()).optional().describe('作用对象'),
    payload: zod_1.z.record(zod_1.z.any()).optional().describe('附加数据'),
    ts: zod_1.z.string().optional().describe('时间戳 (ISO8601，不填用当前)'),
}, ({ chain_id, actor_id, action, target, payload, ts }) => callEco(`/api/v1/chain/${encodeURIComponent(chain_id)}/append`, { actor_id, action, target, payload, ts }));
server.tool('aishield_chain_trace', `按 output_ref 反向追踪责任链，找出该产出物的完整责任路径。

例如：某个 AI 生成的报告由 3 个 agent 协作完成，可以用 output_ref 查到 A→B→C 的完整委托链，
并核对每一步的 HMAC 摘要是否完整。`, {
    chain_id: zod_1.z.string().describe('责任链 ID'),
    output_ref: zod_1.z.string().describe('产出物引用 ID'),
}, ({ chain_id, output_ref }) => callEco(`/api/v1/chain/${encodeURIComponent(chain_id)}/trace`, { output_ref }));
// ── Protocol Bridge ──
server.tool('aishield_protocol_translate', `MCP / A2A / ACP / AP2 协议间互译。

将 MCP tool call 翻译成 A2A message、ACP request 或 AP2 支付指令，反之亦然。
用于 agent 跨平台互通——不同厂商的 agent 用不同协议，bridge 提供统一入口。

支持的协议：mcp (Anthropic) / a2a (Google) / acp (Microsoft) / ap2 (Google Payments)。`, {
    protocol: zod_1.z.enum(['mcp', 'a2a', 'acp', 'ap2']).describe('目标协议'),
    payload: zod_1.z.record(zod_1.z.any()).describe('源协议 payload'),
    from_protocol: zod_1.z.enum(['mcp', 'a2a', 'acp', 'ap2']).optional().describe('源协议 (省略时自动识别)'),
}, ({ protocol, payload, from_protocol }) => callEco('/api/v1/bridge/translate', { protocol, payload, from_protocol }));
// ── Sandbox Backend ──
server.tool('aishield_sandbox_backend_current', `获取当前主机上被选中的 sandbox backend 及其能力摘要。

返回：
  - backend_name：当前选中的后端 (openshell / mcpguard / meclaw / cf-isolate / python-subprocess)
  - reason：为何选中此 backend
  - capabilities：能力布尔矩阵 (seccomp / landlock / namespaces / network-isolate / fs-isolate)
  - availability：可用性评级

与 sandbox_evaluate 的区别：本工具只返回当前 backend；sandbox_evaluate 是别名，
sandbox_backend_matrix 返回全部 5 后端的完整能力矩阵。`, {}, () => callEcoGet('/api/v1/sandbox/backend/current'));
server.tool('aishield_sandbox_evaluate', `获取当前主机 sandbox backend 评估结果 (5 后端可用性自检)。

评估的 backend：
  - OpenShell (Google, 推荐)
  - mcpguard (Microsoft, 零依赖)
  - meclaw (Linux Landlock, 内核级)
  - CF isolate (Cloudflare, 边缘隔离)
  - python-subprocess (兜底)

返回每个 backend 的可用状态、能力评级、是否支持 seccomp / landlock / namespaces。
适合在部署 agent 前做环境自检，选最合适的隔离层。

与 sandbox_backend_current 的区别：本工具返回完整评估；backend_current 只返回当前选中的那一个。`, {}, () => callEcoGet('/api/v1/sandbox/backend/current'));
// ── Leaderboard ──
server.tool('aishield_leaderboard_query', `查询 4 维度 leaderboard 快照 (score/domain/provider/badge)。

聚合 4 个维度：
  - score: 按 trust_score 排序
  - domain: 按专业域分类 (legal/medical/finance/...)
  - provider: 按注册方聚合
  - badge: gold/silver/bronze 徽章统计

用于生态活跃度展示，也是 contributor 激励的依据之一。`, {
    dimension: zod_1.z.enum(['score', 'domain', 'provider', 'badge']).describe('查询维度'),
    limit: zod_1.z.number().min(1).max(100).default(20).describe('返回条数'),
}, ({ dimension, limit }) => callEcoGet(`/api/v1/leaderboard/snapshot?dimension=${dimension}&limit=${limit}`));
// ── Contributor ──
server.tool('aishield_contributor_register', `注册 contributor，进入 4 级激励体系。

级别：Contributor (基础贡献) → Reviewer (审核) → Maintainer (维护) → Trustee (托管)。
可通过 contributor_add_event 累加 6 类事件分：review/rule_patch/bug_report/attestation/doc/ship_gate。

贡献者等级决定其在 agent 注册审核、规则晋升、责任链裁决等环节的话语权。`, {
    contributor_id: zod_1.z.string().optional().describe('自定义 ID'),
    name: zod_1.z.string().describe('名称'),
    org: zod_1.z.string().optional().describe('组织'),
    email: zod_1.z.string().optional().describe('邮箱'),
    badges: zod_1.z.array(zod_1.z.string()).optional().describe('初始徽章'),
}, ({ contributor_id, name, org, email, badges }) => callEco('/api/v1/contributors', { contributor_id, name, org, email, badges }));
// ── Attestation: 信任凭证签发/验证 ──
server.tool('aishield_generate_attestation', `生成 Trust Attestation 凭证，为已扫描的 agent 签发信任凭证。

对齐 docs/trust-attestation-spec.md v1 schema，凭证包含：
  - issuer (签发方) / subject (被签发方)
  - verdict (安全/警告/危险)
  - coverage (扫描覆盖率矩阵)
  - attestation (五维分数)

生成的 attestation_id 可用于 verify 与 revoke，也可嵌入 Agent Card。`, {
    source_url: zod_1.z.string().optional().describe('被签发 agent 的源 URL'),
    scan_report: zod_1.z.record(zod_1.z.any()).optional().describe('已存在的扫描报告 (省略时自动扫描)'),
    issuer: zod_1.z.string().describe('签发方标识'),
    subject: zod_1.z.string().describe('被签发方标识'),
}, ({ source_url, scan_report, issuer, subject }) => callEco('/api/v1/attestations', { source_url, scan_report, issuer, subject }));
server.tool('aishield_verify_attestation', `验证 Trust Attestation 的完整性与有效性。

检查项：
  - JSON Schema v1 合规
  - HMAC 签名完整
  - 未过期
  - 未被 revoke
  - 签发方仍在信任列表

用于跨组织信任传递——第三方拿到 attestation 后可独立核验，无需访问签发方的扫描结果。`, {
    attestation_id: zod_1.z.string().describe('Attestation ID'),
    payload: zod_1.z.record(zod_1.z.any()).optional().describe('直接提供 payload (可选，与 ID 二选一)'),
}, ({ attestation_id, payload }) => callEco('/api/v1/attestations/verify', { attestation_id, payload }));
server.tool('aishield_list_attestations', `列出所有已签发的 Trust Attestation。`, {
    status: zod_1.z.enum(['active', 'revoked', 'expired', 'all']).default('all').describe('筛选状态'),
    limit: zod_1.z.number().min(1).max(200).default(50).describe('返回条数'),
}, ({ status, limit }) => callEco(`/api/v1/attestations?status=${status}&limit=${limit}`, {}));
server.tool('aishield_revoke_attestation', `撤销已签发的 Trust Attestation。

撤销后 attestation 状态变为 revoked，任何后续 verify 都会返回 invalid。
撤销事件也会写入 Evidence Bundle（如已关联）。`, {
    attestation_id: zod_1.z.string().describe('待撤销的 attestation ID'),
    reason: zod_1.z.string().describe('撤销原因'),
    revoked_by: zod_1.z.string().default('system').describe('操作者'),
}, ({ attestation_id, reason, revoked_by }) => callEco('/api/v1/attestations/revoke', { attestation_id, reason, revoked_by }));
// ── Specialist Domains: 列出 8 个专业域 ──
server.tool('aishield_list_specialist_domains', `列出 Specialist Registry 支持的 8 个专业域及其注册的 agent 数量。

域列表：legal / medical / finance / education / engineering / design / research / civic。
返回每域的注册数、活跃数、过期数、顶级 agent 列表。`, {
    include_lapsed: zod_1.z.boolean().default(false).describe('是否包含已过期的 agent'),
}, ({ include_lapsed }) => callEcoGet(`/api/v1/specialist/domains?include_lapsed=${include_lapsed}`));
// ══════════════════════════════════════════════════════════════
// Evidence Bundle Tools (R4-深化, 对齐 CyberGuard v0.13.0)
// ──────────────────────────────────────────────────────────────
// HMAC-SHA256 链式审计 + OCSF 1.1 + STIX 2.1 + ATT&CK v15 TTP +
// Proposal-Bound Approval + 双轮独立验证 + 回滚/归档。
// 参考: elsechord/CyberGuard v0.13.0, GOAI 2026 Agent Infra 3rd。
// ══════════════════════════════════════════════════════════════
server.tool('aishield_evidence_create', `创建 Evidence Bundle 实例 (HMAC-SHA256 链式审计容器)。

Bundle 是 agent 执行证据的容器，所有事件 / proposal / approval / execution / observe / rollback
都被组织为 OCSF 事件，并链接到 ATT&CK TTP 与 STIX Observable，可跨组织离线验证。

hmac_secret 提供时启用 HMAC 完整链路；不提供则走无密钥结构模式（仅供调试，不能跨组织验证）。

返回 run_id，后续所有 evidence_* 工具都用此 ID 定位 bundle。`, {
    run_id: zod_1.z.string().optional().describe('自定义 run_id (不填自动生成)'),
    hmac_secret: zod_1.z.string().optional().describe('HMAC 密钥 (可选，用于跨组织验证)'),
    title: zod_1.z.string().optional().describe('Bundle 标题'),
}, ({ run_id, hmac_secret, title }) => callEco('/api/v1/evidence', { run_id, hmac_secret, title }));
server.tool('aishield_evidence_add_event', `向 Evidence Bundle 追加一条 OCSF 事件。

event_type 遵循 OCSF 1.1 Event Class 命名 (audit.record / process.execution / network.connection ...)。
ttp 字段可选，用于关联 MITRE ATT&CK v15 TTP ID (T1003/T1485/...)。

每次追加后自动重算 HMAC 链，返回 verify 状态。`, {
    run_id: zod_1.z.string().describe('Bundle run_id'),
    event_type: zod_1.z.string().default('audit.record').describe('OCSF event type'),
    agent_id: zod_1.z.string().default('unknown').describe('执行 agent'),
    action: zod_1.z.string().default('record').describe('动作'),
    payload: zod_1.z.record(zod_1.z.any()).default({}).describe('事件 payload'),
    activity_id: zod_1.z.number().default(0).describe('OCSF activity_id'),
    outcome: zod_1.z.enum(['successful', 'failed', 'unknown']).default('successful').describe('结果'),
    reason: zod_1.z.string().optional().describe('原因说明'),
    ttp: zod_1.z.string().optional().describe('ATT&CK TTP ID (T1xxx / Gxxx / Sxxx / TAxxx)'),
}, ({ run_id, event_type, agent_id, action, payload, activity_id, outcome, reason, ttp }) => callEco(`/api/v1/evidence/${encodeURIComponent(run_id)}/events`, { event_type, agent_id, action, payload, activity_id, outcome, reason, ttp }));
server.tool('aishield_evidence_proposal', `创建 Proposal-Bound 提案，等待 approver 显式批准后才允许 dispatch。

对齐 CyberGuard v0.13.0 的 Proposal-Bound Approval：agent 生成的提案被 hash 锁定，
只有当 approver 的签名绑定到该 hash 时才允许执行。防止 approver 事后否认或修改被批准的内容。`, {
    run_id: zod_1.z.string().describe('Bundle run_id'),
    agent_id: zod_1.z.string().default('planner').describe('提案 agent'),
    action: zod_1.z.string().describe('建议动作'),
    target: zod_1.z.record(zod_1.z.any()).default({}).describe('作用目标'),
    parameters: zod_1.z.record(zod_1.z.any()).default({}).describe('动作参数'),
    rationale: zod_1.z.string().describe('提案理由'),
}, ({ run_id, agent_id, action, target, parameters, rationale }) => callEco(`/api/v1/evidence/${encodeURIComponent(run_id)}/proposals`, { agent_id, action, target, parameters, rationale }));
server.tool('aishield_evidence_approve', `批准 Evidence Bundle 中的提案 (Proposal-Bound Approval)。

批准记录独立于提案本身，二者通过 proposal_hash 双向绑定。篡改任意一边都会导致
verify_bundle_payload 失败。scope=task 表示单次任务、scope=session 表示整个会话。`, {
    run_id: zod_1.z.string().describe('Bundle run_id'),
    proposal_id: zod_1.z.string().describe('待批准的提案 ID'),
    approver_id: zod_1.z.string().default('unknown').describe('批准者 ID'),
    scope: zod_1.z.enum(['task', 'session', 'global']).default('task').describe('批准作用域'),
    expires_in: zod_1.z.number().min(60).max(86400).default(3600).describe('批准有效期（秒）'),
}, ({ run_id, proposal_id, approver_id, scope, expires_in }) => callEco(`/api/v1/evidence/${encodeURIComponent(run_id)}/proposals/${encodeURIComponent(proposal_id)}/approve`, { approver_id, scope, expires_in }));
server.tool('aishield_evidence_dispatch', `派发已批准的 proposal，让 executor agent 执行动作。

dispatch 前必须存在有效的 approval 记录（Proposal-Bound）。执行结果被记录为 OCSF 事件，
并进入双轮独立验证流程（第一轮 exec_result，第二轮 observe 观察实际效果）。`, {
    run_id: zod_1.z.string().describe('Bundle run_id'),
    approval_id: zod_1.z.string().describe('批准记录 ID'),
    executor_id: zod_1.z.string().default('unknown').describe('执行者 ID'),
    result: zod_1.z.boolean().default(true).describe('执行是否成功'),
    detail: zod_1.z.record(zod_1.z.any()).default({}).describe('执行详情'),
}, ({ run_id, approval_id, executor_id, result, detail }) => callEco(`/api/v1/evidence/${encodeURIComponent(run_id)}/dispatch`, { approval_id, executor_id, result, detail }));
server.tool('aishield_evidence_observe', `派发后的双轮独立验证：观察者独立核对 exec_result 是否真的落地生效。

对齐 CyberGuard 的 dual-round testing：第 1 轮 exec_result (executor 自证)，
第 2 轮 observe (第三方观察)。两轮结果都 pass 才标记为 verified，任一轮 fail 会
触发 rollback。round_no 支持多次观察累积证据。`, {
    run_id: zod_1.z.string().describe('Bundle run_id'),
    approval_id: zod_1.z.string().describe('关联的 approval ID'),
    observer_id: zod_1.z.string().default('unknown').describe('观察者 ID'),
    round_no: zod_1.z.number().min(1).max(10).default(1).describe('观察轮次'),
    passed: zod_1.z.boolean().default(true).describe('是否通过'),
    detail: zod_1.z.record(zod_1.z.any()).default({}).describe('观察详情'),
    confidence: zod_1.z.number().min(0).max(1).default(1).describe('观察置信度'),
}, ({ run_id, approval_id, observer_id, round_no, passed, detail, confidence }) => callEco(`/api/v1/evidence/${encodeURIComponent(run_id)}/observe`, { approval_id, observer_id, round_no, passed, detail, confidence }));
server.tool('aishield_evidence_rollback', `回滚已派发的动作，创建 rollback 事件并标记原 approval 失效。

对齐 CyberGuard 的 rollback 事件类型。rollback 记录本身也是 OCSF 事件，
同样进入 HMAC 链，事后可以完整还原"执行 → 观察 → 回滚"的三段证据。`, {
    run_id: zod_1.z.string().describe('Bundle run_id'),
    approval_id: zod_1.z.string().describe('待回滚的 approval ID'),
    operator_id: zod_1.z.string().default('unknown').describe('操作者 ID'),
    reason: zod_1.z.string().describe('回滚原因'),
}, ({ run_id, approval_id, operator_id, reason }) => callEco(`/api/v1/evidence/${encodeURIComponent(run_id)}/rollback`, { approval_id, operator_id, reason }));
server.tool('aishield_evidence_archive', `归档 Evidence Bundle，生成 archive manifest 用于离线分发。

归档后 bundle 变为只读，manifest 包含：
  - HMAC 摘要链完整状态
  - 所有 proposal / approval / dispatch / observe / rollback 记录
  - OCSF event class 分布
  - ATT&CK TTP 映射
  - STIX Observable 列表

manifest 可直接发送到第三方 audit 端点，无需重放原始事件。`, {
    run_id: zod_1.z.string().describe('Bundle run_id'),
    archiver_id: zod_1.z.string().default('system').describe('归档者 ID'),
}, ({ run_id, archiver_id }) => callEco(`/api/v1/evidence/${encodeURIComponent(run_id)}/archive`, { archiver_id }));
server.tool('aishield_verify_evidence_bundle', `离线验证 Evidence Bundle 的完整性 (跨组织传递后校验)。

传入已归档的 bundle payload (JSON) + hmac_secret，验证：
  - HMAC 摘要链完整
  - 所有 proposal_hash / approval_hash 双向匹配
  - OCSF event schema 有效
  - ATT&CK TTP ID 合法
  - STIX Observable 类型合法
  - global_seq 单调递增

对齐 CyberGuard 的 dual-round independent testing：即使脱离原组织环境也能
通过 secret 一致重放完整验证。任何一条失败都会明确指出是哪一条事件、哪个字段出错。`, {
    bundle: zod_1.z.record(zod_1.z.any()).describe('Bundle payload (JSON，来自 evidence_archive 的 manifest)'),
    hmac_secret: zod_1.z.string().optional().describe('HMAC 密钥'),
}, ({ bundle, hmac_secret }) => callEco('/api/v1/evidence/verify-payload', { bundle, hmac_secret }));
server.tool('aishield_chain_migrate_to_bundle', `把责任链 (Responsibility Chain v1.1) 迁移为 Evidence Bundle，用于审计格式升级。

迁移后：
  - 原链的所有 append 事件成为 Bundle 的 audit.record 事件
  - HMAC 摘要被重新计算并纳入新的 bundle 链
  - 原链保留只读，Bundle 是新的 canonical 记录

适合从旧责任链升级到 CyberGuard 兼容证据格式的迁移场景。`, {
    chain_id: zod_1.z.string().describe('源责任链 ID'),
    run_id: zod_1.z.string().optional().describe('目标 Bundle run_id'),
    hmac_secret: zod_1.z.string().optional().describe('HMAC 密钥'),
    archiver_id: zod_1.z.string().default('system').describe('归档者'),
}, ({ chain_id, run_id, hmac_secret, archiver_id }) => callEco('/api/v1/chain/migrate', { chain_id, run_id, hmac_secret, archiver_id }));
server.tool('aishield_ship_gate_run', `运行 10 状态发布门禁 (ANALYZE → BLIND_TEST → CHALLENGE → GATE → PREPARE → RELEASE → OBSERVE → ARCHIVE)。

对齐 CyberGuard 的双轮独立测试流程：BLIND_TEST 由独立 agent 执行，CHALLENGE 可对抗性
验证，GATE 综合 score/coverage/pass-fail 三态判定。

--no-auto-accept-challenge 关闭自动接受挑战阶段，走人工审核。
--emit-bundle 结束后自动创建 Evidence Bundle 记录整个生命周期。`, {
    target: zod_1.z.string().describe('扫描目标 (仓库 URL 或本地路径)'),
    target_type: zod_1.z.enum(['mcp', 'skill', 'gpt', 'prompt']).default('mcp').describe('目标类型'),
    emit_bundle: zod_1.z.boolean().default(false).describe('是否生成 Evidence Bundle'),
    auto_accept_challenge: zod_1.z.boolean().default(true).describe('自动接受 challenge 阶段'),
    hmac_secret: zod_1.z.string().optional().describe('HMAC 密钥 (用于 bundle)'),
}, ({ target, target_type, emit_bundle, auto_accept_challenge, hmac_secret }) => callEco('/api/v1/ship-gate/run', { target, target_type, emit_bundle, auto_accept_challenge, hmac_secret }));
// ── Leaderboard 补充：TOP 榜 / 快照 / 贡献者排行 ──
server.tool('aishield_leaderboard_top', `按 trust_score 排序查询 leaderboard TOP-N。

默认按 score 降序，返回前 N 名 agent 及其评分、徽章、所属域、注册方。
适合展示"本周最佳 agent"或用于推荐引擎的输入。`, {
    limit: zod_1.z.number().min(1).max(100).default(10).describe('返回条数'),
    domain: zod_1.z.string().optional().describe('按专业域过滤 (若指定，走 domains/{domain} 端点)'),
    min_score: zod_1.z.number().min(0).max(100).default(0).describe('最低分阈值 (无 domain 时生效)'),
}, ({ limit, domain, min_score }) => domain
    ? callEcoGet(`/api/v1/leaderboard/domains/${encodeURIComponent(domain)}?limit=${limit}`)
    : callEcoGet(`/api/v1/leaderboard/top?limit=${limit}&min_score=${min_score}`));
server.tool('aishield_leaderboard_snapshot', `获取 4 维度 leaderboard 完整快照 (score/domain/provider/badge)。

一次调用返回所有维度的完整数据，便于生态活跃度全景展示与报告生成。`, {
    limit: zod_1.z.number().min(1).max(100).default(50).describe('每维度返回条数'),
}, ({ limit }) => callEcoGet(`/api/v1/leaderboard/snapshot?limit=${limit}`));
server.tool('aishield_contributors_leaderboard', `查询 contributor 排行榜 (4 级激励体系)。

按累计贡献分排序，返回 Contributor / Reviewer / Maintainer / Trustee 四级贡献者
及其分数、徽章、事件分布。`, {
    limit: zod_1.z.number().min(1).max(100).default(20).describe('返回条数'),
}, ({ limit }) => callEcoGet(`/api/v1/contributors/leaderboard?limit=${limit}`));
server.tool('aishield_contributor_add_event', `给 contributor 追加一条贡献事件，累加积分。

支持的 6 类事件：review (审核)、rule_patch (规则补丁)、bug_report (漏洞报告)、
attestation (签发凭证)、doc (文档贡献)、ship_gate (发布门禁通过)。

不同事件有不同权重，累计到一定分即可升级 contributor 等级。`, {
    contributor_id: zod_1.z.string().describe('贡献者 ID'),
    event_type: zod_1.z.enum(['review', 'rule_patch', 'bug_report', 'attestation', 'doc', 'ship_gate']).describe('事件类型'),
    target_ref: zod_1.z.string().describe('事件作用对象 (rule_id / agent_id / PR URL 等)'),
    score: zod_1.z.number().min(0).max(100).default(10).describe('事件基础分'),
    metadata: zod_1.z.record(zod_1.z.any()).optional().describe('附加元数据'),
}, ({ contributor_id, event_type, target_ref, score, metadata }) => callEco(`/api/v1/contributors/${encodeURIComponent(contributor_id)}/events`, { event_type, target_ref, score, metadata }));
server.tool('aishield_sandbox_backend_matrix', `获取 sandbox backend 完整能力矩阵 (5 后端 × 全部能力维度)。

比 sandbox_evaluate 更详细：返回每个 backend 的操作系统兼容性、资源限制支持、
seccomp / landlock / namespaces 支持、网络隔离能力、性能评级等完整字段。`, {}, () => callEcoGet('/api/v1/sandbox/backend/matrix'));
server.tool('aishield_evidence_create_proposal', `创建 Evidence Bundle 提案 (Proposal-Bound Approval)。

等价于 evidence_proposal 的规范别名，对齐 CyberGuard v0.13.0 的提案流程。`, {
    run_id: zod_1.z.string().describe('Bundle run_id'),
    agent_id: zod_1.z.string().default('planner').describe('提案 agent'),
    action: zod_1.z.string().describe('建议动作'),
    target: zod_1.z.record(zod_1.z.any()).default({}).describe('作用目标'),
    parameters: zod_1.z.record(zod_1.z.any()).default({}).describe('动作参数'),
    rationale: zod_1.z.string().describe('提案理由'),
}, ({ run_id, agent_id, action, target, parameters, rationale }) => callEco(`/api/v1/evidence/${encodeURIComponent(run_id)}/proposals`, { agent_id, action, target, parameters, rationale }));
server.tool('aishield_evidence_approve_proposal', `批准 Evidence Bundle 提案 (Proposal-Bound Approval)。

等价于 evidence_approve 的规范别名。批准记录通过 proposal_hash 与提案双向绑定。`, {
    run_id: zod_1.z.string().describe('Bundle run_id'),
    proposal_id: zod_1.z.string().describe('提案 ID'),
    approver_id: zod_1.z.string().default('unknown').describe('批准者'),
    scope: zod_1.z.enum(['task', 'session', 'global']).default('task').describe('批准作用域'),
    expires_in: zod_1.z.number().min(60).max(86400).default(3600).describe('有效期（秒）'),
}, ({ run_id, proposal_id, approver_id, scope, expires_in }) => callEco(`/api/v1/evidence/${encodeURIComponent(run_id)}/proposals/${encodeURIComponent(proposal_id)}/approve`, { approver_id, scope, expires_in }));
server.tool('aishield_evidence_verify', `验证 Evidence Bundle 的 HMAC 链完整性 (bundle 视角)。

不同于 verify_evidence_bundle（接收 payload JSON 做离线验证），本工具直接查询
服务端已存储的 bundle，返回当前 verify 状态与摘要链完整性报告。`, {
    run_id: zod_1.z.string().describe('Bundle run_id'),
}, ({ run_id }) => callEcoGet(`/api/v1/evidence/${encodeURIComponent(run_id)}/verify`));
server.tool('aishield_evidence_verify_payload', `离线验证 Evidence Bundle payload (跨组织传递后校验)。

等价于 verify_evidence_bundle 的规范别名，对齐 CyberGuard 的 dual-round independent
testing：即使脱离原组织环境也能通过 secret 一致重放完整验证。`, {
    bundle: zod_1.z.record(zod_1.z.any()).describe('Bundle payload JSON'),
    hmac_secret: zod_1.z.string().optional().describe('HMAC 密钥'),
}, ({ bundle, hmac_secret }) => callEco('/api/v1/evidence/verify-payload', { bundle, hmac_secret }));
// ══════════════════════════════════════════════════════════════
// Personal Agent Governance Tools (v4.8.0, 2026-09-24)
// 面向个人 Agent（Meta Muse / ChatGPT-Agent / Claude-Agent / 自建 agent）
// 提供消费级身份 + 预算守护 + 行动溯源 + Connector 独立审核。
// 与 Enterprise 侧的 Agent Card / KYA / Evidence Bundle 分工。
// ══════════════════════════════════════════════════════════════
server.tool('aishield_personal_did_create', `创建或查询个人 Agent 身份 (PAI DID)。

一个自然人可以有多个个人 Agent 实例（Alice 的 Muse / Alice 的 ChatGPT-Agent）。
DID 遵循 did:aishield:pa:<hash> 命名约定，服务端为每次身份创建分配唯一标识，
后续可用于签署 Capability Ticket、追溯 Agent 行动、发起 Dispute。`, {
    user_id: zod_1.z.string().describe('自然人标识（如 email 或平台用户 id）'),
    display_name: zod_1.z.string().optional().describe('显示名'),
    email: zod_1.z.string().optional().describe('email'),
}, ({ user_id, display_name, email }) => callEco('/api/v1/personal-agents/users', { user_id, display_name, email }));
server.tool('aishield_personal_instance_register', `在个人 DID 下登记一个 Agent 实例（如 Alice 的 Muse on iOS）。

每个实例独立追踪，可独立吊销。当用户想停用某个 Agent 时，吊销它对应的实例
即可让后续所有 Capability Ticket 失效。

v4.8.1+ 支持 platform 结构化字段（对齐 eco/platform_registry，40+ 平台）：
  - 传入 platform="meta-muse" 会自动附带平台治理缺口
  - 传入 platform 但未知时，platform_known=false，不影响实例创建
  - platform_hint 保留旧字段做向后兼容`, {
    user_id: zod_1.z.string().describe('自然人标识'),
    agent_name: zod_1.z.string().describe('Agent 名称，如 Muse / ChatGPT-Agent'),
    provider: zod_1.z.string().describe('提供方，如 Meta / OpenAI / Anthropic / self-built'),
    platform: zod_1.z.union([zod_1.z.string(), zod_1.z.record(zod_1.z.any())]).optional().describe('平台标识，如 "meta-muse" / "xai-grok-bot" / "bytedance-coze"（可选）'),
    platform_tier: zod_1.z.string().optional().describe('平台订阅等级，如 free / super_grok_heavy / plus'),
    platform_hint: zod_1.z.string().optional().describe('向后兼容字段'),
    capabilities: zod_1.z.array(zod_1.z.string()).optional().describe('Agent 声明的能力'),
}, ({ user_id, agent_name, provider, platform, platform_tier, platform_hint, capabilities }) => callEco(`/api/v1/personal-agents/users/${encodeURIComponent(user_id)}/agent-instances`, { agent_name, provider, platform, platform_tier, platform_hint, capabilities }));
server.tool('aishield_personal_ticket_create', `为用户下的某个 Agent 实例签发 Capability Ticket（授权票据）。

Ticket 是"用户对某 Agent 的一次授权"，带 scope（金额上限 / 域名白名单 /
类别白名单）+ TTL。Ticket 由服务端 HMAC 签名，可被任何 verifier 独立验证。
建议所有个人 Agent 在执行敏感操作前先向用户申请一张 Ticket。`, {
    user_id: zod_1.z.string().describe('自然人标识'),
    instance_id: zod_1.z.string().describe('Agent 实例 id'),
    actions: zod_1.z.array(zod_1.z.string()).min(1).describe('授权的动作白名单，如 ["purchase"]'),
    scope: zod_1.z.record(zod_1.z.any()).optional().describe('边界：{max_amount, to_domain, allowed_categories}'),
    expires_in: zod_1.z.number().int().positive().max(86400).default(3600)
        .describe('TTL 秒数，最长 24h'),
    reason: zod_1.z.string().optional().describe('授权原因'),
}, ({ user_id, instance_id, actions, scope, expires_in, reason }) => callEco(`/api/v1/personal-agents/users/${encodeURIComponent(user_id)}/tickets`, { instance_id, actions, scope, expires_in, reason }));
server.tool('aishield_personal_budget_check', `对个人 Agent 的敏感操作做预算 + 风险 pre-flight 检查。

返回 verdict：
  - allow   : 预算内 & 风险 < 40 → 直接放行
  - confirm : 预算内 & 风险 40-70 → 用户二次确认（quote-first）
  - block   : 预算内 & 风险 >= 70 → 建议阻止
  - denied  : 预算超限（不可覆盖）

风险因素：金额超历史 P90 / 目标域名高危 / 深夜 / 币种漂移 / 首次目标 /
高危 action 类型。`, {
    user_id: zod_1.z.string().describe('自然人标识'),
    action: zod_1.z.string().describe('动作类型，如 purchase / send_email / wire_transfer'),
    amount: zod_1.z.number().positive().describe('金额'),
    currency: zod_1.z.string().default('CNY').describe('币种 CNY / USD'),
    target_url: zod_1.z.string().optional().describe('目标 URL'),
    category: zod_1.z.string().optional().describe('类别，如 groceries / utilities'),
}, ({ user_id, action, amount, currency, target_url, category }) => callEco('/api/v1/personal-agents/budget/check', { user_id, action, amount, currency, target_url, category }));
server.tool('aishield_personal_budget_reserve', `预留一笔个人预算（下单前先冻结）。

下单前调用，冻结额度并返回 reservation_id。下单成功后调用
aishield_personal_budget_commit 落账；下单失败调用 release。`, {
    user_id: zod_1.z.string().describe('自然人标识'),
    order_id: zod_1.z.string().describe('订单 id（用于幂等）'),
    amount: zod_1.z.number().positive().describe('金额'),
    currency: zod_1.z.string().default('CNY').describe('币种'),
    target: zod_1.z.string().optional().describe('目标（域名或 URL）'),
    note: zod_1.z.string().optional().describe('备注'),
}, ({ user_id, order_id, amount, currency, target, note }) => callEco('/api/v1/personal-agents/budget/reserve', { user_id, order_id, amount, currency, target, note }));
server.tool('aishield_personal_action_record', `将个人 Agent 的一次行动追加到用户的 HMAC 链。

所有敏感操作（购买 / 发邮件 / 授权 connector）都应调用本工具留痕，
形成不可篡改的行动 provenance 链。用户可在 90 天内离线验证链完整性，
并对任一 action 发起 dispute。`, {
    user_id: zod_1.z.string().describe('自然人标识'),
    action: zod_1.z.string().describe('动作类型'),
    payload: zod_1.z.record(zod_1.z.any()).optional().describe('动作负载'),
    instance_id: zod_1.z.string().optional().describe('Agent 实例 id'),
    ticket_id: zod_1.z.string().optional().describe('使用的授权 Ticket'),
    verdict: zod_1.z.string().default('allow').describe('check 结果'),
    actor_did: zod_1.z.string().optional().describe('Agent 自签名 DID'),
    note: zod_1.z.string().optional().describe('备注'),
}, ({ user_id, action, payload, instance_id, ticket_id, verdict, actor_did, note }) => callEco(`/api/v1/personal-agents/users/${encodeURIComponent(user_id)}/actions`, { action, payload, instance_id, ticket_id, verdict, actor_did, note }));
server.tool('aishield_personal_dispute_file', `用户对某条行动记录提出 dispute（"这个操作我不知情"）。

dispute 会生成可追溯的 case，包含被质疑的 action hash + 用户 reason。
可用于向 Agent 提供方或支付通道发起正式申诉，也可离线复核。`, {
    user_id: zod_1.z.string().describe('自然人标识'),
    seq: zod_1.z.number().int().positive().describe('action 链上的 seq'),
    reason: zod_1.z.string().describe('争议原因'),
    description: zod_1.z.string().optional().describe('详细描述'),
}, ({ user_id, seq, reason, description }) => callEco(`/api/v1/personal-agents/users/${encodeURIComponent(user_id)}/disputes`, { seq, reason, description }));
server.tool('aishield_personal_connector_vet', `对一个 Connector manifest 做独立安全评估（Meta 官方审核之外的第二意见）。

返回 verdict（pass / pass_with_warnings / needs_review / reject）+ 0-100 分数
+ findings 明细。扫描范围：危险 scope、piped shell 供应链（curl 管道 sh）、
明文 token、签名/过期声明、支付 quote-first、权限-描述一致性。`, {
    user_id: zod_1.z.string().describe('发起审核的用户标识'),
    connector: zod_1.z.record(zod_1.z.any()).describe('Connector manifest：{name, publisher, url, capabilities, scopes, install_commands, signature, expires_at, requires_payments}'),
}, ({ user_id, connector }) => callEco(`/api/v1/personal-agents/users/${encodeURIComponent(user_id)}/connectors/vet`, { connector }));
// ══════════════════════════════════════════════════════════════
// Platform Registry Tools (v4.8.1, 2026-09-24)
// 平台中立接入层：40+ 主流个人 Agent 平台的接入矩阵
// 帮助使用者选择接入平台、了解治理缺口、注册新平台
// ══════════════════════════════════════════════════════════════
server.tool('aishield_platform_catalog', `列出 AIShield 支持的个人 Agent 平台目录（40+ 平台，覆盖海外 + 大陆）。

包含 Meta Muse / Grok Bot / ChatGPT Agent / OpenAI Operator / Claude /
Gemini / 字节 Coze / 豆包 / 元宝 / 文心 / 通义 / Kimi / DeepSeek / GLM 等。

支持按 family（consumer/developer/enterprise/infrastructure）、
cny_accessible（reachable/verified_blocked/regional_only）、
access_path（mcp/openai_compat/connector_official/native_sdk/browser_agent）过滤。`, {
    family: zod_1.z.enum(['consumer', 'developer', 'enterprise', 'infrastructure']).optional()
        .describe('平台家族过滤'),
    cny_accessible: zod_1.z.enum(['reachable', 'verified_blocked', 'regional_only']).optional()
        .describe('大陆可达性过滤（大陆用户重点看 reachable）'),
    access_path: zod_1.z.enum(['mcp', 'openai_compat', 'connector_official', 'native_sdk', 'browser_agent']).optional()
        .describe('按接入路径过滤（推荐 mcp）'),
    include_gaps: zod_1.z.boolean().optional().describe('是否返回治理缺口详情（默认 false）'),
}, ({ family, cny_accessible, access_path, include_gaps }) => {
    const params = new URLSearchParams();
    if (family)
        params.set('family', family);
    if (cny_accessible)
        params.set('cny_accessible', cny_accessible);
    if (access_path)
        params.set('access_path', access_path);
    if (include_gaps)
        params.set('include_gaps', '1');
    return callEcoGet(`/api/v1/platforms?${params.toString()}`);
});
server.tool('aishield_platform_recommend', `根据用户场景推荐接入平台（大陆优先，MCP 优先）。

典型场景：
  - 大陆用户 + 需要个人身份 → 推荐 bytedance-coze（唯一有 MCP 的国内平台）
  - 海外用户 + 消费级 → 推荐 meta-muse / xai-grok-bot / openai-chatgpt-agent
  - 开发者 + OpenAI 兼容 → 推荐 deepseek / moonshot-kimi / zhipu-glm 等

返回 top 10 推荐，每个带 score + 推荐理由。`, {
    user_country: zod_1.z.string().default('CN').describe('用户所在国家/地区，CN 时会过滤掉大陆不通的平台'),
    capabilities_needed: zod_1.z.array(zod_1.z.string()).optional().describe('需要的治理能力，如 ["portable_personal_identity", "cumulative_budget_governance"]'),
    budget: zod_1.z.enum(['free', 'paid']).optional().describe('预算偏好'),
    developer_level: zod_1.z.enum(['beginner', 'intermediate', 'expert']).optional()
        .describe('开发者水平（intermediate+ 时优先 developer family）'),
    prefer_mcp: zod_1.z.boolean().optional().describe('优先 MCP 通道（默认 true）'),
}, ({ user_country, capabilities_needed, budget, developer_level, prefer_mcp }) => callEco('/api/v1/platforms/recommend', {
    user_country, capabilities_needed, budget, developer_level, prefer_mcp,
}));
server.tool('aishield_platform_detail', `查询单个平台的详细信息，包含内置治理能力、缺失的治理项、以及 AIShield 补齐映射。

例：
  - xai-grok-bot：xAI Grok Bot，SuperGrok 订阅，缺 portable_personal_identity 等
  - bytedance-coze：字节 Coze，大陆可达，唯一有 MCP 支持
  - meta-muse：Meta Muse，官方 connector 平台开放`, {
    platform_id: zod_1.z.string().describe('平台 ID，如 meta-muse / xai-grok-bot / bytedance-coze'),
}, ({ platform_id }) => callEcoGet(`/api/v1/platforms/${encodeURIComponent(platform_id)}`));
server.tool('aishield_platform_gap_matrix', `返回平台治理缺口矩阵：每个平台内置了什么治理、缺什么、AIShield 用什么补。

用于平台选型决策："我要选哪个平台，然后 AIShield 帮我补哪些缺口。"`
    + ``, {}, () => callEcoGet('/api/v1/platforms/gap-matrix'));
// ══════════════════════════════════════════════════════════════
// Connectors Tools (v4.8.2, 2026-09-24)
// 海外平台真实接入：Meta Muse + xAI Grok Bot
// 治理层前置（预算 + 敏感词 + 行动溯源）；OAuth/PAT 双通道
// 大陆需 HTTPS_PROXY；mock 模式通过服务端 AISHIELD_*_SECRET_KEY 配置
// ══════════════════════════════════════════════════════════════
server.tool('aishield_connector_catalog', `列出 AIShield 已实现接入的个人 Agent / 开发者平台。

当前支持：
  - meta-muse       Meta Muse（海外，muse.ai，OAuth，需代理）
  - xai-grok-bot    xAI Grok Bot（海外，api.x.ai，OpenAI 兼容，OAuth + PAT）
  - nvidia-dev      NVIDIA 开发者平台（NGC Catalog + NIM 推理 + NeMo 编排，NGC API Key）

每个平台都有 preflight 敏感词升级、4-tier 预算 verdict、HMAC 行动链；
meta-muse / xai-grok-bot 走 OAuth+PAT 双通道，nvidia-dev 走 NGC API Key。`, {}, () => callEcoGet('/api/v1/connectors'));
server.tool('aishield_connector_self_check', `诊断指定平台的接入状态：可达性、密钥配置、存储状态。

大陆环境需要 HTTPS_PROXY 环境变量；返回的 checks 会包含当前 proxy 摘要。`, {
    platform: zod_1.z.enum(['meta-muse', 'xai-grok-bot', 'nvidia-dev']).describe('平台 ID'),
}, ({ platform }) => callEcoGet(`/api/v1/connectors/${encodeURIComponent(platform)}/self-check`));
server.tool('aishield_connector_authorize', `生成 OAuth 授权 URL（用户浏览器打开完成授权；回跳 ?code=...&state=...）。

典型流程：
  1. 调用本工具拿 authorize_url + state
  2. 用户在浏览器打开授权 URL → 平台 → 回跳 redirect_uri?code=...
  3. 调用 aishield_connector_exchange_code 换 token
  4. 调用 aishield_connector_register_agent 注册 agent

需要预配置 client_secret（服务端 AISHIELD_MUSE_SECRET_KEY 或 AISHIELD_GROK_SECRET_KEY）。`, {
    platform: zod_1.z.enum(['meta-muse', 'xai-grok-bot']).describe('平台 ID'),
    client_id: zod_1.z.string().describe('OAuth 应用 client_id（用户在平台官方处创建）'),
    redirect_uri: zod_1.z.string().optional().describe('OAuth 回调地址（需在平台登记）'),
    scopes: zod_1.z.array(zod_1.z.string()).optional().describe('权限范围；省略时使用平台默认'),
}, ({ platform, client_id, redirect_uri, scopes }) => callEco(`/api/v1/connectors/${encodeURIComponent(platform)}/oauth/authorize`, { client_id, redirect_uri, scopes }));
server.tool('aishield_connector_exchange_code', `OAuth 授权码换 access_token + refresh_token。`, {
    platform: zod_1.z.enum(['meta-muse', 'xai-grok-bot']).describe('平台 ID'),
    code: zod_1.z.string().describe('回调拿到的授权码'),
    client_id: zod_1.z.string().describe('OAuth client_id'),
    redirect_uri: zod_1.z.string().optional(),
}, ({ platform, code, client_id, redirect_uri }) => callEco(`/api/v1/connectors/${encodeURIComponent(platform)}/oauth/token`, { code, client_id, redirect_uri }));
server.tool('aishield_connector_register_agent', `把个人 Agent 登记为 PAI 实例（跨平台可携带身份）。

meta-muse / xai-grok-bot:
  auth="pat" 时传 credentials: {"pat": "***"}（Grok Bot 官方推荐）。
  auth="oauth" 或省略时可通过 tokens 参数直接传 access_token。
  传 platform_agent_id 表示平台侧 agent ID。

nvidia-dev:
  鉴权形态是 NGC API Key，不是 OAuth。传 agent_instance_id + api_key。
  不要传 platform_agent_id / credentials。

PAI DID 由 personal_agent 层自动生成，同一 user_id 在多个平台的 agent
共享同一 parent_did。`, {
    platform: zod_1.z.enum(['meta-muse', 'xai-grok-bot', 'nvidia-dev']).describe('平台 ID'),
    user_id: zod_1.z.string().describe('AIShield 用户 ID（自然人）'),
    agent_name: zod_1.z.string().describe('Agent 名称，如 "Alice 的 Muse 助理"'),
    platform_agent_id: zod_1.z.string().optional().describe('平台侧 agent ID（Muse / Grok Bot）'),
    agent_instance_id: zod_1.z.string().optional().describe('PAI agent instance_id（nvidia-dev 必填）'),
    api_key: zod_1.z.string().optional().describe('NGC API Key（nvidia-dev 可选，也可稍后单独设置）'),
    client_id: zod_1.z.string().optional().describe('OAuth client_id（可选）'),
    auth: zod_1.z.enum(['pat', 'oauth']).optional().default('oauth').describe('认证方式'),
    credentials: zod_1.z.object({
        pat: zod_1.z.string().optional().describe('Grok Bot PAT（auth=pat 时必填）'),
        access_token: zod_1.z.string().optional(),
        refresh_token: zod_1.z.string().optional(),
        expires_at: zod_1.z.number().optional(),
        refresh_expires_at: zod_1.z.number().optional(),
        scope: zod_1.z.string().optional(),
    }).optional(),
    capabilities: zod_1.z.array(zod_1.z.string()).optional(),
    platform_tier: zod_1.z.string().optional(),
}, ({ platform, ...body }) => callEco(`/api/v1/connectors/${encodeURIComponent(platform)}/agents/register`, body));
server.tool('aishield_connector_run', `在指定平台的 Agent 上执行动作（chat / run_task / tool_call 等）。

治理层已内置：
  - preflight 预算 + 8 因素风险 + 敏感词升级
  - 4-tier verdict：allow / confirm / block / denied
    · denied: 硬拒，override 无效
    · block:  需 override=true 强制放行（如"帮我转账"）
    · confirm: 需 override=true 二次确认
    · allow:  直接放行
  - HMAC 行动链记录（90 天离线可验证）
  - 支付类金额自动 reserve + commit

nvidia-dev 的 action 取值：nim_chat（NIM 推理）/ ngc_catalog（NGC 模型检索）/ nemo_job（NeMo 训练编排）。`, {
    platform: zod_1.z.enum(['meta-muse', 'xai-grok-bot', 'nvidia-dev']).describe('平台 ID'),
    agent_instance_id: zod_1.z.string().describe('已注册的 PAI agent instance_id'),
    user_id: zod_1.z.string().describe('AIShield 用户 ID'),
    prompt: zod_1.z.string().describe('发送给 Agent 的内容/指令'),
    action: zod_1.z.enum(['chat', 'chat_completions', 'run_task', 'tool_call', 'get_agent', 'get_state', 'nim_chat', 'ngc_catalog', 'nemo_job']).default('chat'),
    bot_id: zod_1.z.string().optional().describe('平台侧 agent ID（可选，默认 agent_instance_id）'),
    model: zod_1.z.string().optional().describe('模型名（Grok 如 "grok-3"；NVIDIA 如 "meta/llama-3.1-8b-instruct"）'),
    currency: zod_1.z.enum(['CNY', 'USD']).optional().default('CNY').describe('币种，Grok / NVIDIA 默认 USD'),
    amount: zod_1.z.number().optional().describe('本次预估金额；缺省时从 prompt 提取'),
    override: zod_1.z.boolean().optional().default(false).describe('true 时强制 block/confirm'),
}, ({ platform, ...body }) => callEco(`/api/v1/connectors/${encodeURIComponent(platform)}/actions/run`, body));
// ══════════════════════════════════════════════════════════════
// Agent Infra Scan Tools (v4.8.3, 2026-09-25)
// Agent 基础设施开源生态扫描管道：扫描 → 封装 → 二次研发清单
// 目标类：laya / nasiko / agent-desktop / nvidia-dev 等 infrastructure|developer 平台
// 输入三态：repo_url（在线，走 api.github.com）/ local_path / files（内存，离线）
// ══════════════════════════════════════════════════════════════
server.tool('aishield_agent_infra_targets', `列出 AIShield 平台注册表中所有 agent 基础设施 / 开发者平台类目标
（family = infrastructure | developer），供开源扫描管道选靶。

包含 nvidia-dev、laya、nasiko、agent-desktop 等；
每个目标带 access_paths / cny_accessible / governance 缺口信息。

用于回答："有哪些 agent 基础设施开源项目值得扫描 + 封装成 MCP 适配器？"`, {}, () => callEcoGet('/api/v1/agent-infra/targets'));
server.tool('aishield_agent_infra_scan', `扫描一个 agent 基础设施开源项目，产出三层交付物：

  1. report          安全扫描结果（复用 AIShield scanner：findings / 评分 / 建议）
  2. mcp_adapter_skeleton  自动生成 MCP 封装适配器骨架（Python 代码，含治理 preflight 接入点）
  3. secondary_rd_checklist 二次研发清单（按风险类别派生的工作项）

输入三态（三选一）：
  - repo_url   GitHub 仓库 URL（在线；本环境走 api.github.com）
  - local_path 本地目录路径（离线）
  - files      内存文件字典 {"path": "content"}（完全离线、确定性，用于测试）

返回 ok=true 时含 report / mcp_adapter_skeleton / secondary_rd_checklist。`, {
    name: zod_1.z.string().describe('目标名称，如 "laya"'),
    repo_url: zod_1.z.string().optional().describe('GitHub 仓库 URL（在线扫描）'),
    local_path: zod_1.z.string().optional().describe('本地目录路径（离线扫描）'),
    files: zod_1.z.record(zod_1.z.string()).optional().describe('内存文件字典 {"path":"content"}（离线、确定性）'),
    platform_id: zod_1.z.string().optional().describe('关联的 AIShield 平台 ID（如 "laya" / "nasiko"）'),
    tool_type: zod_1.z.string().optional().default('mcp').describe('工具类型，默认 "mcp"'),
}, ({ name, repo_url, local_path, files, platform_id, tool_type }) => callEco('/api/v1/agent-infra/scan', { name, repo_url, local_path, files, platform_id, tool_type }));
// ══════════════════════════════════════════════════════════════
// Ecosystem Support Tools (v4.10.0, 2026-09-30)
// 战略转向：从"agent 安全扫描器"→"agent 生态支持体系基础设施"
// 5 硬骨头模块统一 API 入口：Agent Memory / Policy Pack / Red-team probe
//   / confidence 晋升 / rule decay。全部走 /api/v1/eco-support/*。
// ══════════════════════════════════════════════════════════════
server.tool('aishield_eco_support_summary', `AIShield Agent 生态支持体系能力总览 — 5 硬骨头模块 + 端点清单 + 阈值参数。

用于快速判断"这个需求该走哪个 API / MCP 工具"。`, {}, () => callEcoGet('/api/v1/eco-support/summary'));
server.tool('aishield_agent_memory_scan', `Agent Memory 深度扫描 — 覆盖 8 个主流 memory 框架（Hermes / Hindsight / Innate /
Letta / Mem0 / Zep / Memobase / Cognee）+ 4 类新品类攻击面：

  * framework_specific_api   框架 API 缺 version pin / scope / audit log 等约束
  * cross_session_accumulation  跨 session 累积污染（无 timestamp / 无 session 边界）
  * memory_recall_injection     检索结果直接拼进 system prompt
  * persistent_goal_injection   "从此刻起 / 永久 / always" 跨 session 语义

输入 files = {"path": "content"} 内存字典（离线、确定性、可复现）。
对齐 OWASP Agentic AI Top 10 ASI06 + MCP Top 10 MCP06。`, {
    files: zod_1.z.record(zod_1.z.string()).describe('{"path":"content"} 内存文件字典'),
    framework_focus: zod_1.z.string().optional().describe('仅返回某框架相关 finding，如 "hermes"'),
}, ({ files, framework_focus }) => callEco('/api/v1/eco-support/agent-memory-scan', { files, framework_focus }));
server.tool('aishield_list_policy_packs', `列出 AIShield 内置策略包（Policy Pack）及其六维策略配置。

5 内置：default（生产基线）/ strict（CI 阻断）/ mcp-only（MCP 类工具专项）/
personal-agent（个人 Agent 治理）/ red-team（探针自检，永不 fail）。

六维：severity_min / fail_on / excluded_categories / required_categories /
excluded_files / description。`, {}, () => callEcoGet('/api/v1/eco-support/policy-packs'));
server.tool('aishield_apply_policy_pack', `用 Policy Pack 过滤一份 AIShield 扫描报告并给出 CI pass/fail 判定。

输入：pack_name（默认 "default"）+ report 或 findings。
返回：过滤后 findings + pass 判定 + 六维策略应用明细。

对齐 Semgrep policy-as-code / agentshield 的六维策略语义。`, {
    pack_name: zod_1.z.string().optional().default('default').describe('策略包名，如 default / strict / red-team'),
    report: zod_1.z.record(zod_1.z.any()).optional().describe('AIShield 扫描报告对象'),
    findings: zod_1.z.array(zod_1.z.record(zod_1.z.any())).optional().describe('或只传 findings 数组（简写）'),
    overall_score: zod_1.z.number().optional().default(100),
}, ({ pack_name, report, findings, overall_score }) => callEco('/api/v1/eco-support/policy-apply', { pack_name, report, findings, overall_score }));
server.tool('aishield_red_team_probes', `AIShield Red-team 探针集（17 个）— 覆盖 OWASP MCP Top 10 (2025 v0.1) +
Agentic AI Top 10 (2025) 双维。

用于回归测试：给每条规则喂一个精心构造的攻击 payload，检查是否被命中。
返回每 probe 的 passed 判定 + 命中 rule_id 列表 + OWASP 类别。

include_failed=true 时返回未通过的 probe（默认隐藏，避免噪音）。`, {
    include_failed: zod_1.z.boolean().optional().default(false).describe('是否返回未通过的 probe（缺口清单）'),
    probe_ids: zod_1.z.array(zod_1.z.string()).optional().describe('仅运行指定 probe id，如 ["MCP01-1", "ASI04-2"]'),
}, ({ include_failed, probe_ids }) => callEco('/api/v1/eco-support/red-team-probe', { include_failed, probe_ids }));
server.tool('aishield_red_team_coverage', `AIShield Red-team 探针 OWASP 覆盖矩阵 — 按 MCP01-10 / ASI01-10 汇总 pass/fail 数。`, {}, () => callEcoGet('/api/v1/eco-support/red-team-probe/coverage'));
server.tool('aishield_confidence_promotion', `AIShield Confidence-based 规则晋升检查 — 对齐 instinct 项目三态累积机制。

阈值：SEED=1（种子）→ DRAFT=5（草稿）→ RULE=10+（正式规则）。
衰减：90 天未观察 → STALE / 180 天未观察 → DEAD（自动降级）。
红线：任何命中 BENIGN_CORPUS 的候选立即被标记 false_positive 阻断晋升。

enforce=true 时自动写回 radar_rules.json（生产用）；默认只读检查。`, {
    write_back: zod_1.z.boolean().optional().default(false).describe('是否把判定结果写回 radar_rules.json'),
    enforce: zod_1.z.boolean().optional().default(false).describe('enforce=true 时自动落晋升/降级决策'),
}, ({ write_back, enforce }) => callEco('/api/v1/eco-support/confidence-promotion', { write_back, enforce }));
server.tool('aishield_rule_decay', `AIShield 规则衰减状态报告 — 独立于 confidence 晋升的出口机制。

从 90 天滑动窗口历史快照计算 dormant/retire_suggested 集合。
dormant = 14 天窗口内 0 命中；retire_suggested = 30 天窗口内 ≤1 命中。

配合 POST /rule-decay/retire 执行实际退役（改 radar_rules.json）。`, {}, () => callEcoGet('/api/v1/eco-support/rule-decay'));
// ── Start ──
async function main() {
    const transport = new stdio_js_1.StdioServerTransport();
    await server.connect(transport);
    console.error(`AIShield MCP Server v${SERVER_VERSION} — OWASP MCP Top 10 aligned`);
    console.error(`  API: ${API_BASE}`);
    console.error(`  Key: ${API_KEY ? '***' + API_KEY.slice(-4) : '(not set — free tier)'}`);
}
main().catch((err) => {
    console.error('Fatal:', err);
    process.exit(1);
});
