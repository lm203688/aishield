# -*- coding: utf-8 -*-
"""
Tech Radar 闭环测试 —— 从生态信号到检测能力的完整链路

这条链路上每一环都曾经或可能悄悄失效，本文件逐环钉死：

  1. arXiv 取数    —— 曾因 export.arxiv.org DNS 不通被误判为"arXiv 挂了"而整源
                       跳过，连续多日 0 产出却不报错。现在是三级端点降级。
  2. 攻击分类      —— 模式表太窄时，扫到 40 篇论文只识别出 2 篇，规则候选恒为 0。
  3. 采纳线过滤    —— 只靠 audit/benchmark 等弱词匹配，会把金融 benchmark、
                       Verilog 硬件论文当成"我们缺失的安全能力"。
  4. 晋升闸门      —— 放行一条会误报的规则，比没有这条规则更糟。
  5. 规则载入      —— 晋升了但 scanner 不加载，等于没晋升。
  6. 文档一致性    —— 晋升后 README 数字不同步会直接红 CI。

测试不触网：所有取数环节用桩替换。
"""

import json
import os
import re
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import capability_gap  # noqa: E402
import promote_rule    # noqa: E402
import tech_radar      # noqa: E402


# ══════════════════════════════════════════════════════════════
# 1. arXiv 三级端点降级
# ══════════════════════════════════════════════════════════════
class TestArxivEndpointChain(unittest.TestCase):
    """单一端点不可达不得导致整源静默归零"""

    def setUp(self):
        self._orig = (tech_radar._arxiv_via_api,
                      tech_radar._arxiv_via_rss,
                      tech_radar._arxiv_via_listing)

    def tearDown(self):
        (tech_radar._arxiv_via_api,
         tech_radar._arxiv_via_rss,
         tech_radar._arxiv_via_listing) = self._orig

    @staticmethod
    def _sig(title):
        return {'_source': 'arxiv', 'id': 'x1', 'title': title, 'url': 'u'}

    def _stub(self, api=None, rss=None, listing=None):
        def mk(behaviour):
            def fn(days, max_results):
                if isinstance(behaviour, Exception):
                    raise behaviour
                return behaviour
            return fn
        tech_radar._arxiv_via_api = mk(api if api is not None else RuntimeError('down'))
        tech_radar._arxiv_via_rss = mk(rss if rss is not None else RuntimeError('down'))
        tech_radar._arxiv_via_listing = mk(listing if listing is not None
                                           else RuntimeError('down'))

    def test_falls_through_to_rss_when_api_dns_fails(self):
        """export.arxiv.org 解析失败是常态，必须自动降级而非放弃"""
        self._stub(api=RuntimeError('getaddrinfo failed'),
                   rss=[self._sig('paper via rss')])
        out = tech_radar.scan_arxiv(days=7, max_results=5)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]['title'], 'paper via rss')

    def test_falls_through_to_listing_when_api_and_rss_fail(self):
        self._stub(rss=[], listing=[self._sig('paper via listing')])
        out = tech_radar.scan_arxiv(days=7, max_results=5)
        self.assertEqual(out[0]['title'], 'paper via listing')

    def test_weekend_empty_rss_is_not_treated_as_success(self):
        """RSS 周末为空是正常的，但不能就此收工——还要试 listing"""
        self._stub(rss=[], listing=[self._sig('weekday paper')])
        out = tech_radar.scan_arxiv(days=7, max_results=5)
        self.assertEqual(out[0]['title'], 'weekday paper')

    def test_all_endpoints_down_reports_error_not_silence(self):
        """全挂时必须留下可诊断的错误，而不是安静地返回空列表"""
        self._stub()
        out = tech_radar.scan_arxiv(days=7, max_results=5)
        self.assertEqual(len(out), 1)
        self.assertIn('_error', out[0])
        self.assertIn('api', out[0]['_error'])
        self.assertIn('rss', out[0]['_error'])
        self.assertIn('listing', out[0]['_error'])

    def test_within_days_filter(self):
        self.assertTrue(tech_radar._within_days(tech_radar._today_str(), 7))
        self.assertFalse(tech_radar._within_days('2000-01-01', 7))
        self.assertTrue(tech_radar._within_days('not-a-date', 7),
                        '日期不可解析时应保留信号，不应静默丢弃')


