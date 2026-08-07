# -*- coding: utf-8 -*-
"""
MCP Server 契约测试 — 锁定「npm 包能读到真实分数」这条链路

背景（真实缺陷，2026-08-07 发现，随 4.2.2 修复）:
  api/server.py 的 /api/v1/audit 响应形状是
      { success, score, badge_level, risk_level, report: { overall_score, findings, ... } }
  而 mcp-server/src/index.ts 读的是顶层 data.overall_score —— 该键在顶层不存在。

  后果不是报错，是**静默降级**:
    · aishield_scan     每次都显示 "Score: 0/100"，五维全 0，findings 为空
    · aishield_guardrail score 恒为 0 → 永远落进 BLOCK 分支，对再干净的仓库
                         也判"不要安装"

  这与 2026-08-05 的 CI 门禁事故同源: 消费方按想象中的形状取值，
  取不到就静默得 0，而"恒定输出的检查等价于没有检查"。

不变量:
  1. MCP server 读取的每个分数字段，都必须能从 API 的真实响应形状中取到
  2. 协议层自报的版本，必须与 npm 包版本一致（否则用户报障时对不上代码）

本文件含两层:
  · 静态契约（永远运行，不依赖 node / 网络）
  · stdio 端到端（node 或构建产物缺失时自动跳过）
"""

import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_TS = os.path.join(ROOT, 'mcp-server', 'src', 'index.ts')
PKG_JSON = os.path.join(ROOT, 'mcp-server', 'package.json')
DIST_JS = os.path.join(ROOT, 'mcp-server', 'dist', 'index.js')
SYNC_PY = os.path.join(ROOT, 'scripts', 'sync_version.py')
SERVER_PY = os.path.join(ROOT, 'api', 'server.py')


def _read(path):
    with open(path, 'r', encoding='utf-8-sig') as fh:
        return fh.read()


def _strip_comments(src):
    """
    剥掉 // 行注释与 /* */ 块注释再做静态检查。

    否则文档会误伤自己：解释「不要写 data.overall_score」的那句注释，
    本身就含有这个字符串。检查代码的东西不该被讲解代码的文字绊倒。
    """
    src = re.sub(r'/\*.*?\*/', '', src, flags=re.S)
    src = re.sub(r'(?m)^\s*//.*$', '', src)
    src = re.sub(r'(?m)\s//[^\n]*$', '', src)
    return src


# ══════════════════════════════════════════════════════════════
# 第一层：静态契约（无外部依赖，永远运行）
# ══════════════════════════════════════════════════════════════

class TestAuditShapeContract(unittest.TestCase):
    """MCP server 的取值方式必须匹配 API 的真实响应形状"""

    def setUp(self):
        self.ts = _read(INDEX_TS)

    def test_unwrap_helper_exists(self):
        """必须有显式的解包函数，而不是各处零散地猜结构"""
        self.assertIn('function unwrapAudit', self.ts,
                      'unwrapAudit 缺失 —— 消费方又在直接猜响应结构')

    def test_unwrap_reads_nested_report(self):
        """解包函数必须认得 report 嵌套层"""
        self.assertRegex(self.ts, r'data\.report',
                         'unwrapAudit 未读取 report 嵌套层')

    def test_no_top_level_overall_score_read(self):
        """
        禁止再从顶层直接读 overall_score —— 这正是造成恒 0 分的写法。
        允许 report.overall_score / report?.overall_score。
        """
        bad = re.findall(r'\bdata\.overall_score\b', _strip_comments(self.ts))
        self.assertEqual(
            bad, [],
            '检出顶层 data.overall_score 取值 —— API 顶层无此键，会静默得 0 分',
        )

    def test_api_provides_every_field_mcp_reads(self):
        """
        跨文件一致性：MCP server 从顶层读的便捷字段，API 必须真实提供。
        （score / badge_level / risk_level 三个是 API 承诺的顶层字段）
        """
        api = _read(SERVER_PY)
        for key in ('score', 'badge_level', 'risk_level'):
            self.assertRegex(
                api, r'"%s":\s*result\.get\(' % key,
                'API 顶层未提供 %s，但 MCP server 依赖它' % key,
            )

    def test_guardrail_uses_unwrapped_score(self):
        """guardrail 的判定分数必须来自解包结果，否则会对一切工具判 BLOCK"""
        seg = self.ts[self.ts.find('aishield_guardrail'):]
        seg = seg[:seg.find('// ═══', 200)] if '// ═══' in seg[200:] else seg[:3000]
        self.assertIn('unwrapAudit(raw)', seg,
                      'guardrail 未使用 unwrapAudit —— score 恒 0 会导致永远 BLOCK')


