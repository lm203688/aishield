# -*- coding: utf-8 -*-
"""#2 沙箱硬化规则包测试：SANDBOX_RULES 必须检出逃逸原语、对良性配置零误报。"""
import os
import re
import sys
import tempfile
import shutil
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scanner.rules as rules
from scanner.rules import SANDBOX_RULES, ALL_RULES, get_rule_count


class TestSandboxRulesStructure(unittest.TestCase):
    def test_loaded_and_in_all(self):
        self.assertTrue(len(SANDBOX_RULES) >= 10)
        for pat in SANDBOX_RULES:
            self.assertIn(pat, ALL_RULES, "SANDBOX_RULES 必须并入 ALL_RULES")

    def test_category_mapping(self):
        self.assertEqual(rules.get_owasp_category_rules("SANDBOX"), len(SANDBOX_RULES))

    def test_all_patterns_compile(self):
        for pat in SANDBOX_RULES:
            try:
                re.compile(pat)
            except re.error as e:
                self.fail(f"正则无法编译: {pat} -> {e}")

    def test_not_overbroad(self):
        # 与晋升闸门同款不变量：空串/单字符串不得误吞
        for pat in SANDBOX_RULES:
            rx = re.compile(pat)
            self.assertIsNone(rx.search(""), "空串不应匹配")
            self.assertIsNone(rx.search("a"), "单字符不应匹配")

    def test_rule_count_grew(self):
        # SANDBOX 接入后 MCP 规则数应明显 > 200
        self.assertGreater(get_rule_count("mcp"), 210)


class TestSandboxRulesMalicious(unittest.TestCase):
    """这些真实世界逃逸配置必须被 SANDBOX_RULES 命中。"""
    MALICIOUS = [
        # Docker socket 挂载
        "docker run -v /var/run/docker.sock:/var/run/docker.sock myagent",
        # 特权容器（flag）
        "docker run --privileged --rm evil/agent",
        # compose 特权
        "services:\n  agent:\n    image: x\n    privileged: true",
        # host 网络
        "docker run --network host scanme",
        "services:\n  s:\n    network_mode: host",
        # host pid / ipc
        "docker run --pid=host busybox",
        "docker run --ipc=host busybox",
        # 全能力
        "docker run --cap-add=ALL pwn",
        "cap_add:\n  - ALL",
        "CAP_SYS_ADMIN needed here",
        # 关闭 seccomp
        "docker run --security-opt seccomp:unconfined x",
        # root 运行
        "docker run --user 0 ubuntu",
        # k8s 宿主命名空间
        "hostNetwork: true\nhostPID: true",
        "spec:\n  hostIPC: true",
        # k8s hostPath
        "volumes:\n  - name: h\n    hostPath:\n      path: /",
    ]

    def test_each_malicious_hits(self):
        for sample in self.MALICIOUS:
            hits = [desc for pat, (desc, sev) in SANDBOX_RULES.items()
                    if re.search(pat, sample)]
            self.assertTrue(hits, f"未检出逃逸配置: {sample[:50]!r} -> {hits}")


class TestSandboxRulesBenign(unittest.TestCase):
    """良性 Dockerfile / compose / k8s 必须零误报。"""
    BENIGN = [
        # 常规 Dockerfile
        "FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nEXPOSE 8000\nCMD [\"python\",\"app.py\"]",
        # 普通 compose
        "services:\n  web:\n    image: nginx:alpine\n    ports:\n      - \"80:80\"\n  db:\n    image: postgres:16\n    environment:\n      POSTGRES_PASSWORD: example",
        # 普通 k8s deployment
        "apiVersion: apps/v1\nkind: Deployment\nspec:\n  replicas: 3\n  template:\n    spec:\n      containers:\n        - name: api\n          image: myapi:1.2.3\n          ports:\n            - containerPort: 8080",
        # 普通 docker run
        "docker run -d -p 3000:3000 myapp:latest",
        # 一句普通说明
        "我们把宿主目录挂载到了容器里做开发",
        # 含 user 但非 root 特权
        "services:\n  app:\n    image: x\n    user: \"1000:1000\"",
    ]

    def test_benign_zero_fp(self):
        for sample in self.BENIGN:
            hits = [desc for pat, (desc, sev) in SANDBOX_RULES.items()
                    if re.search(pat, sample)]
            self.assertEqual(hits, [], f"良性样本误报: {sample[:40]!r} -> {hits}")


class TestSandboxRulesIntegration(unittest.TestCase):
    """经真实引擎 analyze() 验证：逃逸配置产出 critical 级 finding。"""
    def _scan_text(self, text):
        files = {"Dockerfile": text}
        rep = rules.analyze(files, tool_type="mcp")
        return rep.get("findings", [])

    def test_privileged_detected_via_engine(self):
        findings = self._scan_text("docker run --privileged --rm evil/agent")
        descs = [f.get("description") for f in findings]
        self.assertTrue(any("特权" in d for d in descs), f"引擎未检出特权: {descs}")

    def test_benign_dockerfile_clean(self):
        df = "FROM python:3.11-slim\nWORKDIR /app\nRUN pip install flask\nCMD [\"python\"]"
        findings = self._scan_text(df)
        sandbox_hits = [f for f in findings
                        if f.get("owasp_category") == "SANDBOX" or
                        any(k in (f.get("description") or "") for k in ("特权", "Docker socket", "host", "CAP_", "unconfined", "hostPath"))]
        self.assertEqual(sandbox_hits, [], f"良性 Dockerfile 误报: {sandbox_hits}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
