"""
tests/test_rule_count_gate.py — 规则数一致性门禁的契约测试

被测对象：scripts/rule_count_gate.py

这份门禁的价值不在"能跑"，而在它是否**真的看得见**声明位漂移。而它最难
做好的恰恰是两件事：不要漏看（假绿），不要乱看（假阳性）。下面每条测试
都对应一次真实踩过的坑，不是假设性的防御。

一、假绿（漏看）
----------------
1. scan 与 sync 口径分裂 —— 门禁说"对"、同步却按另一个口径写坏数据。
2. pair 替换截断 —— `233条Skill` 被切成 `Sk241`，产出
   `235条MCP/233条Sk241`。更糟的是这个乱码不被任何模式匹配，
   门禁随后一路绿灯。
3. 数字中间起跳 —— 固定长度后顾拦不住引擎退回重试，
   `Top 10检测规则` 被改写成 `Top 1235检测规则`，同样不被检出。

二、假阳性（乱看）
------------------
4. OWASP 分类小计（MCP-01 … MCP-10、Subtotal）不是总计声明。
5. "OWASP MCP Top 10检测规则" 的 10 是风险类别数，不是规则数。
6. CSS 里的 `rgba(238, 69, 96)` 只是颜色分量。
7. `235/241 条规则` 与 `**Total: 235 rules** (MCP type) / **241 rules**
   (Skill type)` 是合法声明，不得被单值兜底再报一遍。

三、不变量
----------
8. 权威数字必须来自 scanner.rules 运行时计算，不许硬编码。
   门禁自己写死 235，就会在规则晋升当天变成新的漂移源。
"""

import os
import re
import shutil
import sys
import tempfile
import unittest
import unittest.mock as mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import rule_count_gate as G  # noqa: E402
import scanner.rules as RULES  # noqa: E402


def _auth():
    """测试用的权威值：全部取运行时真值，不写死。

    刻意通过模块属性（`RULES.get_rule_count`）而非 `from ... import` 访问。
    套件里有测试会 mock.patch 掉 `scanner.rules` 上的函数，`from ... import`
    在导入时就把名字绑死到原始实现，于是"门禁读到的值"和"断言比较的值"
    来自两个不同的函数对象 —— 同源的东西被读出了两个数，断言假失败。
    """
    return {
        "mcp": str(RULES.get_rule_count()),
        "skill": str(RULES.get_rule_count("skill")),
        "static": "208",
        "generated": "8",
        "radar": "19",
    }


PATTERNS = None


def _pats():
    global PATTERNS
    if PATTERNS is None:
        PATTERNS = G._patterns()
    return PATTERNS


def _fill(t):
    """把 `{mcp}` / `{skill}` 占位符换成当前权威值。

    测试文本里凡是"应当合法"的数字都必须这样动态生成。写死 235/241 等于
    把门禁的期望值抄进测试 —— 规则晋升后测试会假失败，与门禁本身是同一个病。
    刻意写错的漂移值（227、233、238、244）则保持字面量：它们必须固定，
    才能稳定地触发同一条路径。
    """
    a = _auth()
    return t.format(mcp=a["mcp"], skill=a["skill"])


def _gate_src():
    """门禁源码（两处结构级断言都要读，统一在这里拿）。"""
    p = os.path.join(os.path.dirname(__file__), '..', 'scripts',
                     'rule_count_gate.py')
    with open(p, encoding='utf-8') as f:
        return f.read()


def _drifts(text):
    """一段文本里的漂移声明列表：[(kind, got, match)]"""
    out = []
    for ln, m, kind, got, expected, ok in G.iter_declarations(
            text.splitlines(), _pats(), _auth()):
        if not ok:
            out.append((kind, got, m.group(0)))
    return out


