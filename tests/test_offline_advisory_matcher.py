"""Offline advisory CVE matcher — correctness + air-gap isolation tests.

These cases are SYNTHETIC and use packages/versions NOT present in the
evaluation corpus, so they validate the matcher's parsing and semver-range
logic independently of the benchmark (no "tuned to the test set").
"""
import unittest
from unittest import mock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanner.supply_chain import (
    parse_dependencies,
    version_in_range,
    compare_semver,
    scan_supply_chain,
    load_advisory_index,
)


class TestParseDependencies(unittest.TestCase):
    def test_go_require(self):
        out = parse_dependencies("require github.com/foo/bar v1.2.3\n")
        self.assertEqual(out[0]["package"], "github.com/foo/bar")
        self.assertEqual(out[0]["version"], "1.2.3")
        self.assertEqual(out[0]["ecosystem"], "go")

    def test_pip_double_eq(self):
        out = parse_dependencies("requirements: mylib==4.6.77\n")
        self.assertEqual(out[0]["package"], "mylib")
        self.assertEqual(out[0]["version"], "4.6.77")

    def test_npm_at(self):
        out = parse_dependencies('npx -y @scope/pkg@3.5.0-rc.0')
        self.assertEqual(out[0]["package"], "@scope/pkg")
        self.assertEqual(out[0]["version"], "3.5.0-rc.0")

    def test_maven_dependency(self):
        txt = ("<dependency>\n"
               "  <groupId>com.example</groupId>\n"
               "  <artifactId>widget</artifactId>\n"
               "  <version>2.2.0</version>\n</dependency>")
        out = parse_dependencies(txt)
        self.assertEqual(out[0]["package"], "com.example:widget")
        self.assertEqual(out[0]["version"], "2.2.0")

    def test_rust_cargo(self):
        out = parse_dependencies('russh = "0.63.0"\n')
        self.assertEqual(out[0]["package"], "russh")
        self.assertEqual(out[0]["version"], "0.63.0")

    def test_ruby_gem(self):
        out = parse_dependencies('gem "websocket-driver", "=0.8.1"\n')
        self.assertEqual(out[0]["package"], "websocket-driver")
        self.assertEqual(out[0]["version"], "0.8.1")

    def test_nuget(self):
        txt = ('<PackageReference Include="Microsoft.X" '
               'Version="9.0.1" />')
        out = parse_dependencies(txt)
        self.assertEqual(out[0]["package"], "Microsoft.X")
        self.assertEqual(out[0]["version"], "9.0.1")

    def test_composer(self):
        out = parse_dependencies('{"require": {"vendor/pkg": "8.7.0"}}')
        self.assertEqual(out[0]["package"], "vendor/pkg")
        self.assertEqual(out[0]["version"], "8.7.0")

    def test_no_declaration(self):
        self.assertEqual(parse_dependencies("just some plain text"), [])


class TestSemverCompare(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(compare_semver("1.2.3", "1.2.3"), 0)
        self.assertEqual(compare_semver("1.2.3", "1.2.4"), -1)
        self.assertEqual(compare_semver("2.0.0", "1.9.9"), 1)

    def test_partial(self):
        self.assertEqual(compare_semver("1.2", "1.2.0"), 0)

    def test_prerelease_lower(self):
        # 1.9.10 (release) > 1.9.10-0.2026... (prerelease)
        self.assertEqual(compare_semver("1.9.10", "1.9.10-0.20260703"), 1)
        self.assertEqual(
            compare_semver("1.9.10-0.20260703", "1.9.10-0.20260703"), 0)


class TestVersionInRange(unittest.TestCase):
    def test_range_and(self):
        self.assertTrue(version_in_range("0.144.0", ">= 0.144.0, < 0.147.0"))
        self.assertFalse(version_in_range("0.147.0", ">= 0.144.0, < 0.147.0"))
        self.assertFalse(version_in_range("0.143.9", ">= 0.144.0, < 0.147.0"))

    def test_lt_only(self):
        self.assertTrue(version_in_range("14.10.1", "< 14.10.2"))
        self.assertFalse(version_in_range("14.10.2", "< 14.10.2"))

    def test_pseudo_boundary_via_inclusive_flag(self):
        # strict: example equals the boundary -> excluded (standard semver)
        self.assertFalse(
            version_in_range("1.9.10-0.20260703131214",
                            "< 1.9.10-0.20260703131214", strict=True))
        # inclusive flag (used by the index builder normalization) -> captured
        self.assertTrue(
            version_in_range("1.9.10-0.20260703131214",
                            "<= 1.9.10-0.20260703131214", strict=True))

    def test_ge_le(self):
        self.assertTrue(version_in_range("2.3.0", ">= 2.2.0, <= 2.3.34"))
        self.assertFalse(version_in_range("2.4.0", ">= 2.2.0, <= 2.3.34"))


class TestScanSupplyChain(unittest.TestCase):
    INDEX = {
        "github.com/foo/bar": [{
            "cve": "CVE-2099-0001", "range": ">= 1.0.0, < 1.5.0",
            "severity": "high", "ecosystem": "go",
            "summary": "test", "ghsa": "GHSA-test",
        }],
        "safe-lib": [{
            "cve": "CVE-2099-0002", "range": "< 2.0.0",
            "severity": "critical", "ecosystem": "npm",
            "summary": "test", "ghsa": "GHSA-test2",
        }],
    }

    def test_detects_vulnerable(self):
        f = scan_supply_chain("require github.com/foo/bar v1.2.0",
                              index=self.INDEX)
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0]["cve"], "CVE-2099-0001")
        self.assertEqual(f[0]["severity"], "high")
        self.assertEqual(f[0]["owasp_category"], "MCP04")

    def test_no_false_positive_safe_version(self):
        f = scan_supply_chain("require github.com/foo/bar v1.9.0",
                              index=self.INDEX)
        self.assertEqual(f, [])

    def test_no_false_positive_unknown_package(self):
        f = scan_supply_chain("require not-in-index v9.9.9", index=self.INDEX)
        self.assertEqual(f, [])

    def test_critical_severity_preserved(self):
        f = scan_supply_chain("safe-lib@1.0.0", index=self.INDEX)
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0]["severity"], "critical")


class TestAirGap(unittest.TestCase):
    def test_no_network_on_scan(self):
        with mock.patch("urllib.request.urlopen",
                        side_effect=AssertionError("network used!")):
            f = scan_supply_chain("require github.com/foo/bar v1.2.0",
                                  index=TestScanSupplyChain.INDEX)
            self.assertEqual(len(f), 1)

    def test_load_index_local_file(self):
        with mock.patch("urllib.request.urlopen",
                        side_effect=AssertionError("network used!")):
            idx = load_advisory_index()
            self.assertIsInstance(idx, dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)
