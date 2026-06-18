#!/usr/bin/env node
/**
 * AIShield MCP Server - npm package entry
 * 
 * Agent原生分发核心：`npx aishield-mcp` 一键启动
 * 支持两种模式：
 *   1. stdio本地模式（默认）：本地扫描，无需API
 *   2. remote远程模式：通过AIShield SaaS API扫描，免安装依赖
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// 远程MCP Server URL（默认公共服务，可自建）
const DEFAULT_API_URL = 'https://aishield.ai';
const REMOTE_MODE = process.env.AISHIELD_REMOTE === '1' || process.env.AISHIELD_API_URL;
const API_URL = process.env.AISHIELD_API_URL || DEFAULT_API_URL;
const API_KEY = process.env.AISHIELD_API_KEY || '';

// ========== MCP Protocol (stdio) ==========
const TOOLS = [
  {
    name: "scan_ai_tool",
    description: "Scan AI tools (MCP/GPT/Skill/Prompt) for security risks. Returns 4-dimensional scoring (security/privacy/quality/performance) and detailed findings. Supports GitHub repo URLs, GPT Store links, etc.",
    inputSchema: {
      type: "object",
      properties: {
        source_url: { type: "string", description: "Tool source URL (GitHub repo, GPT Store link, etc.)" },
        tool_type: { type: "string", enum: ["mcp", "skill", "gpt", "prompt"], description: "Tool type" },
        name: { type: "string", description: "Tool name (optional)" }
      },
      required: ["source_url", "tool_type"]
    }
  },
  {
    name: "get_security_badge",
    description: "Get AIShield security badge info (score, risk level, badge tier) for a tool. Use this to display security certification in README or docs.",
    inputSchema: {
      type: "object",
      properties: {
        source_url: { type: "string", description: "Tool source URL" },
        name: { type: "string", description: "Tool name (optional, either source_url or name)" }
      }
    }
  },
  {
    name: "batch_scan",
    description: "Batch scan multiple AI tools. Returns summary scores for each. Max 10 tools per call.",
    inputSchema: {
      type: "object",
      properties: {
        tools: {
          type: "array",
          items: {
            type: "object",
            properties: {
              source_url: { type: "string" },
              tool_type: { type: "string", enum: ["mcp", "skill", "gpt", "prompt"] },
              name: { type: "string" }
            },
            required: ["source_url", "tool_type"]
          },
          description: "Tools to scan (max 10)"
        }
      },
      required: ["tools"]
    }
  },
  {
    name: "check_tool_safety",
    description: "Quick safety check before installing an MCP tool. Returns pass/fail with score. Designed for guardrail use — call this before adding any MCP server to your config.",
    inputSchema: {
      type: "object",
      properties: {
        source_url: { type: "string", description: "GitHub repo URL of the MCP tool" },
        name: { type: "string", description: "Tool name (optional)" }
      },
      required: ["source_url"]
    }
  }
];

const SERVER_INFO = {
  name: "aishield",
  version: "2.1.0",
  description: "AIShield - AI Tool Security Scanner. Scan MCP/Skill/GPT/Prompt for security risks. OWASP-aligned 4-dimensional scoring with certified badges."
};

function send(id, result) {
  process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id, result }) + '\n');
}

function sendError(id, code, message) {
  process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id, error: { code, message } }) + '\n');
}

// ========== Remote API call ==========
async function callRemote(endpoint, body) {
  const https = require('https');
  const http = require('http');
  const url = new URL(API_URL + endpoint);
  const lib = url.protocol === 'https:' ? https : http;
  
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify(body);
    const options = {
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData),
      },
      timeout: 120000
    };
    if (API_KEY) options.headers['X-API-Key'] = API_KEY;
    
    const req = lib.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch { resolve({ error: 'Invalid response', raw: data.substring(0, 500) }); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Request timeout')); });
    req.write(postData);
    req.end();
  });
}

async function pollResult(auditId) {
  for (let i = 0; i < 60; i++) {
    await new Promise(r => setTimeout(r, 3000));
    const https = require('https');
    const http = require('http');
    const url = new URL(API_URL + '/api/v1/audit/' + auditId);
    const lib = url.protocol === 'https:' ? https : http;
    
    const result = await new Promise((resolve, reject) => {
      const options = { hostname: url.hostname, port: url.port || (url.protocol === 'https:' ? 443 : 80), path: url.pathname, method: 'GET', headers: {}, timeout: 10000 };
      if (API_KEY) options.headers['X-API-Key'] = API_KEY;
      const req = lib.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => { try { resolve(JSON.parse(data)); } catch { resolve({}); } });
      });
      req.on('error', reject);
      req.on('timeout', () => { req.destroy(); resolve({}); });
      req.end();
    });
    
    if (result.status === 'completed') return result;
    if (result.status === 'failed') throw new Error('Scan failed');
  }
  throw new Error('Polling timeout');
}

// ========== Tool handlers ==========
async function handleScan(args) {
  const { source_url, tool_type = 'mcp', name = '' } = args;
  if (!source_url) return { content: [{ type: "text", text: "❌ Error: source_url is required" }] };
  
  try {
    // Submit audit
    const submit = await callRemote('/api/v1/audit', { tool_type, source_url, name });
    if (submit.error || !submit.audit_id) {
      return { content: [{ type: "text", text: `❌ Submit failed: ${submit.error || submit.message || 'unknown'}` }] };
    }
    
    // Poll for result
    const result = await pollResult(submit.audit_id);
    const report = result.report || {};
    const badge = { gold: '🥇', silver: '🥈', bronze: '🥉', none: '⚠️' };
    const risk = { safe: '✅', medium: '🟡', high: '🟠', critical: '🔴' };
    
    let summary = `🛡️ AIShield Security Audit Report\n\n`;
    summary += `📦 Tool: ${report.name || name || source_url.split('/').pop()}\n`;
    summary += `🔗 URL: ${source_url}\n`;
    summary += `🏷️ Type: ${tool_type}\n\n`;
    summary += `📊 Scores:\n`;
    summary += `  Security: ${report.security_score || 0}/100\n`;
    summary += `  Privacy:  ${report.privacy_score || 0}/100\n`;
    summary += `  Quality:  ${report.quality_score || 0}/100\n`;
    summary += `  Performance: ${report.performance_score || 0}/100\n`;
    summary += `  ━━━━━━━━━━━━━\n`;
    summary += `  Overall:  ${report.overall_score || 0}/100\n\n`;
    summary += `${badge[report.badge_level] || '⚠️'} Badge: ${(report.badge_level || 'none').toUpperCase()}\n`;
    summary += `${risk[report.risk_level] || '✅'} Risk: ${report.risk_level || 'safe'}\n`;
    summary += `📝 Findings: ${report.findings?.length || 0}\n`;
    
    const critical = (report.findings || []).filter(f => ['critical', 'high'].includes(f.severity));
    if (critical.length) {
      summary += `\n🚨 Critical Risks:\n`;
      critical.slice(0, 5).forEach(f => {
        summary += `  • [${f.severity.toUpperCase()}] ${f.description} (${f.file || ''})\n`;
      });
    }
    
    if (report.recommendations?.length) {
      summary += `\n💡 Recommendations:\n`;
      report.recommendations.slice(0, 3).forEach(r => summary += `  ${r}\n`);
    }
    
    summary += `\n🏷️ Badge: ![AIShield](${API_URL}/api/v1/badge/${encodeURIComponent(source_url)})`;
    summary += `\n📄 Full report: ${API_URL}/report/${submit.audit_id}`;
    
    return { content: [{ type: "text", text: summary }] };
  } catch (e) {
    return { content: [{ type: "text", text: `❌ Scan error: ${e.message}` }] };
  }
}

async function handleBadge(args) {
  const { source_url = '', name = '' } = args;
  try {
    const endpoint = '/api/v1/badge-info' + (source_url ? `?url=${encodeURIComponent(source_url)}` : `?name=${encodeURIComponent(name)}`);
    const https = require('https');
    const http = require('http');
    const url = new URL(API_URL + endpoint);
    const lib = url.protocol === 'https:' ? https : http;
    
    const result = await new Promise((resolve, reject) => {
      const options = { hostname: url.hostname, port: url.port || (url.protocol === 'https:' ? 443 : 80), path: url.pathname + url.search, method: 'GET', headers: {}, timeout: 10000 };
      if (API_KEY) options.headers['X-API-Key'] = API_KEY;
      const req = lib.request(options, (res) => { let d=''; res.on('data', c => d+=c); res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve({}); } }); });
      req.on('error', reject); req.on('timeout', () => { req.destroy(); resolve({}); }); req.end();
    });
    
    if (!result.name) return { content: [{ type: "text", text: `❌ Not found. Scan the tool first using scan_ai_tool.` }] };
    
    const badge = { gold: '🥇', silver: '🥈', bronze: '🥉', none: '⚠️' };
    let text = `🏷️ AIShield Badge Info\n\n`;
    text += `📦 Tool: ${result.name}\n`;
    text += `${badge[result.badge_level] || '⚠️'} Badge: ${(result.badge_level || 'none').toUpperCase()}\n`;
    text += `📊 Score: ${result.overall_score || 0}/100\n`;
    text += `🔒 Risk: ${result.risk_level || 'safe'}\n`;
    text += `\nMarkdown: ![AIShield](${API_URL}/api/v1/badge-name/${encodeURIComponent(result.name)})`;
    return { content: [{ type: "text", text }] };
  } catch (e) {
    return { content: [{ type: "text", text: `❌ Error: ${e.message}` }] };
  }
}

async function handleBatch(args) {
  const tools = args.tools || [];
  if (!tools.length) return { content: [{ type: "text", text: "❌ No tools provided" }] };
  if (tools.length > 10) return { content: [{ type: "text", text: "❌ Max 10 tools per batch" }] };
  
  const results = [];
  for (const t of tools) {
    try {
      const submit = await callRemote('/api/v1/audit', t);
      if (!submit.audit_id) { results.push(`❌ ${t.name || t.source_url}: submit failed`); continue; }
      const result = await pollResult(submit.audit_id);
      const r = result.report || {};
      const badge = { gold: '🥇', silver: '🥈', bronze: '🥉', none: '⚠️' };
      results.push(`${badge[r.badge_level] || '⚠️'} ${r.name || t.name}: ${r.overall_score || 0}/100 (${r.risk_level || 'safe'})`);
    } catch (e) {
      results.push(`❌ ${t.name || t.source_url}: ${e.message}`);
    }
  }
  return { content: [{ type: "text", text: "🛡️ Batch Scan Results\n\n" + results.join('\n') }] };
}

async function handleQuickCheck(args) {
  const { source_url, name = '' } = args;
  try {
    const submit = await callRemote('/api/v1/audit', { tool_type: 'mcp', source_url, name });
    if (!submit.audit_id) return { content: [{ type: "text", text: `❌ Submit failed` }] };
    const result = await pollResult(submit.audit_id);
    const r = result.report || {};
    const score = r.overall_score || 0;
    const risk = r.risk_level || 'safe';
    const pass = score >= 60 && risk !== 'critical';
    
    let text = `${pass ? '✅ SAFE TO INSTALL' : '⚠️ CAUTION: Security issues found'}\n\n`;
    text += `📦 ${r.name || name}\n`;
    text += `📊 Score: ${score}/100 | Risk: ${risk}\n`;
    text += `🛡️ Badge: ${(r.badge_level || 'none').toUpperCase()}\n`;
    if (r.findings?.length) {
      const critical = r.findings.filter(f => ['critical', 'high'].includes(f.severity));
      if (critical.length) {
        text += `\n🚨 Issues:\n`;
        critical.slice(0, 3).forEach(f => text += `  • [${f.severity.toUpperCase()}] ${f.description}\n`);
      }
    }
    text += `\n📄 Report: ${API_URL}/report/${submit.audit_id}`;
    return { content: [{ type: "text", text }] };
  } catch (e) {
    return { content: [{ type: "text", text: `❌ Error: ${e.message}` }] };
  }
}

// ========== Main loop ==========
async function main() {
  let inputBuffer = '';
  
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', async (chunk) => {
    inputBuffer += chunk;
    const lines = inputBuffer.split('\n');
    inputBuffer = lines.pop();
    
    for (const line of lines) {
      if (!line.trim()) continue;
      let request;
      try { request = JSON.parse(line); }
      catch { continue; }
      
      const method = request.method || '';
      const id = request.id;
      const params = request.params || {};
      
      if (method === 'initialize') {
        send(id, { protocolVersion: "2024-11-05", capabilities: { tools: {} }, serverInfo: SERVER_INFO });
      } else if (method === 'notifications/initialized') {
        // no response
      } else if (method === 'tools/list') {
        send(id, { tools: TOOLS });
      } else if (method === 'tools/call') {
        const toolName = params.name || '';
        const args = params.arguments || {};
        try {
          let result;
          if (toolName === 'scan_ai_tool') result = await handleScan(args);
          else if (toolName === 'get_security_badge') result = await handleBadge(args);
          else if (toolName === 'batch_scan') result = await handleBatch(args);
          else if (toolName === 'check_tool_safety') result = await handleQuickCheck(args);
          else { sendError(id, -32601, `Unknown tool: ${toolName}`); continue; }
          send(id, result);
        } catch (e) {
          sendError(id, -32603, `Tool error: ${e.message}`);
        }
      } else if (method === 'ping') {
        send(id, {});
      } else if (id !== undefined) {
        sendError(id, -32601, `Unknown method: ${method}`);
      }
    }
  });
  
  process.stdin.on('end', () => process.exit(0));
}

main().catch(e => { console.error(e); process.exit(1); });