class TestProtocolVersionTruthfulness(unittest.TestCase):
    """协议层自报版本 == npm 包版本"""

    def test_server_version_matches_package_json(self):
        ts = _read(INDEX_TS)
        m = re.search(r"const SERVER_VERSION\s*=\s*'([^']+)'", ts)
        self.assertIsNotNone(m, 'index.ts 缺少 SERVER_VERSION 常量')
        pkg = json.loads(_read(PKG_JSON))
        self.assertEqual(
            m.group(1), pkg['version'],
            '协议自报版本 %s 与包版本 %s 不符 —— 用户报障时无法定位代码'
            % (m.group(1), pkg['version']),
        )

    def test_no_hardcoded_version_literal_in_server_ctor(self):
        """McpServer 构造里不得再出现硬编码版本字面量"""
        ts = _read(INDEX_TS)
        m = re.search(r'new McpServer\(\{(.*?)\}\)', ts, re.S)
        self.assertIsNotNone(m, '未找到 McpServer 构造')
        self.assertRegex(m.group(1), r'version:\s*SERVER_VERSION',
                         'McpServer 版本未使用 SERVER_VERSION 单一真源')

    def test_version_gate_guards_the_ts_source(self):
        """index.ts 必须被纳入版本一致性门禁，否则又会悄悄漂移"""
        self.assertIn('mcp-server/src/index.ts', _read(SYNC_PY),
                      'sync_version.py 未把 index.ts 纳入门禁')


class TestPublishedDocsTellTheTruth(unittest.TestCase):
    """
    包内 README 会原样显示在 npmjs.com 的包页面上，是对外的第一句话。

    它曾长期写着"82 rules"，而规则库实际有 201 条 —— 少报了一半以上。
    夸大会被戳穿，少报同样有害：它让这个项目看起来比竞品弱。
    这里把文档里的数字直接绑到规则引擎的实测值上。
    """

    def setUp(self):
        readme = os.path.join(ROOT, 'mcp-server', 'README.md')
        if not os.path.exists(readme):
            self.skipTest('mcp-server/README.md 不存在')
        self.readme = _read(readme)
        try:
            from scanner import rules as R
        except Exception as exc:
            self.skipTest('规则模块不可用: %s' % exc)
        self.R = R

    def test_readme_total_matches_engine(self):
        m = re.search(r'\*\*Total:\s*(\d+)\s*rules\*\*\s*\(MCP type\)', self.readme)
        self.assertIsNotNone(m, 'README 缺少 MCP type 规则总数声明')
        self.assertEqual(
            int(m.group(1)), self.R.get_rule_count('mcp'),
            'README 宣称的规则数与引擎实测值不符',
        )

    def test_readme_skill_total_matches_engine(self):
        m = re.search(r'\*\*(\d+)\s*rules\*\*\s*\(Skill type\)', self.readme)
        self.assertIsNotNone(m, 'README 缺少 Skill type 规则总数声明')
        self.assertEqual(
            int(m.group(1)), self.R.get_rule_count('skill'),
            'README 宣称的 Skill 规则数与引擎实测值不符',
        )

    def test_readme_per_category_counts_match(self):
        """逐类计数也必须真实 —— 总数对但分布错，同样会误导选型"""
        for prefix in ('MCP', 'ASI'):
            for i in range(1, 11):
                cat = '%s%02d' % (prefix, i)
                actual = len(getattr(self.R, cat + '_RULES'))
                m = re.search(r'\|\s*%s\s*\|\s*(\d+)\s*\|' % cat, self.readme)
                self.assertIsNotNone(m, 'README 未列出 %s' % cat)
                self.assertEqual(int(m.group(1)), actual,
                                 '%s 声明 %s 条，实际 %d 条'
                                 % (cat, m.group(1), actual))

    def test_all_six_tools_documented(self):
        """六个工具都要在 README 里出现，漏列等于用户永远不知道它存在"""
        ts = _read(INDEX_TS)
        tools = set(re.findall(r"server\.tool\(\s*'([a-z_]+)'", ts))
        self.assertGreaterEqual(len(tools), 6, '未解析到全部工具注册')
        for t in sorted(tools):
            self.assertIn(t, self.readme, 'README 未记录工具 %s' % t)


# ══════════════════════════════════════════════════════════════
# 第二层：stdio 端到端（缺 node / 构建产物时跳过）
# ══════════════════════════════════════════════════════════════

_AUDIT_RESPONSE = {
    "success": True,
    "score": 87,
    "badge_level": "gold",
    "risk_level": "low",
    "report": {
        "name": "demo-tool",
        "overall_score": 87,
        "security_score": 90,
        "permissions_score": 85,
        "data_handling_score": 80,
        "supply_chain_score": 75,
        "reliability_score": 95,
        "risk_level": "low",
        "badge_level": "gold",
        "rules_count": 201,
        "total_findings": 2,
        "scanned_at": "2026-08-07T12:00:00Z",
        "scanner_version": "4.2.2",
        "owasp_coverage": {"covered": ["MCP01", "MCP03"], "covered_count": 2},
        "findings": [
            {"severity": "high", "description": "hardcoded token", "file": "a.py"},
            {"severity": "low", "description": "nit", "file": "b.py"},
        ],
        "recommendations": ["rotate the token"],
    },
}