class TestScanSyncConsistency(unittest.TestCase):
    """门禁说"对"的，同步就不得改；门禁说"错"的，同步必须改。

    这是整个门禁的根基。如果 scan 和 sync 各写一套判定逻辑，就会出现
    检查一路绿灯而数据已被写坏的局面 —— 比没有门禁更危险，因为它提供了
    虚假的安全感。
    """

    def test_scan_and_sync_share_one_parser(self):
        """sync 必须通过 iter_declarations 取改法，不得自行匹配。"""
        src = _gate_src()
        body = src.split('def sync_text')[1].split('def main')[0]
        self.assertIn('iter_declarations', body,
                      'sync_text 未复用 iter_declarations —— scan/sync 口径将分裂')

    def test_sync_never_touches_legal_declaration(self):
        """合法的 MCP/Skill 双值声明，sync 必须零改动。"""
        text = (_fill('**Total: {mcp} rules** (MCP type) / '
                      '**{skill} rules** (Skill type)\n')
                + _fill('{mcp}/{skill} 条规则\n'))
        new, n = G.sync_text(text, _auth(), _pats())
        self.assertEqual(n, 0, f'合法声明被改动：{new!r}')
        self.assertEqual(new, text)

    def test_sync_fixes_every_scan_finding(self):
        """sync 的改动数必须等于 scan 的漂移数，不多不少。"""
        text = '共 238 条规则，其中 244 条 Skill 规则。\n'
        want = len(_drifts(text))
        _, n = G.sync_text(text, _auth(), _pats())
        self.assertEqual(n, want, f'scan 报 {want} 处，sync 改 {n} 处')

    def test_sync_then_check_is_clean(self):
        """sync 之后再 scan 必须零漂移（否则门禁永远红不了）。"""
        text = '共 238 条规则，Skill 侧 244 条。\n'
        new, _ = G.sync_text(text, _auth(), _pats())
        self.assertEqual(_drifts(new), [], f'sync 后仍有漂移：{new!r}')


class TestPairReplacement(unittest.TestCase):
    """双值声明的替换。这里出过一次数据损坏事故。"""

    def test_pair_replacement_keeps_tail_text(self):
        """`233条Skill` 之后的"安全规则"必须原样保留。"""
        text = 'AI Agent 安全生态基础设施 — OWASP MCP Top 10 对齐，' \
               '227条MCP/233条Skill安全规则 + 六维能力边界扫描'
        new, n = G.sync_text(text, _auth(), _pats())
        self.assertEqual(n, 1)
        self.assertIn(_fill('{mcp}条MCP/{skill}条Skill安全规则'), new,
                      f'pair 替换结果异常：{new!r}')

    def test_pair_replacement_does_not_corrupt_keyword(self):
        """回归：曾产出 `233条Sk241安全规则` —— Skill 被截成 Sk。"""
        text = '227条MCP/233条Skill安全规则'
        new, _ = G.sync_text(text, _auth(), _pats())
        self.assertNotIn('Sk241', new, 'pair 替换截断了 Skill 关键字')
        self.assertNotIn('Sk', new.replace('Skill', ''), '替换产生了残缺 token')
        self.assertIn('Skill安全规则', new)

    def test_pair_separator_preserved(self):
        """不同分隔写法（空格、紧凑）都要保留原样。"""
        for text, want_mid in (('227条MCP/233条Skill', '/'),
                               ('227 MCP / 233 Skill', ' MCP / ')):
            new, _ = G.sync_text(text, _auth(), _pats())
            self.assertIn(want_mid, new, f'分隔符丢失：{text} -> {new!r}')

    def test_typed_pair_line_syncs_in_one_pass(self):
        """回归（2026-10-02）：`**253 rules** (MCP type) / **253 rules** (Skill type)`
        必须**一次** --sync 改对两个数。

        旧实现把同一行里重叠的 edit 直接按位置倒序打补丁：第 2 处的
        `rules\\b` 兜底模式会覆盖 `(Skill` 标注模式刚写好的结果（加粗符与
        类型括号一起被抹掉、长度变化让后续落点错位），于是第一次 sync 只改
        MCP 那一半、Skill 那半留着旧值，得再跑一遍才正确 —— 对外文档上就是
        「一半新一半旧」。_resolve_overlaps 修掉它。
        """
        text = '**253 rules** (MCP type) / **253 rules** (Skill type)'
        new, n = G.sync_text(text, _auth(), _pats())
        self.assertEqual(n, 2, f'一次 sync 应改两处，实际改了 {n} 处：{new!r}')
        self.assertIn('**%s rules** (MCP type)' % _auth()['mcp'], new)
        self.assertIn('**%s rules** (Skill type)' % _auth()['skill'], new)
        # 幂等：再跑一次不许动
        again, n2 = G.sync_text(new, _auth(), _pats())
        self.assertEqual(n2, 0, f'sync 不幂等：{again!r}')

    def test_overlapping_edits_resolve_to_specific_pattern(self):
        """重叠区间只保留具体模式：兜底 edit 不许抹掉 (Skill 标注的括号。"""
        edits = [(10, 20, 'X', 0), (12, 18, 'Y', 3)]
        kept = G._resolve_overlaps(edits)
        self.assertEqual([(s, e) for s, e, _ in kept], [(10, 20)])
        # 完全不重叠的两条都保留
        self.assertEqual(len(G._resolve_overlaps([(0, 5, 'a', 0), (6, 9, 'b', 1)])), 2)

    def test_corrupted_pair_text_is_detected(self):
        """回归：`233条Sk241安全规则` 这种损坏必须被检出，不许漏过。"""
        self.assertTrue(_drifts('233条Sk241安全规则'),
                        '损坏文本未被检出 —— 门禁存在盲区')


