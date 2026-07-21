#!/usr/bin/env node

/**
 * AIShield MCP Server v3.0
 * 
 * OWASP MCP Top 10 aligned security scanner.
 * 6 tools: scan / guardrail / prompt_check / banned_words / rug_pull / handshake
 * 
 * Usage:
 *   npx @aishield/mcp-server
 * 
 * Env:
 *   AISHIELD_API_URL  — backend API URL (default: https://api.aishield.tools)
 *   AISHIELD_API_KEY  — optional API key for higher rate limits
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

const API_BASE = process.env.AISHIELD_API_URL || 'https://api.aishield.tools';
const API_KEY = process.env.AISHIELD_API_KEY || '';

// ── API Helper ──
async function apiCall(path: string, body: Record<string, unknown>, timeoutMs = 30000): Promise<any> {
  const url = `${API_BASE}${path}`;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'User-Agent': 'AIShield-MCP-Server/3.0',
  };
  if (API_KEY) headers['Authorization'] = `Bearer ${API_KEY}`;

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
  } finally {
    clearTimeout(timer);
  }
}

// ── Create Server ──
const server = new McpServer({
  name: 'AIShield Security Scanner',
  version: '3.0.0',
  description: 'OWASP MCP Top 10 aligned security scanner — 133 rules, 5-dimension scoring, tool poisoning & supply chain detection',
});

// ══════════════════════════════════════════════════════════════
// Tool 1: Full Security Scan
// ══════════════════════════════════════════════════════════════

server.tool(
  'aishield_scan',
  `AIShield安全扫描 — 扫描MCP Server/AI工具的安全风险。

对齐OWASP MCP Top 10 (2025 v0.1)，82+条规则覆盖10大风险类别。
5维评分: 安全(40%)/权限(20%)/数据处理(20%)/供应链(10%)/可靠性(10%)
返回: 评分 + 风险等级 + OWASP合规矩阵 + 修复建议`,
  {
    source_url: z.string().describe('GitHub repo URL of the tool to scan'),
    tool_type: z.enum(['mcp', 'skill', 'gpt', 'prompt']).default('mcp').describe('Tool type'),
    name: z.string().optional().describe('Tool name (optional)'),
  },
  async ({ source_url, tool_type, name }) => {
    try {
      const data = await apiCall('/api/v1/audit', { source_url, tool_type, name });
      return formatScanResult(data);
    } catch (e: any) {
      return { content: [{ type: 'text' as const, text: `AIShield scan failed: ${e.message}` }] };
    }
  }
);

// ══════════════════════════════════════════════════════════════
// Tool 2: Pre-install Guardrail
// ══════════════════════════════════════════════════════════════

server.tool(
  'aishield_guardrail',
  `AIShield安装前安全检查 — 在安装任何MCP/AI工具前调用此工具。

返回pass/block判定 + 评分 + OWASP合规矩阵。
建议在安装任何第三方MCP Server前自动调用此工具。`,
  {
    source_url: z.string().describe('GitHub repo URL of the tool to check'),
    auto_block: z.boolean().default(true).describe('If true, return block verdict for unsafe tools'),
  },
  async ({ source_url, auto_block }) => {
    try {
      const data = await apiCall('/api/v1/audit', { source_url, tool_type: 'mcp', auto_block });
      const score = data.overall_score || 0;
      const risk = data.risk_level || 'unknown';
      const badge = data.badge_level || 'none';

      let verdict: string;
      if (score >= 70) {
        verdict = '✅ PASS — Safe to install';
      } else if (score >= 55 && !auto_block) {
        verdict = '⚠️ WARN — Review recommended before installing';
      } else {
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
        ...(data.recommendations || []).map((r: string) => `  • ${r}`),
      ].join('\n');

      return { content: [{ type: 'text' as const, text: summary }] };
    } catch (e: any) {
      return { content: [{ type: 'text' as const, text: `Guardrail check failed: ${e.message}. CAUTION: Do not install until verified.` }] };
    }
  }
);

// ══════════════════════════════════════════════════════════════
// Tool 3: Prompt Injection Detection
// ══════════════════════════════════════════════════════════════

server.tool(
  'aishield_prompt_check',
  `Prompt安全检测 — 检测用户输入的Prompt是否存在注入/越狱/数据外传风险。

支持中文和英文，覆盖: 越狱指令/身份切换/系统提示窃取/数据外传/角色扮演注入/零宽字符/Unicode编码`,
  {
    prompt: z.string().min(10).describe('待检测的Prompt文本（至少10个字符）'),
  },
  async ({ prompt }) => {
    try {
      const data = await apiCall('/api/v1/prompt-check', { prompt });
      const safe = data.safe ? '✅ SAFE' : '❌ UNSAFE';
      const summary = [
        `Prompt安全检测结果: ${safe}`,
        `评分: ${data.score}/100 | 风险: ${data.risk || 'unknown'}`,
        ``,
        data.summary || '',
        ``,
        `发现的问题:`,
        ...(data.findings || []).map((f: any) => `  [${f.severity}] ${f.description}`),
      ].join('\n');
      return { content: [{ type: 'text' as const, text: summary }] };
    } catch (e: any) {
      return { content: [{ type: 'text' as const, text: `Prompt检测失败: ${e.message}` }] };
    }
  }
);

// ══════════════════════════════════════════════════════════════
// Tool 4: Chinese Banned Words Check
// ══════════════════════════════════════════════════════════════

server.tool(
  'aishield_banned_words',
  `中文违禁词检测 — 检测文本中的违禁词/敏感词。

覆盖6大平台: 微信/抖音/小红书/B站/知乎/微博
返回: 违禁词列表 + 法律条文 + 罚款金额 + 替换建议`,
  {
    text: z.string().describe('待检测文本'),
    platform: z.enum(['douyin', 'xiaohongshu', 'wechat', 'weibo', 'bilibili', 'kuaishou', 'all']).default('all').describe('目标平台'),
  },
  async ({ text, platform }) => {
    try {
      const data = await apiCall('/api/v1/banned-words', { text, platform });
      return { content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }] };
    } catch (e: any) {
      return { content: [{ type: 'text' as const, text: `违禁词检测失败: ${e.message}` }] };
    }
  }
);

// ══════════════════════════════════════════════════════════════
// Tool 5: Rug Pull Detection
// ══════════════════════════════════════════════════════════════

server.tool(
  'aishield_rug_pull',
  `Rug Pull检测 — 检查MCP工具是否在版本更新中移除安全代码或新增可疑网络请求。

对比最近commit diff，检测: 安全代码删除、新增网络请求、权限扩大、大量代码删除。
返回风险等级(critical/high/medium/low/safe)和具体发现。`,
  {
    source_url: z.string().describe('GitHub repo URL'),
  },
  async ({ source_url }) => {
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
          lines.push(`  [${f.severity}] ${f.description} ${f.commit_sha ? '('+f.commit_sha+')' : ''}`);
        }
      }
      return { content: [{ type: 'text' as const, text: lines.join('\n') }] };
    } catch (e: any) {
      return { content: [{ type: 'text' as const, text: `Rug pull check failed: ${e.message}` }] };
    }
  }
);

// ══════════════════════════════════════════════════════════════
// Tool 6: MCP Handshake Verification
// ══════════════════════════════════════════════════════════════

server.tool(
  'aishield_handshake',
  `MCP握手验证 — 分析MCP配置、检测npx自动安装风险、敏感环境变量、工具描述异常长度。

提取README/package.json中的MCP配置，分析: npx -y风险、敏感env变量、远程URL安全性、
工具描述长度（>500字符可能隐藏指令）。如果是HTTP类型MCP，尝试实际握手。`,
  {
    source_url: z.string().describe('GitHub repo URL'),
  },
  async ({ source_url }) => {
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
          lines.push(`  [${f.severity}] ${f.description}`);
        }
      }
      if (data.configs && data.configs.length > 0) {
        lines.push('', '── MCP Configs ──');
        for (const c of data.configs.slice(0, 3)) {
          lines.push(`  ${JSON.stringify(c).slice(0, 100)}`);
        }
      }
      return { content: [{ type: 'text' as const, text: lines.join('\n') }] };
    } catch (e: any) {
      return { content: [{ type: 'text' as const, text: `Handshake check failed: ${e.message}` }] };
    }
  }
);

// ── Helper ──
function formatScanResult(data: any) {
  const score = data.overall_score || 0;
  const badge = data.badge_level || 'none';
  const risk = data.risk_level || 'unknown';

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
    const important = (data.findings as any[]).filter(
      (f) => f.severity === 'critical' || f.severity === 'high'
    );
    for (const f of important.slice(0, 15)) {
      lines.push(`  [${f.severity.toUpperCase()}] ${f.description} (${f.file})`);
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

  return { content: [{ type: 'text' as const, text: lines.join('\n') }] };
}

// ── Start ──
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('AIShield MCP Server v3.0 — OWASP MCP Top 10 aligned');
  console.error(`  API: ${API_BASE}`);
  console.error(`  Key: ${API_KEY ? '***' + API_KEY.slice(-4) : '(not set — free tier)'}`);
}

main().catch((err) => {
  console.error('Fatal:', err);
  process.exit(1);
});