class _StubAPI(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0) or 0)
        self.rfile.read(n)
        body = json.dumps(_AUDIT_RESPONSE).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def _free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TestMcpStdioEndToEnd(unittest.TestCase):
    """真正把包跑起来，用 MCP 协议问它要结果"""

    @classmethod
    def setUpClass(cls):
        cls.node = shutil.which('node')
        if not cls.node:
            raise unittest.SkipTest('node 不在 PATH，跳过 stdio 端到端')
        if not os.path.exists(DIST_JS):
            raise unittest.SkipTest('mcp-server/dist 未构建，跳过 stdio 端到端')

        cls.port = _free_port()
        cls.srv = HTTPServer(('127.0.0.1', cls.port), _StubAPI)
        cls.thread = threading.Thread(target=cls.srv.serve_forever, daemon=True)
        cls.thread.start()
        cls.responses = cls._talk()

    @classmethod
    def tearDownClass(cls):
        srv = getattr(cls, 'srv', None)
        if srv:
            srv.shutdown()
            srv.server_close()

    @classmethod
    def _talk(cls):
        """启动 server，跑一轮 initialize + 两次 tools/call，收集响应"""
        env = dict(os.environ, AISHIELD_API_URL='http://127.0.0.1:%d' % cls.port)
        proc = subprocess.Popen(
            [cls.node, 'dist/index.js'],
            cwd=os.path.join(ROOT, 'mcp-server'), env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8', bufsize=1,
        )
        collected = []

        def reader():
            try:
                for line in proc.stdout:
                    collected.append(line)
            except Exception:
                pass

        threading.Thread(target=reader, daemon=True).start()

        msgs = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                        "clientInfo": {"name": "contract-test", "version": "1"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
             "params": {"name": "aishield_scan",
                        "arguments": {"source_url": "https://github.com/x/y",
                                      "tool_type": "mcp"}}},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "aishield_guardrail",
                        "arguments": {"source_url": "https://github.com/x/y",
                                      "auto_block": True}}},
        ]
        try:
            for m in msgs:
                proc.stdin.write(json.dumps(m) + '\n')
                proc.stdin.flush()
                time.sleep(0.35)

            deadline = time.time() + 25
            while time.time() < deadline:
                if any('"id":3' in c or '"id": 3' in c for c in collected):
                    break
                time.sleep(0.25)
        finally:
            try:
                proc.kill()
                proc.wait(timeout=5)
            except Exception:
                pass
            # 显式关闭三条管道，否则 unittest 会刷一屏 ResourceWarning，
            # 把真正的失败信息淹掉。
            for stream in (proc.stdin, proc.stdout, proc.stderr):
                try:
                    if stream:
                        stream.close()
                except Exception:
                    pass

        out = {}
        for line in collected:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if 'id' in d:
                out[d['id']] = d
        return out

    def _text(self, rid):
        d = self.responses.get(rid)
        self.assertIsNotNone(d, 'MCP server 未返回 id=%s 的响应' % rid)
        parts = [c.get('text', '') for c in d.get('result', {}).get('content', [])]
        return '\n'.join(parts)

    def test_initialize_reports_real_version(self):
        info = self.responses.get(1, {}).get('result', {}).get('serverInfo', {})
        pkg = json.loads(_read(PKG_JSON))
        self.assertEqual(info.get('version'), pkg['version'],
                         'initialize 自报版本与包版本不一致')

    def test_scan_reports_real_score_not_zero(self):
        """核心回归：分数必须来自 report，而不是恒 0"""
        txt = self._text(2)
        self.assertIn('Score: 87/100', txt,
                      '扫描分数未正确解包（历史缺陷表现为恒 0/100）:\n' + txt[:400])
        self.assertNotIn('Score: 0/100', txt)

    def test_scan_surfaces_dimensions_and_findings(self):
        txt = self._text(2)
        self.assertIn('Security:      90/100', txt, '五维分数未解包')
        self.assertIn('hardcoded token', txt, 'findings 未解包')
        self.assertIn('rotate the token', txt, 'recommendations 未解包')
        self.assertIn('Rules: 201', txt, 'rules_count 未解包')

    def test_guardrail_passes_clean_tool(self):
        """高分工具必须判 PASS —— 历史缺陷下这里恒为 BLOCK"""
        txt = self._text(3)
        self.assertIn('PASS', txt, 'guardrail 对 87 分工具未判 PASS:\n' + txt[:400])
        self.assertNotIn('BLOCK', txt)
        self.assertIn('MCP01', txt, 'owasp_coverage 未解包')


if __name__ == '__main__':
    unittest.main(verbosity=2)