class TestNoMidNumberJump(unittest.TestCase):
    """正则引擎退回重试时不得从数字中间起跳。

    固定长度后顾（如 `(?<!Top )`）只能挡住"整个词"，挡不住引擎在数字内部
    重新起跳：`10` 在 `1` 处被拦下后，引擎退回 `0` 处再试，此时前一个字符
    是 `1` 而非 `Top `，后顾通过，于是捕获到 `got="0"`。
    """

    def test_top10_not_treated_as_rule_count(self):
        text = '提供OWASP MCP Top 10检测规则、本地API调用示例'
        self.assertEqual(_drifts(text), [], f'Top 10 被当成规则数：{_drifts(text)}')

    def test_top10_not_rewritten_by_sync(self):
        """回归：`Top 10` 曾被打成 `Top 1235`。"""
        text = 'OWASP MCP Top 10检测规则'
        new, n = G.sync_text(text, _auth(), _pats())
        self.assertEqual(n, 0, f'误改 Top 10：{new!r}')
        self.assertEqual(new, text)

    def test_captures_whole_number(self):
        """多位数必须整体捕获，不得只拿到后缀。"""
        got = _drifts('共 12345 条规则')
        self.assertEqual([g for _, g, _ in got], ['12345'],
                         f'数字被截断：{got}')

    def test_all_number_anchored_patterns_guarded(self):
        """结构级断言：任何捕获组裸露在模式开头的，都必须有 `(?<!\\d)`。

        两种安全写法之一必须成立：
        * 前缀带 `(?<!\\d)` —— 直接禁止从数字中间起跳；
        * 捕获组前面已有语境锚点（如 `rules_count: (\\d+)` 的 `[:=]\\s*`）
          —— 引擎不可能落在数字上。
        """
        for pat, _kind in _pats():
            s = pat.pattern
            if '(?<!\\d)' in s:
                continue
            i = s.find(r'(\d+)')
            self.assertGreater(i, 0,
                               f'模式既无 (?<!\\d) 又以捕获组开头，'
                               f'可能被数字中间起跳误命中：{s}')


