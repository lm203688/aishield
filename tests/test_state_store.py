"""
api/state_store 回归测试 —— H1 / S3 状态地基

钉死四条不变量：
  1. 原子写：写完不留 .tmp 残留，活文件始终完整。
  2. 缺失文件 → 返回 default（不抛）。
  3. 损坏文件 → 备份坏文件（.corrupt-<ts>）并自愈返回 default，绝不卡死服务。
  4. schema_version 不符 → 视为不兼容旧格式，返回 default（不静默加载坏/旧数据）。
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api import state_store as st  # noqa: E402


class TestStateStore(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.p = os.path.join(self.d, "x.json")

    def test_save_then_load_roundtrip(self):
        st.save_json(self.p, {"a": 1, "nested": [1, 2, 3]})
        self.assertEqual(st.load_json(self.p), {"a": 1, "nested": [1, 2, 3]})

    def test_no_tmp_leftover_after_write(self):
        st.save_json(self.p, {"k": "v"})
        leftovers = [f for f in os.listdir(self.d) if f.endswith(".tmp")]
        self.assertEqual(leftovers, [], "原子写不应留下 .tmp 残留")

    def test_load_missing_returns_default(self):
        self.assertEqual(
            st.load_json(os.path.join(self.d, "nope.json"), {"fallback": True}),
            {"fallback": True})

    def test_corrupt_file_self_heals(self):
        with open(self.p, "w", encoding="utf-8") as fh:
            fh.write("{ this is not valid json")
        self.assertEqual(st.load_json(self.p, {"recovered": True}),
                         {"recovered": True})
        backups = [f for f in os.listdir(self.d)
                   if f.startswith("x.json.corrupt-")]
        self.assertTrue(backups, "损坏文件应被备份为 .corrupt-<ts>")

    def test_schema_version_mismatch_returns_default(self):
        st.save_json(self.p, {"schema_version": "2", "v": 1})
        self.assertEqual(st.load_json(self.p, {}, schema_version="1"), {})

    def test_schema_version_match_returns_data(self):
        st.save_json(self.p, {"schema_version": "1", "v": 1})
        self.assertEqual(
            st.load_json(self.p, {}, schema_version="1"),
            {"schema_version": "1", "v": 1})


if __name__ == "__main__":
    unittest.main(verbosity=2)