# ══════════════════════════════════════════════════════════════
# 2. 攻击分类（defend 线）
# ══════════════════════════════════════════════════════════════
class TestSignalClassification(unittest.TestCase):
    """真实论文标题，取自 2026-08-09 当天 arXiv 扫描结果"""

    CASES = [
        ('When Experience Becomes Instruction: Trajectory Poisoning in '
         'Self-Evolving Agent Skill Systems', 'trajectory-poisoning'),
        ('Towards a Risk Assessment of Malicious Skill Files in Coding Agents',
         'skill-poisoning'),
        ('Breaking Customized LLMs for Coding: Automated Red Teaming for '
         'Instruction Backdoor Attacks', 'instruction-hijack'),
        ('Agent Against Agent: An Agentic System for Automatic Prompt '
         'Injection Red Teaming', 'prompt-injection'),
    ]

    def test_known_attack_papers_are_classified(self):
        for title, expected in self.CASES:
            cat, sev, side = tech_radar.classify_signal({'title': title, 'summary': ''})
            self.assertEqual(cat, expected, '误分类: %s' % title[:60])
            self.assertIn(sev, ('critical', 'high', 'medium'))

    def test_defence_papers_are_downgraded_not_escalated(self):
        """防御类论文描述了攻击，但它本身不是威胁，不应判为 critical"""
        cat, sev, side = tech_radar.classify_signal({
            'title': 'PromptShield Home: Ambient Multimodal Prompt Injection '
                     'Defense for Smart-Home Agents', 'summary': ''})
        self.assertEqual(cat, 'prompt-injection')
        self.assertEqual(sev, 'medium')
        self.assertEqual(side, 'defense')

    def test_exploit_language_escalates_to_critical(self):
        _, sev, _ = tech_radar.classify_signal({
            'title': 'Unauthenticated RCE exploit in MCP tool poisoning chain',
            'summary': ''})
        self.assertEqual(sev, 'critical')

    def test_unrelated_paper_is_not_classified(self):
        cat, _, _ = tech_radar.classify_signal({
            'title': 'A Survey of Adversarial Efficiency Degradation for '
                     'Vision Transformer', 'summary': ''})
        self.assertIsNone(cat, '与 agent 安全无关的论文不应产生规则候选')

    def test_coverage_did_not_regress(self):
        """分类器曾经 9 篇只认出 2 篇，导致规则候选恒为 0"""
        titles = [t for t, _ in self.CASES]
        hits = sum(1 for t in titles
                   if tech_radar.classify_signal({'title': t, 'summary': ''})[0])
        self.assertEqual(hits, len(titles))

    def test_defense_side_is_not_drafted(self):
        """根因修复：防御侧信号不得进入攻击起草链路（不得产死稿）"""
        sig = {'_source': 'arxiv', 'id': 'def1',
               'title': 'PromptShield: Prompt Injection Defense for Agents',
               'url': 'https://example.com/x'}
        self.assertIsNone(tech_radar.draft_rule_candidate(sig),
                          '防御侧信号不应起草攻击规则候选')

    def test_repo_spam_is_suppressed(self):
        """根因修复：owner 级仓库刷量（genpark-*）须被抑制为 spam"""
        sig = {'_source': 'github', 'id': 'spam1',
               'title': 'alphaparkinc/genpark-firewall-sentinel-skill',
               'url': 'https://github.com/alphaparkinc/genpark-firewall-sentinel-skill'}
        cat, sev, side = tech_radar.classify_signal(sig)
        self.assertEqual(side, 'spam')
        self.assertIsNone(cat)