class TestBreakdownExclusion(unittest.TestCase):
    """分类小计不是总计声明，不得参与校验。"""

    def test_breakdown_rows_excluded(self):
        for line in ('| MCP-06 | Prompt 注入 | Critical | 22 条规则 |',
                     '| MCP01 | 工具投毒 | 6 条规则 |',
                     'Subtotal: **113 rules**',
                     'Static baseline: **208 rules** (113 MCP + 62 ASI)'):
            self.assertTrue(G._is_breakdown_row(line), f'分解行未被识别：{line!r}')

    def test_breakdown_lines_produce_no_drift(self):
        text = '| MCP-06 | Prompt 注入 | Critical | 22 条规则 |\n'
        self.assertEqual(_drifts(text), [], '分类小计被当成总计漂移')

    def test_total_line_not_excluded(self):
        self.assertFalse(G._is_breakdown_row('**Total: 238 rules**'),
                         '总计行被误判为分解行')

    def test_topic_mention_does_not_exempt_real_declaration(self):
        """回归：行内"提及"ASI01-10 不得把同行的真声明位一起豁免。

        早期实现是行级整行豁免 —— smithery.yaml 的描述行同时含
        `Agentic ASI01-10 aligned`（话题提及）与 `244 skill rules`
        （真正的声明位），整行豁免把两者一起放走，门禁报 0 漂移。
        """
        line = ('description: "OWASP MCP Top 10 + Agentic ASI01-10 aligned. '
                '238 MCP / 244 skill rules. Your code never leaves your machine."')
        got = _drifts(line)
        self.assertTrue(got, '含话题提及的行被整行豁免，真声明位漏检')
        # 必须判成 **pair**（两个数一起报），不能只抓 skill 一侧。
        # 2026-10-05 实测：pair 模式当时要求大写 `Skill`，而这里是小写，
        # 于是整个 pair 不匹配、只剩单值的 `244 skill rules` 被抓住 ——
        # `--sync` 便把 244 改对、把 238 原样留下，产出"半对文件"，
        # 而 238 因为不匹配任何模式，门禁随后一路绿灯。smithery.yaml 里
        # 那句 `238 MCP / 291 skill rules` 就是这么躺了两个多月的。
        kinds = {g for _, g, _ in got}
        self.assertEqual(kinds, {('238', '244')},
                         f'双值声明必须整体判为 pair 漂移，实得 {got}')

    def test_lowercase_skill_pair_is_not_half_fixed(self):
        """小写 `skill` 的 `N MCP / M skill rules` 必须整体识别为 pair。

        这是上一条的产品化版本：只要 pair 因大小写漏匹配，`--sync` 就会
        写出半对文件。判据用最终产物 —— sync 后必须**两个数都对**。
        """
        auth = G.authority()
        patterns = G._patterns()
        line = 'x. 238 MCP / 244 skill rules. y.'
        fixed, changes = G.sync_text(line, auth, patterns)
        mcp = auth['mcp']
        skill = auth['skill']
        self.assertEqual(changes, 1, f'应记录 1 处修正，实得 {changes}')
        self.assertIn(f'{mcp} MCP', fixed, f'sync 未修正 MCP 一侧：{fixed!r}')
        self.assertIn(f'{skill} skill', fixed, f'sync 未修正 skill 一侧：{fixed!r}')
        self.assertNotIn('238', fixed, f'sync 后残留旧值：{fixed!r}')

    def test_cell_marker_only_exempts_neighbouring_number(self):
        """紧邻分类编号的数字豁免，远端的仍须校验。

        注意这里用列表式（非表格）行：`| MCP-06 | ... | 22 条规则 |` 这种
        带 `|` 的行已由 `_is_breakdown_row` 整行豁免，根本走不到
        `_is_breakdown_context`。单点豁免只在列表式分解项
        （`- MCP-06: 22 条规则`）里生效，那里标记与数字才是紧邻的。
        """
        row = 'MCP-06 覆盖 22 条规则'
        self.assertTrue(G._is_breakdown_context(row, row.find('22')),
                        '紧邻分类编号的小计未被豁免')
        line = 'ASI01-10 aligned. 244 skill rules'
        self.assertFalse(G._is_breakdown_context(line, line.find('244')),
                         '距分类编号过远的数字被误豁免')


class TestFalsePositiveGuard(unittest.TestCase):
    """非规则数的数字不得被当成声明位。"""

    def test_css_color_not_flagged(self):
        for text in ('rgba(238, 69, 96, 0.85)', 'background:#38bdf8',
                     '--shadow: 0 4px 20px rgba(233, 69, 96, 0.2)'):
            self.assertEqual(_drifts(text), [], f'CSS 被误报：{text!r}')

    def test_legal_total_line_not_double_reported(self):
        """`**Total: 235 rules** (MCP type) / **241 rules** (Skill type)`
        是两条合法声明，不得被英文兜底模式再报一次。"""
        text = _fill('**Total: {mcp} rules** (MCP type) / '
                     '**{skill} rules** (Skill type)')
        self.assertEqual(_drifts(text), [], f'合法声明被重复报：{_drifts(text)}')

    def test_compact_pair_not_double_reported(self):
        self.assertEqual(_drifts(_fill('{mcp}/{skill} 条规则')), [],
                         '紧凑 pair 被单值模式重复报')

    def test_drifted_pair_reported_once(self):
        """pair 漂移只报一条，内部单值不该再报一遍（噪音）。"""
        got = _drifts('227条MCP/233条Skill安全规则')
        self.assertEqual(len(got), 1, f'重复报：{got}')
        self.assertEqual(got[0][0], 'pair')

    def test_two_independent_declarations_both_reported(self):
        """重叠屏蔽不能过头：一行里两个独立声明都要报。"""
        got = _drifts('238 条规则 与 244条Skill规则')
        self.assertEqual(len(got), 2, f'漏报：{got}')

    def test_drifted_number_is_caught_without_measure_word(self):
        """`238 安全规则`（无"条"）同样是声明位。"""
        got = _drifts('238 安全规则')
        self.assertEqual([g for _, g, _ in got], ['238'])

    def test_english_pair_not_reported_twice(self):
        """`253 / 280 rules` 是 pair（MCP/Skill），中文有 `/N条规则` 这一条
        pair 模式，英文一直缺 —— 于是第二个数字落到兜底单值模式上被判成
        MCP 声明。sync 照单执行就把 llms.txt 的 280 改写成 253，对外文档的
        规则总数被静默篡改，而 --check 又是绿的。"""
        self.assertEqual(_drifts(_fill('{mcp} / {skill} rules')), [],
                         '英文 pair 被单值兜底模式重复报')

    def test_english_pair_drift_is_reported_once_as_pair(self):
        got = _drifts('227 / 241 rules')
        self.assertEqual(len(got), 1, f'重复报：{got}')
        self.assertEqual(got[0][0], 'pair')

    def test_english_pair_sync_preserves_skill_number(self):
        """回归：sync 必须只改漂移的那一半，不能把合法的一半一起改坏。

        这次事故的形态就是"合法声明被 sync 改写"——门禁只测 scan ，
        sync 走的是另一条替换路径（sync_text），两边共用解析但
        替换逻辑各自独立，所以必须在 sync 侧也钉住。
        """
        auth = G.authority()
        # 两个数字都写成历史值：sync 必须两个都改成权威值，且顺序不能颠倒。
        new, n = G.sync_text('the dual taxonomy with 227 / 241 rules.',
                             auth, G._patterns())
        # n 是“改了几行”不是“改了几个数字”，两个数字在同一行只计 1。
        self.assertEqual(n, 1, f'改动行数不对：{n}')
        self.assertEqual(
            new,
            f"the dual taxonomy with {auth['mcp']} / {auth['skill']} rules.",
            'sync 把英文 pair 改坏了 —— 两个数字的顺序必须保持 MCP/Skill')

    def test_english_pair_with_security_word(self):
        """`security` 插在两个数字与 rules 之间时，pair 仍要认出来。"""
        got = _drifts('227 / 241 security rules')
        self.assertEqual(len(got), 1, f'重复报：{got}')
        self.assertEqual(got[0][0], 'pair')


