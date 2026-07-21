"""
GEO 优化测试 -- 验证结构化数据和发现端点

测试策略:
  - 静态文件测试: 直接读取磁盘文件验证内容正确性（不依赖服务器）
  - 服务器端点测试: 通过 HTTP 请求验证运行时返回（需要服务器启动时自动运行）
  - 验证 SEO 结构化数据、robots.txt、sitemap.xml、Agent Card 等 GEO 关键资产
"""

import unittest
import sys
import os
import json
import re
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 静态文件根目录
_STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'api', 'static')

# 检查服务器是否可达
def _server_ready(port=8450):
    try:
        req = urllib.request.Request(f'http://127.0.0.1:{port}/api/v1/health')
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False

_SERVER_PORT = int(os.environ.get('AISHIELD_PORT', os.environ.get('PORT', 8450)))
_SERVER_UP = _server_ready(_SERVER_PORT)
_BASE_URL = f'http://127.0.0.1:{_SERVER_PORT}'


# ============================================================
#  静态文件测试 (不依赖服务器)
# ============================================================

class TestRobotsTxt(unittest.TestCase):
    """验证 robots.txt 文件内容正确性"""

    def setUp(self):
        path = os.path.join(_STATIC_DIR, 'robots.txt')
        with open(path, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def test_robots_txt_exists(self):
        """robots.txt 文件存在且非空"""
        self.assertTrue(len(self.content) > 0)

    def test_robots_txt_allows_root(self):
        """robots.txt 允许抓取根路径"""
        self.assertIn('Allow: /', self.content)

    def test_robots_txt_disallows_sensitive_paths(self):
        """robots.txt 禁止抓取敏感数据目录"""
        self.assertIn('Disallow: /api/data/', self.content)
        self.assertIn('Disallow: /admin/', self.content)

    def test_robots_txt_contains_sitemap_location(self):
        """robots.txt 包含 Sitemap 声明"""
        self.assertIn('Sitemap:', self.content)
        self.assertIn('https://aishield.dev/sitemap.xml', self.content)

    def test_robots_txt_has_ai_crawler_rules(self):
        """robots.txt 包含 AI 搜索引擎专属规则"""
        self.assertIn('GPTBot', self.content)
        self.assertIn('ClaudeBot', self.content)
        self.assertIn('PerplexityBot', self.content)


class TestSitemapXml(unittest.TestCase):
    """验证 sitemap.xml 结构和内容"""

    def setUp(self):
        path = os.path.join(_STATIC_DIR, 'sitemap.xml')
        with open(path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        self.root = ET.fromstring(self.content)

    def test_sitemap_is_valid_xml(self):
        """sitemap.xml 是有效的 XML 文件"""
        self.assertEqual(self.root.tag, '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')

    def test_sitemap_contains_major_pages(self):
        """sitemap 包含所有主要页面"""
        text = self.content
        self.assertIn('https://aishield.dev/', text)
        self.assertIn('https://aishield.dev/agent.html', text)
        self.assertIn('https://aishield.dev/banned-words', text)
        self.assertIn('https://aishield.dev/report', text)
        self.assertIn('https://aishield.dev/tool/profile', text)
        self.assertIn('https://aishield.dev/.well-known/agent-card.json', text)

    def test_sitemap_urls_have_loc_elements(self):
        """每个 URL 条目包含 loc 元素"""
        ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        urls = self.root.findall(f'{ns}url')
        self.assertTrue(len(urls) >= 5)
        for url in urls:
            loc = url.find(f'{ns}loc')
            self.assertIsNotNone(loc)
            self.assertTrue(len(loc.text) > 0)

    def test_sitemap_homepage_has_highest_priority(self):
        """首页优先级最高 (1.0)"""
        text = self.content
        # 首页应 priority 1.0
        self.assertIn('1.0', text)


class TestAgentCardJson(unittest.TestCase):
    """验证 Agent Card JSON 结构和必要字段"""

    def setUp(self):
        path = os.path.join(_STATIC_DIR, '.well-known', 'agent-card.json')
        with open(path, 'r', encoding='utf-8') as f:
            self.card = json.load(f)

    def test_agent_card_is_valid_json(self):
        """Agent Card 是有效的 JSON 对象"""
        self.assertIsInstance(self.card, dict)

    def test_agent_card_has_required_fields(self):
        """Agent Card 包含必须字段: name, version, skills, trust_score"""
        self.assertIn('name', self.card)
        self.assertIn('version', self.card)
        self.assertIn('skills', self.card)
        self.assertIn('trust_score', self.card)

    def test_agent_card_name_is_aishield(self):
        """Agent Card name 字段为 AIShield"""
        self.assertEqual(self.card['name'], 'AIShield')

    def test_agent_card_has_endpoints(self):
        """Agent Card 包含 API 端点列表"""
        self.assertIn('endpoints', self.card)
        self.assertIsInstance(self.card['endpoints'], dict)
        # 至少包含核心端点
        endpoints = self.card['endpoints']
        self.assertIn('health', endpoints)
        self.assertIn('scan_api', endpoints)

    def test_agent_card_trust_score_has_overall(self):
        """trust_score 包含 overall 总分"""
        trust = self.card['trust_score']
        self.assertIn('overall', trust)
        self.assertIsInstance(trust['overall'], (int, float))
        self.assertTrue(0 <= trust['overall'] <= 100)

    def test_agent_card_skills_have_input_output_schema(self):
        """每个 skill 包含 input_schema"""
        skills = self.card.get('skills', [])
        self.assertTrue(len(skills) >= 1)
        for skill in skills:
            self.assertIn('id', skill)
            self.assertIn('name', skill)
            self.assertIn('input_schema', skill)


class TestAgentHtml(unittest.TestCase):
    """验证 agent.html 包含 JSON-LD 结构化数据"""

    def setUp(self):
        path = os.path.join(_STATIC_DIR, 'agent.html')
        with open(path, 'r', encoding='utf-8') as f:
            self.html = f.read()

    def test_agent_html_contains_json_ld(self):
        """agent.html 包含 JSON-LD 结构化数据"""
        self.assertIn('application/ld+json', self.html)

    def test_agent_html_json_ld_is_parseable(self):
        """JSON-LD 内容可被正确解析"""
        match = re.search(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            self.html, re.DOTALL
        )
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        self.assertIn('@context', data)
        self.assertIn('@type', data)

    def test_agent_html_has_meta_description(self):
        """agent.html 包含 meta description 标签"""
        self.assertIn('<meta name="description"', self.html)

    def test_agent_html_has_og_tags(self):
        """agent.html 包含 Open Graph 标签"""
        self.assertIn('og:title', self.html)
        self.assertIn('og:description', self.html)


class TestIndexPage(unittest.TestCase):
    """验证首页包含 JSON-LD 结构化数据"""

    def setUp(self):
        path = os.path.join(_STATIC_DIR, 'index.html')
        with open(path, 'r', encoding='utf-8') as f:
            self.html = f.read()

    def test_index_contains_json_ld(self):
        """首页包含 JSON-LD 结构化数据"""
        self.assertIn('application/ld+json', self.html)

    def test_index_json_ld_has_organization_type(self):
        """首页 JSON-LD 包含 Organization 类型"""
        match = re.search(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            self.html, re.DOTALL
        )
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        self.assertEqual(data.get('@type'), 'Organization')

    def test_index_has_seo_meta_tags(self):
        """首页包含 SEO meta 标签"""
        self.assertIn('<meta name="description"', self.html)
        self.assertIn('<meta name="keywords"', self.html)
        self.assertIn('<meta name="robots"', self.html)

    def test_index_has_canonical_url(self):
        """首页包含 canonical URL"""
        self.assertIn('rel="canonical"', self.html)
        self.assertIn('https://aishield.dev/', self.html)


class TestBannedWordsPage(unittest.TestCase):
    """验证违禁词页面包含 GEO meta 标签"""

    def setUp(self):
        path = os.path.join(_STATIC_DIR, 'banned_words.html')
        with open(path, 'r', encoding='utf-8') as f:
            self.html = f.read()

    def test_banned_words_page_has_title(self):
        """违禁词页面包含正确的标题"""
        self.assertIn('违禁词', self.html)
        self.assertIn('AIShield', self.html)

    def test_banned_words_page_has_meta_description(self):
        """违禁词页面包含 meta description"""
        self.assertIn('<meta name="description"', self.html)

    def test_banned_words_page_has_og_tags(self):
        """违禁词页面包含 Open Graph 标签"""
        self.assertIn('og:title', self.html)
        self.assertIn('og:description', self.html)

    def test_banned_words_page_has_canonical(self):
        """违禁词页面包含 canonical URL"""
        self.assertIn('rel="canonical"', self.html)
        self.assertIn('https://aishield.dev/banned-words', self.html)


# ============================================================
#  服务器端点测试 (需要服务器启动)
# ============================================================

class TestGeoServerEndpoints(unittest.TestCase):
    """通过 HTTP 验证 GEO 端点的运行时行为"""

    @unittest.skipUnless(_SERVER_UP, "服务器未启动")
    def test_get_robots_txt_returns_200(self):
        """GET /robots.txt 返回 200 和 text/plain"""
        req = urllib.request.Request(f'{_BASE_URL}/robots.txt')
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            ct = resp.headers.get('Content-Type', '')
            self.assertIn('text/plain', ct)

    @unittest.skipUnless(_SERVER_UP, "服务器未启动")
    def test_get_sitemap_xml_returns_200(self):
        """GET /sitemap.xml 返回 200 和 application/xml"""
        req = urllib.request.Request(f'{_BASE_URL}/sitemap.xml')
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            ct = resp.headers.get('Content-Type', '')
            self.assertIn('xml', ct)

    @unittest.skipUnless(_SERVER_UP, "服务器未启动")
    def test_get_agent_card_returns_200(self):
        """GET /.well-known/agent-card.json 返回 200 和 JSON"""
        req = urllib.request.Request(f'{_BASE_URL}/.well-known/agent-card.json')
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode())
            self.assertIn('name', data)

    @unittest.skipUnless(_SERVER_UP, "服务器未启动")
    def test_get_agent_html_returns_200(self):
        """GET /agent.html 返回 200 和 HTML"""
        req = urllib.request.Request(f'{_BASE_URL}/agent.html')
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            ct = resp.headers.get('Content-Type', '')
            self.assertIn('text/html', ct)

    @unittest.skipUnless(_SERVER_UP, "服务器未启动")
    def test_get_index_returns_html_with_json_ld(self):
        """GET / 首页返回包含 JSON-LD 的 HTML"""
        req = urllib.request.Request(f'{_BASE_URL}/')
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            html = resp.read().decode()
            self.assertIn('application/ld+json', html)

    @unittest.skipUnless(_SERVER_UP, "服务器未启动")
    def test_get_banned_words_returns_html(self):
        """GET /banned-words 返回 200 和 HTML"""
        req = urllib.request.Request(f'{_BASE_URL}/banned-words')
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            ct = resp.headers.get('Content-Type', '')
            self.assertIn('text/html', ct)


if __name__ == '__main__':
    unittest.main(verbosity=2)