# ══════════════════════════════════════════════════════════════
# 3. 采纳线（adopt）—— 能力 gap 分析
# ══════════════════════════════════════════════════════════════
class TestCapabilityGap(unittest.TestCase):

    def test_catalog_impl_files_all_exist(self):
        """能力清单必须有代码背书，否则会随重构悄悄腐化成谎言"""
        problems = capability_gap.verify_catalog()
        self.assertEqual(problems, [], '能力清单存在问题: %s' % problems)

    def test_defensive_papers_recognised(self):
        for title in [
            'DreamGuard: Efficient Runtime Guardrail for LLM Agents via '
            'Risk-Aware World Model',
            'Hardware Keystores for AI Agent Signing Workflows: A Zero-Trust '
            'MCP Enforcement Architecture',
            'PromptShield Home: Ambient Multimodal Prompt Injection Defense '
            'for Smart-Home Agents',
        ]:
            self.assertTrue(
                capability_gap.is_defensive({'id': 'x', 'title': title}),
                '未识别为防御能力: %s' % title[:60])

    def test_weak_keywords_alone_do_not_qualify(self):
        """audit / benchmark / framework 是弱词，单靠它们匹配会淹没采纳清单"""
        for title in [
            'FinEvo-Bench: A Longitudinal Benchmark for Self-Evolving Agents '
            'in Professional Financial Workflows',
            'The Illusion of Visual Tool-Use: A Causal Audit of Thinking with Images',
            'ChainClaw: A Layered Agent Framework for Reliable On-Chain Execution',
        ]:
            self.assertFalse(
                capability_gap.is_defensive({'id': 'x', 'title': title}),
                '弱词误判为防御能力: %s' % title[:60])

    def test_out_of_scope_verticals_excluded(self):
        self.assertFalse(capability_gap.is_defensive({
            'id': 'x',
            'title': 'LLM-Assisted Detection and Repair of Hardware Security '
                     'Vulnerabilities in Verilog Designs'}),
            '硬件安全属于相邻领域，不应进入采纳清单')

    def test_life_science_papers_excluded(self):
        """2026-08-11 实测误报：'risk of bias' 里的 risk 被当成安全强词，
        叠加摘要里的 'LLM agents' 就误判为可采纳防御能力。生命科学论文
        大量复用 risk/safety/integrity 的非安全义项，必须按垂直领域排除。"""
        self.assertFalse(capability_gap.is_defensive({
            'id': 'x',
            'title': 'Authoring and Management of Transparent Research '
                     'Integrity Assessments of Randomised Clinical Trial '
                     'Publications',
            'summary': 'We present a platform where large language model '
                       'agents assist reviewers in assessing risk of bias '
                       'in randomised clinical trial reports.'}),
            '临床试验论文不应进入采纳清单（risk of bias 非安全语义）')

    def test_agent_security_paper_survives_new_exclusions(self):
        """垂直黑名单不能误伤本领域论文——加词后必须重跑这条"""
        self.assertTrue(capability_gap.is_defensive({
            'id': 'x',
            'title': 'Prompt injection attacks against MCP tool descriptions',
            'summary': 'We show malicious skill manifests can hijack agents.'}),
            '本领域攻防论文被新增排除词误伤')

    def test_existing_capability_is_matched_not_flagged_as_gap(self):
        """我们已有的能力不能被报成缺口，否则会重复造轮子"""
        res = capability_gap.analyse([{
            '_source': 'arxiv', 'id': 'a1',
            'title': 'DreamGuard: Efficient Runtime Guardrail for LLM Agents',
            'url': 'u'}])
        self.assertEqual(len(res['gaps']), 0)
        self.assertEqual(len(res['covered']), 1)
        self.assertIn('kill switch', res['covered'][0]['capability'].lower())

    def test_novel_capability_becomes_a_gap(self):
        res = capability_gap.analyse([{
            '_source': 'arxiv', 'id': 'a2',
            'title': 'Neuro-symbolic intent firewall defending LLM agents '
                     'against semantic drift attacks',
            'url': 'u'}])
        self.assertEqual(len(res['gaps']), 1)

    def test_render_section_is_safe_on_empty_input(self):
        self.assertEqual(capability_gap.render_section(
            {'covered': [], 'gaps': []}), [])