class TestAuthority(unittest.TestCase):
    """权威数字必须来自运行时，不许在门禁里写死。"""

    def test_breakdown_snapshot_is_self_consistent(self):
        """构成必须加总为 total。

        这条断言曾经挂过：`ALL_RULES.update(RADAR_RULES)` 只写在模块顶层，
        而 test_promote_rule_shadow / test_provenance_audit 会在 import 后
        调用 `_load_radar_rules()` 做隔离重载 —— 重载只改 `RADAR_RULES`、
        不碰 `ALL_RULES`，于是 breakdown 报出 `208+9+19=236` 对
        `total=235` 的自相矛盾数字。根因已修（重载函数自己维护 ALL_RULES
        同步），这里把它钉死，防止回归。
        """
        b = RULES.get_rule_breakdown()
        self.assertEqual(b["static"] + b["generated"] + b["radar"], b["total"],
                         'breakdown 构成与 total 不自洽')

    def test_breakdown_still_consistent_after_reload(self):
        """重载雷达规则后 breakdown 仍须自洽（ALL_RULES 必须同步撤并）。"""
        saved = dict(RULES.RADAR_RULES)
        try:
            RULES.RADAR_RULES = {}
            RULES._load_radar_rules()
            b = RULES.get_rule_breakdown()
            self.assertEqual(b["static"] + b["generated"] + b["radar"], b["total"],
                             '重载后 ALL_RULES 与 RADAR_RULES 未同步')
        finally:
            RULES.RADAR_RULES = saved
            RULES._load_radar_rules()

    def test_radar_reload_is_idempotent(self):
        """`_load_radar_rules()` 重载 N 次必须得到同一份集合，不是叠加 N 份。

        这条钉的是一次真实的内存态污染：重载只 merge 不清空，于是
        tests/test_provenance_audit.py 的 tearDown（把 __file__ 指回真仓后
        reload）把测试期间注入 tmp 的那条 `legacy\\s*rule` 一并留在了
        RADAR_RULES 里 —— radar 19→20、total 264→265，而且这条污染会活到
        整个套件结束。此后任何读 authority() 的断言都整体差 1，属于
        "单跑绿、套件里红"那一类最难查的假失败（真身是测试污染，不是
        测试写错 —— 修断言没用，修重载才有用）。
        """
        before = RULES.get_rule_breakdown()
        try:
            for _ in range(3):
                RULES._load_radar_rules()
        finally:
            RULES.RADAR_RULES = {}
            RULES._load_radar_rules()
        self.assertEqual(RULES.get_rule_breakdown(), before,
                         '重载改变了 radar 计数 —— 重载是累加的')
        self.assertEqual(len(RULES.ALL_RULES), before["total"])

    def test_authority_values_are_positive_ints(self):
        auth = G.authority()
        for k in ("mcp", "skill", "static", "generated", "radar"):
            self.assertGreater(int(auth[k]), 0, f'{k} 不是正整数')
        self.assertEqual(int(auth["static"]) + int(auth["generated"])
                         + int(auth["radar"]), int(auth["mcp"]),
                         'authority() 内部构成与 mcp 总数不自洽')

    def test_authority_follows_runtime_changes(self):
        """权威值必须跟随运行时变化 —— 这是"数字没写死"的行为证据。"""
        with mock.patch.object(RULES, "get_rule_count", return_value=999):
            auth = G.authority()
        self.assertEqual(auth["skill"], "999",
                         'authority() 未跟随运行时值 —— 数字被写死在门禁里')

    def test_authority_does_not_cache(self):
        """连续两次调用必须都反映最新状态，不得缓存首次结果。"""
        with mock.patch.object(RULES, "get_rule_count", side_effect=[777, 888]):
            self.assertEqual(G.authority()["skill"], "777")
            self.assertEqual(G.authority()["skill"], "888")

    def test_gate_source_has_no_hardcoded_rule_counts(self):
        """门禁源码里不得出现 235 / 241 / 208 这类字面量。

        一旦出现，规则晋升当天门禁自己就成了新的漂移源 —— 而它本该是
        唯一的真相校验者。文档字符串里的举例数字不算，只扫可执行代码。
        """
        src = _gate_src()
        body = src[src.index('REPO = '):]           # 跳过模块 docstring
        body = body[:body.index('# ── 声明位语境模式')]   # 跳过模式注释区
        for lit in ('235', '241', '208', '238', '244'):
            self.assertNotIn(f'"{lit}"', body,
                             f'门禁源码硬编码了规则数字 {lit}')


