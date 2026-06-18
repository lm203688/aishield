#!/usr/bin/env node
/**
 * AIShield Guardrail MCP Server
 * 
 * 杀手级产品：拦截Agent工具安装，自动触发安全扫描
 * 
 * Agent把它放在MCP列表第一个，它拦截所有tool_install请求，
 * 先调AIShield扫描，不安全的工具直接阻止安装。
 * 
 * 配置方式:
 * {
 *   "mcpServers": {
 *     "aishield-guardrail": {
 *       "command": "npx",
 *       "args": ["aishield-guardrail"]
 *     }
 *   }
 * }
 * 
 * 环境变量:
 *   AISHIELD_API_KEY  - API Key (可选，免费5次/天)
 *   AISHIELD_API_URL  - API URL (默认 https://aishield.ai)
 *   AISHIELD_MIN_SCORE - 最低安全分(默认60)
 *   AISHIELD_BLOCK_RISK - 阻止的风险等级(默认critical,high)
 */

const AIShIELD_API_URL = process.env.AISHIELD_API_URL || 'https://aishield.ai';
const API_KEY = process.env.AISHIELD_API_KEY || '';
const MIN_SCORE = parseInt(process.env.AISHIELD_MIN_SCORE || '60');
const BLOCK_RISK = (process.env.AISHIELD_BLOCK_RISK || 'critical,high').split(',');

// ========== Guardrail Tools ==========
const TOOLS = [
  {
    name: "guard_install",
    description: "🛡️ GUARDRAIL: Call this BEFORE installing any MCP server, AI skill, or agent tool. Scans the tool for security risks and returns pass/fail. If fail, DO NOT install the tool — warn the user about the risks.",
    inputSchema: {
      type: "object",
      properties: {
        source_url: { type: "string", description: "GitHub repo URL of the tool to install" },
        tool_type: { type: "string", enum: ["mcp", "skill", "gpt", "prompt"], description: "Type of tool (default: mcp)" },
        name: { type: "string", description: "Tool name (optional)" },
        auto_block: { type: "boolean", description: "If true (default), return block verdict for unsafe tools" }
      },
      required: ["source_url"]
    }
  },
  {
    name: "scan_before_use",
    description: "🛡️ GUARDRAIL: Call this BEFORE using a tool you haven't used before. Quick safety check. Returns pass/fail with score.",
    inputSchema: {
      type: "object",
      properties: {
        source_url: { type: "string", description: "Tool source URL" },
        name: { type: "string", description: "Tool name (optional)" }
      },
      required: ["source_url"]
    }
  },
  {
    name: "audit_config",
    description: "🛡️ GUARDRAIL: Audit your entire MCP/AI tool configuration. Pass your mcpServers config object and get a security report for all tools.",
    inputSchema: {
      type: "object",
      properties: {
        config: {
          type: "object",
          description: "Your mcpServers config object (from claude_desktop_config.json or similar)",
          additionalProperties: true
        }
      },
      required: ["config"]
    }
  },
  {
    name: "get_policy",
    description: "Get current AIShield guardrail policy (min score, blocked risk levels, etc.)",
    inputSchema: {
      type: "object",
      properties: {}
    }
  }
];

const SERVER_INFO = {
  name: "aishield-guardrail",
  version: "1.0.0",
  description: "AIShield Guardrail - Security gate for AI agent tool installation. Blocks unsafe MCP/skill installs."
};

function send(id, result) {
  process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id, result }) + '\n');
}

function sendError(id, code, message) {
  process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id, error: { code, message } }) + '\n');
}

// ========== API calls ==========
const https = require('https');
const http = require('http');

function apiCall(endpoint, body, method = 'POST') {
  return new Promise((resolve, reject) => {
    const url = new URL(AIShIELD_API_URL + endpoint);
    const lib = url.protocol === 'https:' ? https : http;
    const postData = body ? JSON.stringify(body) : null;
    const options = {
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname + url.search,
      method,
      headers: { 'Content-Type': 'application/json' },
      timeout: 120000
    };
    if (postData) options.headers['Content-Length'] = Buffer.byteLength(postData);
    if (API_KEY) options.headers['X-API-Key'] = API_KEY;
    
    const req = lib.request(options, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => { try { resolve(JSON.parse(data)); } catch { resolve({ error: 'parse error', raw: data.substring(0, 500) }); } });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    if (postData) req.write(postData);
    req.end();
  });
}