# ══════════════════════════════════════════════════════════════
# 4. 晋升闸门
# ══════════════════════════════════════════════════════════════
class TestPromotionGate(unittest.TestCase):
    """闸门若对任何输入都放行，就等于没有闸门"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='aishield_promo_')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _candidate(self, rules, status='ready'):
        path = os.path.join(self.tmp, 'PROPOSED_TEST.json')
        data = {
            'status': status,
            'drafted_at': '2026-08-09',
            'signal': {'id': 't', 'title': 'test', 'url': 'u', 'source': 'test'},
            'attack_category': 'test',
            'severity': 'high',
            'rules': rules,
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return path, data

    def _validate(self, rules, status='ready'):
        path, data = self._candidate(rules, status)
        return promote_rule.validate(path, data, known_patterns=set())

    GOOD = [{'pattern': r'evil_marker_[0-9a-f]{8}_payload',
             'description': '测试规则', 'severity': 'high'}]

    def test_valid_candidate_passes(self):
        ok, problems = self._validate(self.GOOD)
        self.assertTrue(ok, '合格规则被误拒: %s' % problems)

    def test_draft_status_blocked(self):
        ok, problems = self._validate(self.GOOD, status='draft')
        self.assertFalse(ok)
        self.assertIn('expected', problems[0])

    def test_todo_placeholder_blocked(self):
        ok, problems = self._validate([
            {'pattern': 'TODO: regex here', 'description': 'x', 'severity': 'high'}])
        self.assertFalse(ok)
        self.assertIn('TODO', problems[0])

    def test_uncompilable_regex_blocked(self):
        ok, problems = self._validate([
            {'pattern': '([unclosed', 'description': 'x', 'severity': 'high'}])
        self.assertFalse(ok)
        self.assertIn('compile', problems[0])

    def test_overly_broad_pattern_blocked(self):
        for pattern in ['.*', '.?', '[\\s\\S]*']:
            ok, problems = self._validate([
                {'pattern': pattern, 'description': 'x', 'severity': 'high'}])
            self.assertFalse(ok, '过宽模式被放行: %s' % pattern)

    def test_false_positive_on_benign_corpus_blocked(self):
        """在良性样本上命中的规则一律拒绝——误报比漏报更伤信任"""
        ok, problems = self._validate([
            {'pattern': 'description', 'description': 'x', 'severity': 'high'}])
        self.assertFalse(ok)
        self.assertTrue(any('FALSE POSITIVE' in p for p in problems))

    def test_invalid_severity_blocked(self):
        ok, problems = self._validate([
            {'pattern': 'evil_marker_unique_xyz', 'description': 'x',
             'severity': 'URGENT'}])
        self.assertFalse(ok)
        self.assertTrue(any('severity' in p for p in problems))

    def test_duplicate_pattern_blocked(self):
        path, data = self._candidate(self.GOOD)
        ok, problems = promote_rule.validate(
            path, data, known_patterns={self.GOOD[0]['pattern']})
        self.assertFalse(ok)
        self.assertTrue(any('duplicate' in p for p in problems))

    def test_benign_corpus_is_not_empty(self):
        """语料被清空会让误报检查静默失效"""
        self.assertGreaterEqual(len(promote_rule.BENIGN_CORPUS), 8)
        self.assertTrue(any(
            any('\u4e00' <= ch <= '\u9fff' for ch in s)
            for s in promote_rule.BENIGN_CORPUS),
            '良性语料需含中文样本，否则中文规则的误报无法被发现')


# ══════════════════════════════════════════════════════════════
# 5 & 6. 晋升后规则真的生效 + 文档同步
# ══════════════════════════════════════════════════════════════
class TestPromotedRulesAreLive(unittest.TestCase):

    def setUp(self):
        from scanner import rules as R
        self.R = R

    def test_radar_rules_merged_into_all_rules(self):
        for pattern in self.R.RADAR_RULES:
            self.assertIn(pattern, self.R.ALL_RULES,
                          '雷达规则未合入 ALL_RULES，晋升等于白做')

    def test_radar_rules_are_labelled(self):
        """打标签才能在报告里追溯规则来自哪条情报"""
        for desc, _sev in self.R.RADAR_RULES.values():
            self.assertTrue(desc.startswith('[雷达]'))

    def test_radar_rules_carry_provenance(self):
        meta = self.R.get_radar_rules_meta()
        if not self.R.RADAR_RULES:
            self.skipTest('尚无晋升规则')
        self.assertEqual(meta.get('total_rules'), len(self.R.RADAR_RULES))
        for pattern in self.R.RADAR_RULES:
            prov = meta.get('provenance', {}).get(pattern, {})
            self.assertTrue(prov.get('signal_url'),
                            '规则缺少情报溯源 URL，无法回答"为什么有这条规则"')

    def test_radar_rules_do_not_fire_on_benign_corpus(self):
        """已晋升的规则也要持续接受误报检查，而不只在晋升那一刻"""
        for pattern in self.R.RADAR_RULES:
            compiled = re.compile(pattern, re.IGNORECASE)
            for i, sample in enumerate(promote_rule.BENIGN_CORPUS):
                self.assertIsNone(
                    compiled.search(sample),
                    '已上线的雷达规则在良性样本 #%d 上误报: %s' % (i, pattern))

    def test_readme_counts_match_engine_after_promotion(self):
        """晋升会改变规则总数，README 必须同步，否则 CI 契约测试会红"""
        readme = os.path.join(ROOT, 'mcp-server', 'README.md')
        if not os.path.exists(readme):
            self.skipTest('mcp-server/README.md 不存在')
        with open(readme, encoding='utf-8') as f:
            text = f.read()
        m = re.search(r'\*\*Total:\s*(\d+)\s*rules\*\*\s*\(MCP type\)', text)
        self.assertIsNotNone(m)
        self.assertEqual(int(m.group(1)), self.R.get_rule_count('mcp'))

    def test_sync_readme_is_idempotent(self):
        changed_first = promote_rule.sync_readme_counts()
        changed_again = promote_rule.sync_readme_counts()
        self.assertFalse(changed_again,
                         '同步应当幂等，重复执行不该反复改写文件')
        del changed_first


# ══════════════════════════════════════════════════════════════
# 7. 候选文件格式必须与扫描器真实结构一致
# ══════════════════════════════════════════════════════════════
class TestDraftFormatMatchesEngine(unittest.TestCase):
    """
    历史 bug：起草模板生成的是 `class X(Rule)` 的 Python stub，
    但项目根本没有 Rule / RuleResult 类，规则实际是
    {正则: (描述, 严重度)} 字典 —— 每个候选从诞生起就无法被采用。
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='aishield_draft_')
        self._orig_dir = tech_radar.PROPOSED_DIR
        tech_radar.PROPOSED_DIR = self.tmp

    def tearDown(self):
        tech_radar.PROPOSED_DIR = self._orig_dir
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_draft_is_json_with_promotable_shape(self):
        path = tech_radar.draft_rule_candidate({
            '_source': 'arxiv', 'id': 'abcdef123456',
            'title': 'Trajectory Poisoning in Self-Evolving Agent Skill Systems',
            'url': 'https://arxiv.org/abs/1234.5678'})
        self.assertIsNotNone(path)
        self.assertTrue(path.endswith('.json'))

        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        for field in ('status', 'signal', 'attack_category', 'severity', 'rules'):
            self.assertIn(field, data)
        self.assertEqual(data['status'], 'draft')
        rule = data['rules'][0]
        self.assertEqual(set(rule), {'pattern', 'description', 'severity'},
                         '候选字段必须与 scanner/rules.py 的规则结构对应')

    def test_no_reference_to_nonexistent_rule_classes(self):
        from scanner import rules as R
        self.assertFalse(hasattr(R, 'Rule'))
        self.assertFalse(hasattr(R, 'RuleResult'))
        src = open(os.path.join(ROOT, 'scripts', 'tech_radar.py'),
                   encoding='utf-8').read()
        self.assertNotIn('from scanner.rules import Rule', src,
                         '起草模板不得引用不存在的 Rule 类')

    def test_unclassifiable_signal_drafts_nothing(self):
        self.assertIsNone(tech_radar.draft_rule_candidate({
            '_source': 'arxiv', 'id': 'x',
            'title': 'A study of protein folding', 'url': 'u'}))


if __name__ == '__main__':
    unittest.main(verbosity=2)