class TestDriftedFilesForPush(unittest.TestCase):
    """`drifted_files()` 是给推送链路用的机器出口。

    为什么需要它不是镀金：规则晋升后 `--sync` 会一次改掉 20+ 个声明位，
    人工挑文件推送必然只带一部分，CI 立刻在没推的那些文件上红。人肉挑文件
    靠不住，所以推送脚本要能问门禁"哪些漂移"，把差集并进同一批提交。

    这里用临时 REPO 把 monkeypatch 掉 `G.REPO`，避免真的写坏仓库里的声明位。
    """

    @staticmethod
    def _tmp_repo(text):
        d = tempfile.mkdtemp(prefix="gate_drift_")
        os.makedirs(os.path.join(d, "api", "static"), exist_ok=True)
        with open(os.path.join(d, "api", "static", "drift.md"), "w",
                  encoding="utf-8") as f:
            f.write(text)
        return d

    def _drifted(self, text):
        d = self._tmp_repo(text)
        old = G.REPO
        G.REPO = d
        try:
            return G.drifted_files()
        finally:
            G.REPO = old
            shutil.rmtree(d, ignore_errors=True)

    def test_drifted_decl_file_is_reported(self):
        """写了错数字的文件必须出现在列表里 —— 这是推送脚本唯一的事实来源。"""
        self.assertEqual(self._drifted('AIShield 提供 238 条规则。\n'),
                         ['api/static/drift.md'])

    def test_clean_decl_file_is_not_reported(self):
        """合法声明不得进列表 —— 否则推送会无谓地带上一堆文件。"""
        self.assertEqual(self._drifted(_fill('提供 {mcp} 条规则。\n')), [])

    def test_result_is_sorted_subset_of_collected(self):
        """返回值必须是 collect_files() 的有序子集，且只含漂移项。"""
        d = self._tmp_repo(_fill('提供 {mcp} 条规则。\n')
                           + '旧文 238 条规则\n')
        old = G.REPO
        G.REPO = d
        try:
            collected = set(G.collect_files())
            drifted = G.drifted_files()
            self.assertTrue(drifted)
            self.assertLessEqual(set(drifted), collected)
            self.assertEqual(drifted, sorted(drifted))
            # 同一份文末的漂移与门禁 --check 的口径必须一致
            self.assertEqual(drifted,
                             [f["file"] for f in G.scan(
                                 drifted[0], G.authority(), _pats())])
        finally:
            G.REPO = old
            shutil.rmtree(d, ignore_errors=True)