async function scanAndWait(sourceUrl, toolType, name) {
  const submit = await apiCall('/api/v1/audit', { tool_type: toolType || 'mcp', source_url: sourceUrl, name: name || '' });
  if (!submit.audit_id) throw new Error(submit.error || 'submit failed');
  
  for (let i = 0; i < 60; i++) {
    await new Promise(r => setTimeout(r, 3000));
    const result = await apiCall('/api/v1/audit/' + submit.audit_id, null, 'GET');
    if (result.status === 'completed') return { ...result.report, audit_id: submit.audit_id };
    if (result.status === 'failed') throw new Error('scan failed');
  }
  throw new Error('timeout');
}

// ========== Tool handlers ==========
async function handleGuardInstall(args) {
  const { source_url, tool_type = 'mcp', name = '', auto_block = true } = args;
  
  try {
    const report = await scanAndWait(source_url, tool_type, name);
    const score = report.overall_score || 0;
    const risk = report.risk_level || 'safe';
    const blocked = auto_block && (score < MIN_SCORE || BLOCK_RISK.includes(risk));
    
    const badge = { gold: '🥇', silver: '🥈', bronze: '🥉', none: '⚠️' };
    const riskIcon = { safe: '✅', medium: '🟡', high: '🟠', critical: '🔴' };
    
    let text = `🛡️ AIShield Guardrail — Install Gate\n\n`;
    text += `📦 Tool: ${report.name || name || source_url.split('/').pop()}\n`;
    text += `🔗 URL: ${source_url}\n`;
    text += `🏷️ Type: ${tool_type}\n\n`;
    text += `📊 Score: ${score}/100 | Risk: ${riskIcon[risk] || '✅'} ${risk}\n`;
    text += `${badge[report.badge_level] || '⚠️'} Badge: ${(report.badge_level || 'none').toUpperCase()}\n\n`;
    
    if (blocked) {
      text += `🚫 VERDICT: BLOCKED\n`;
      text += `   Score ${score} < ${MIN_SCORE} OR risk '${risk}' is in blocklist [${BLOCK_RISK.join(',')}]\n\n`;
      text += `⚠️ DO NOT INSTALL THIS TOOL. Security issues:\n`;
      const critical = (report.findings || []).filter(f => ['critical', 'high', 'medium'].includes(f.severity));
      critical.slice(0, 8).forEach(f => {
        text += `  • [${f.severity.toUpperCase()}] ${f.description}\n`;
        if (f.file) text += `    📄 ${f.file}:${f.lines || ''}\n`;
      });
      text += `\n💡 If you must install, review the full report first:\n`;
      text += `   ${AIShIELD_API_URL}/report/${report.audit_id}\n`;
      text += `\nTo override, set AISHIELD_MIN_SCORE=0 and AISHIELD_BLOCK_RISK=none`;
    } else {
      text += `✅ VERDICT: APPROVED\n`;
      text += `   Score ${score} ≥ ${MIN_SCORE} and risk '${risk}' is acceptable\n`;
      const issues = (report.findings || []).filter(f => ['critical', 'high'].includes(f.severity));
      if (issues.length) {
        text += `\n⚠️ Note: ${issues.length} issues found but below block threshold:\n`;
        issues.slice(0, 3).forEach(f => text += `  • [${f.severity.toUpperCase()}] ${f.description}\n`);
      }
      text += `\n📄 Full report: ${AIShIELD_API_URL}/report/${report.audit_id}\n`;
      text += `\n🏷️ Badge for your README:\n`;
      text += `   ![AIShield](${AIShIELD_API_URL}/api/v1/badge-name/${encodeURIComponent(report.name || name)})`;
    }
    
    return { content: [{ type: "text", text }] };
  } catch (e) {
    return { content: [{ type: "text", text: `🚫 AIShield Guardrail Error: ${e.message}\n\n⚠️ CAUTION: Could not verify tool safety. Do not install until AIShield is available.` }] };
  }
}

async function handleScanBeforeUse(args) {
  const { source_url, name = '' } = args;
  try {
    const report = await scanAndWait(source_url, 'mcp', name);
    const score = report.overall_score || 0;
    const risk = report.risk_level || 'safe';
    const safe = score >= MIN_SCORE && !BLOCK_RISK.includes(risk);
    
    let text = `🛡️ AIShield Pre-Use Check\n\n`;
    text += `📦 ${report.name || name}: ${score}/100 (${risk})\n`;
    text += safe ? `✅ Safe to use\n` : `⚠️ Caution: safety issues detected\n`;
    if (report.findings?.length) {
      text += `\nFindings: ${report.findings.length} total\n`;
    }
    return { content: [{ type: "text", text }] };
  } catch (e) {
    return { content: [{ type: "text", text: `⚠️ Check failed: ${e.message}` }] };
  }
}