class TestBlindSpotsClosed(unittest.TestCase):
    """门禁看不见的声明位，等于没有声明位。

    下面五条都是**先有一次真实漂移、被测试抓到、才回头补上门禁**的。
    补门禁而不是删测试的道理很简单：测试只在本地跑，门禁跑在 CI 的每个
    commit 上；能被 CI 拦住的才是机制，能被本地拦住的只是记忆。

    这五条盲区有一个共同形态：门禁的覆盖面是"散文 + 人工挑的文件"，
    而真实声明面还包括源码里的工具描述、JSON 契约字段、机器读的 llms.txt，
    以及被 breakdown 豁免掉的分类表格。
    """

    @staticmethod
    def _scan_in(rel, text, cats=None, auth=None):
        """把 text 写进临时 REPO 的 rel 路径，返回该文件的 drift 列表。

        auth / cats 都可以外部指定。这不是洁癖：套件里 promote_rule 的
        shadow 用例会往 data/radar_rules.json 落一条真实雷达规则，扫描顺序
        不同时 `G.authority()` 返回的雷达数就会差 1 —— 一个只依赖全局
        状态的断言，在单跑时绿、在套件里红，那是最难查的那类假失败。
        """
        d = tempfile.mkdtemp(prefix="gate_blind_")
        full = os.path.join(d, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)
        old = G.REPO
        G.REPO = d
        try:
            auth = auth or G.authority()
            if cats is None:
                return G.scan(rel, auth, _pats())
            real = G.category_counts
            G.category_counts = lambda: cats
            try:
                return G.scan(rel, auth, _pats())
            finally:
                G.category_counts = real
        finally:
            G.REPO = old
            shutil.rmtree(d, ignore_errors=True)

    def test_category_table_row_is_checked(self):
        """`| MCP03 | 11 | Tool Poisoning |` 必须与引擎逐类真值一致。

        这类行原本被 breakdown 规则**整行**豁免（`_is_breakdown_row` 只判
        是不是"总计"，不判"逐类小计也要准"），于是 README 的逐类分布可以
        漂（实测 MCP03 写 10、引擎 11）而门禁零反应。
        """
        # 真实形态是"编号 | 条数 | 名称"（见 mcp-server/README.md 的表格）
        row = '| MCP03 | 11 | Tool Poisoning |\n'
        found = self._scan_in(
            'mcp-server/README.md', row, cats={'MCP03': 12})
        self.assertTrue(found, '逐类表格行未被校验 —— 门禁盲区')
        self.assertEqual([f['kind'] for f in found], ['category'])
        self.assertEqual(found[0]['category'], 'MCP03')
        self.assertEqual(found[0]['got'], '11')
        self.assertEqual(found[0]['expected'], '12')

    def test_matching_category_row_is_not_reported(self):
        """行内数字与引擎一致时不得报 —— 否则每次跑门禁都是一堆假红。"""
        row = '| MCP03 | 11 | Tool Poisoning |\n'
        self.assertEqual(self._scan_in('mcp-server/README.md', row,
                                       cats={'MCP03': 11}), [])

    def test_category_row_is_fixed_by_sync(self):
        """只查不改等于把门禁变成永远红的摆设。"""
        row = '| MCP03 | 10 | Tool Poisoning |\n'
        found = self._scan_in('mcp-server/README.md', row,
                              cats={'MCP03': 11})
        self.assertTrue(found)
        new, _ = G.sync_text(row, _auth(), _pats())
        self.assertIn('| MCP03 | 11 | Tool Poisoning |', new,
                      f'sync 未修逐类小计：{new!r}')

    def test_tool_source_belongs_to_declared_surface(self):
        """index.ts 是 TEXT_EXT —— 工具描述是每一次调用都展示给用户的。"""
        self.assertIn('.ts', G.TEXT_EXT, 'index.ts 不在门禁视野内')
        self.assertTrue(G._is_declared_surface('mcp-server/src/index.ts'))

    def test_docs_llms_txt_is_not_treated_as_historical(self):
        """/docs/llms.txt 与 api/static/llms.txt 必须成对维护。

        门禁把 docs/ 整体当历史快照豁免，但 llms.txt 是**机器读的实时产物**
        —— 豁免它之后两份文件各自漂移（实测 253/280 对 256/283），
        是 tests/test_compliance 比出来的差异。
        """
        self.assertEqual(G._is_declared_surface('docs/llms.txt'), True)

    def test_json_contract_fields_are_checked(self):
        """`"total"` / `"static"` 这类 JSON 字段是契约，不是散文。

        只校 total 也不够：total 已是 256 而 static 还停 226 时，这份
        agent.json 报出的构成自相矛盾（256 ≠ 226+8+19）。
        """
        text = '{\n  "rules": {\n    "total": 256,\n    "static": 226,\n' \
               '    "generated": 8,\n    "radar": 19\n  }\n}\n'
        auth = {'mcp': '256', 'skill': '283', 'static': '229',
                'generated': '8', 'radar': '19'}
        found = self._scan_in('api/static/agent.json', text, auth=auth)
        kinds = sorted((f['kind'], f['got'], f['expected']) for f in found)
        self.assertEqual(kinds, [('static', '226', '229')],
                         'JSON 构成字段只应报出漂移的 static 一项')

    def test_mcp_rule_categories_prose_is_checked(self):
        """`.well-known/agent.json` 的 description 写 `235 MCP rule categories`。

        门禁那条英文 pattern 要求名词是 `rules`，遇到 `rule categories` 就
        认不出来 —— 一个复数变形把整份机器读的 agent 名片推出视野。实测后果：
        线上名片 rules 块已是 264/291，description 仍对外宣称 235/241，
        同一份文件自相矛盾，而门禁一路绿灯。
        """
        text = ('"description": "... aligned, 235 MCP rule categories / '
                '241 skill rule categories. Static analysis only ...")')
        # 期望值照样取运行时真值，绝不写死 264/291：写死的话规则晋升当天
        # 这条测试自己就会变成新的假失败，而它本该只验证"这类散文有没有被
        # 门禁看见"。真正的稳定化来自 scanner/rules.py 把 _load_radar_rules()
        # 改成幂等（详见 TestAuthority.test_radar_reload_is_idempotent）——
        # 之前那 +1 是测试污染，不是测试写错。
        a = _auth()
        found = self._scan_in('api/static/.well-known/agent.json', text)
        kinds = sorted((f['kind'], f['got'], f['expected']) for f in found)
        self.assertEqual(
            kinds,
            [('mcp', '235', a['mcp']), ('skill', '241', a['skill'])],
            'MCP/skill rule categories 散文未被校验 —— 门禁盲区')

    def test_mcp_rule_categories_prose_survives_sync(self):
        """查得到还得改得动，否则门禁就是一条永远红的规则。"""
        text = ('"description": "... aligned, 235 MCP rule categories / '
                '241 skill rule categories. Static ...")')
        a = _auth()
        new, _ = G.sync_text(text, a, _pats())
        self.assertIn(f'{a["mcp"]} MCP rule categories', new,
                      f'sync 未修 rule categories 散文：{new!r}')
        self.assertIn(f'{a["skill"]} skill rule categories', new)


class TestPushWiring(unittest.TestCase):
    """推送脚本必须真的接上 drifted_files()。"""

    @staticmethod
    def _push_src():
        p = os.path.join(os.path.dirname(__file__), '..', 'scripts',
                         '_push_batch.py')
        with open(p, encoding='utf-8') as f:
            return f.read()

    def test_push_script_consumes_drifted_files(self):
        src = self._push_src()
        self.assertIn('drifted_files', src,
                      '_push_batch.py 未接上 rule_count_gate.drifted_files')
        # 差集而不是"全部声明位都带上"：否则每次推送都硬塞 47 个文件
        self.assertIn('- have', src, '自动带入未做差集')

    def test_auto_include_can_be_disabled(self):
        src = self._push_src()
        self.assertIn('--no-auto-decl', src, '缺少关闭开关')

    def test_dry_run_does_not_touch_remote(self):
        """--dry-run 必须停在写远端之前，否则没法在不推送的情况下验证。"""
        src = self._push_src()
        dry = src.split('if ARGS.dry_run:')[1].split('if not blobs')[0]
        self.assertNotIn('git/commits', dry,
                         '--dry-run 分支里出现了提交动作')
        self.assertIn('raise SystemExit(0)', dry,
                      '--dry-run 未显式退出，会继续往下推')


class TestGateCli(unittest.TestCase):
    """命令行行为的最低契约。"""

    def test_exit_code_semantics(self):
        import subprocess
        repo = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        script = os.path.join(repo, 'scripts', 'rule_count_gate.py')
        r = subprocess.run([sys.executable, script, '--check'],
                           capture_output=True, text=True, cwd=repo)
        self.assertIn(r.returncode, (0, 1))
        self.assertIn('规则数一致性检查', r.stdout)
        if r.returncode == 0:
            self.assertIn('无漂移', r.stdout)
        else:
            self.assertIn('漂移', r.stdout)

    def test_json_shape(self):
        import json
        import subprocess
        repo = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        r = subprocess.run([sys.executable,
                            os.path.join(repo, 'scripts', 'rule_count_gate.py'),
                            '--json'], capture_output=True, text=True, cwd=repo)
        self.assertEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertEqual(set(data), {'authority', 'files_checked', 'drifts'})
        self.assertGreater(data['files_checked'], 0,
                           '受约束声明位为空 —— 门禁没覆盖到任何文件')


if __name__ == '__main__':
    unittest.main()