async function handleAuditConfig(args) {
  const config = args.config || {};
  const servers = config.mcpServers || config;
  const entries = Object.entries(servers);
  
  if (!entries.length) {
    return { content: [{ type: "text", text: "❌ No MCP servers found in config" }] };
  }
  
  let text = `🛡️ AIShield Config Audit\n\nScanning ${entries.length} MCP servers...\n\n`;
  const results = [];
  
  for (const [name, conf] of entries) {
    // Try to extract GitHub URL from config
    const cmd = conf.command || '';
    const argsStr = (conf.args || []).join(' ');
    let githubUrl = '';
    
    // Common patterns: npx package-name → search npm→github
    const npxMatch = argsStr.match(/([a-z0-9-]+mcp[a-z0-9-]+)/i);
    if (npxMatch) {
      githubUrl = `https://github.com/search?q=${encodeURIComponent(npxMatch[1])}`;
    }
    
    if (conf.url) {
      // Remote MCP server
      results.push(`ℹ️ ${name}: remote server (${conf.url}) — skip static scan`);
      continue;
    }
    
    if (!githubUrl) {
      results.push(`⚠️ ${name}: no GitHub URL detected — manual review needed`);
      continue;
    }
    
    try {
      const report = await scanAndWait(githubUrl, 'mcp', name);
      const badge = { gold: '🥇', silver: '🥈', bronze: '🥉', none: '⚠️' };
      const score = report.overall_score || 0;
      const risk = report.risk_level || 'safe';
      const blocked = score < MIN_SCORE || BLOCK_RISK.includes(risk);
      results.push(`${blocked ? '🚫' : '✅'} ${badge[report.badge_level] || '⚠️'} ${name}: ${score}/100 (${risk})${blocked ? ' — BLOCKED' : ''}`);
    } catch (e) {
      results.push(`❌ ${name}: scan failed — ${e.message}`);
    }
  }
  
  text += results.join('\n');
  const blocked = results.filter(r => r.includes('BLOCKED')).length;
  if (blocked) {
    text += `\n\n🚫 ${blocked} tool(s) blocked by guardrail policy`;
  }
  return { content: [{ type: "text", text }] };
}

function handleGetPolicy() {
  const text = `🛡️ AIShield Guardrail Policy\n\n`;
  const lines = [
    `Minimum score: ${MIN_SCORE}/100`,
    `Blocked risk levels: ${BLOCK_RISK.join(', ')}`,
    `API URL: ${AIShIELD_API_URL}`,
    `API Key: ${API_KEY ? '✅ configured' : '❌ not set (free tier: 5 scans/day)'}`,
    ``,
    `Configure via environment variables:`,
    `  AISHIELD_MIN_SCORE=${MIN_SCORE}`,
    `  AISHIELD_BLOCK_RISK=${BLOCK_RISK.join(',')}`,
    `  AISHIELD_API_KEY=<your-key>`,
    `  AISHIELD_API_URL=${AIShIELD_API_URL}`,
  ];
  return { content: [{ type: "text", text: text + lines.join('\n') }] };
}

// ========== Main ==========
async function main() {
  let buf = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', async (chunk) => {
    buf += chunk;
    const lines = buf.split('\n');
    buf = lines.pop();
    
    for (const line of lines) {
      if (!line.trim()) continue;
      let req;
      try { req = JSON.parse(line); } catch { continue; }
      
      const method = req.method || '';
      const id = req.id;
      const params = req.params || {};
      
      if (method === 'initialize') {
        send(id, { protocolVersion: "2024-11-05", capabilities: { tools: {} }, serverInfo: SERVER_INFO });
      } else if (method === 'notifications/initialized') {
        // pass
      } else if (method === 'tools/list') {
        send(id, { tools: TOOLS });
      } else if (method === 'tools/call') {
        const toolName = params.name;
        const args = params.arguments || {};
        try {
          let result;
          if (toolName === 'guard_install') result = await handleGuardInstall(args);
          else if (toolName === 'scan_before_use') result = await handleScanBeforeUse(args);
          else if (toolName === 'audit_config') result = await handleAuditConfig(args);
          else if (toolName === 'get_policy') result = handleGetPolicy();
          else { sendError(id, -32601, `Unknown: ${toolName}`); continue; }
          send(id, result);
        } catch (e) {
          sendError(id, -32603, e.message);
        }
      } else if (method === 'ping') {
        send(id, {});
      } else if (id !== undefined) {
        sendError(id, -32601, `Unknown: ${method}`);
      }
    }
  });
  process.stdin.on('end', () => process.exit(0));
}

main().catch(e => { console.error(e); process.exit(1); });
