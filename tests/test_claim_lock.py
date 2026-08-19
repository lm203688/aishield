"""
tests/test_claim_lock.py — TaskDelegation 任务原子锁（Cumora 式 atomic claim）

覆盖:
  - 同一 from_agent_id + task_key 已有 active 委派 → 重复委派 fail-closed 拒绝
  - 不同 task_key → 允许
  - 默认 task_key=None → 不锁（向后兼容，允许重复）
  - 不同 from_agent_id 同 task_key → 不冲突（锁仅限同一委派方）
  - active 集合含 awaiting_approval / pending / accepted，均视为占用
  - 委派完成后（completed）锁释放，可重新委派同 task_key
"""

import unittest
import uuid

from eco import collab


def _uid(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class ClaimLockTest(unittest.TestCase):

    def test_duplicate_task_key_rejected(self):
        td = collab.TaskDelegation()
        frm = _uid("from")
        key = _uid("task")
        r1 = td.delegate(task_description="do X", from_agent_id=frm,
                         to_agent_id="agentB", task_key=key)
        self.assertEqual(r1["status"], "pending")
        with self.assertRaises(ValueError):
            td.delegate(task_description="do X again", from_agent_id=frm,
                        to_agent_id="agentC", task_key=key)

    def test_different_task_key_allowed(self):
        td = collab.TaskDelegation()
        frm = _uid("from")
        r1 = td.delegate(task_description="do X", from_agent_id=frm,
                         to_agent_id="agentB", task_key=_uid("k1"))
        r2 = td.delegate(task_description="do X", from_agent_id=frm,
                         to_agent_id="agentC", task_key=_uid("k2"))
        self.assertEqual(r1["status"], "pending")
        self.assertEqual(r2["status"], "pending")

    def test_default_no_lock_backward_compat(self):
        td = collab.TaskDelegation()
        frm = _uid("from")
        r1 = td.delegate(task_description="do X", from_agent_id=frm,
                         to_agent_id="agentB")
        r2 = td.delegate(task_description="do X", from_agent_id=frm,
                         to_agent_id="agentC")
        self.assertEqual(r1["status"], "pending")
        self.assertEqual(r2["status"], "pending")

    def test_cross_from_agent_no_conflict(self):
        td = collab.TaskDelegation()
        key = _uid("task")
        r1 = td.delegate(task_description="do X", from_agent_id=_uid("from1"),
                         to_agent_id="agentB", task_key=key)
        r2 = td.delegate(task_description="do X", from_agent_id=_uid("from2"),
                         to_agent_id="agentC", task_key=key)
        self.assertEqual(r1["status"], "pending")
        self.assertEqual(r2["status"], "pending")

    def test_lock_holds_in_awaiting_approval(self):
        td = collab.TaskDelegation()
        frm = _uid("from")
        key = _uid("task")
        r1 = td.delegate(task_description="do X", from_agent_id=frm,
                         to_agent_id="agentB", require_human_approval=True,
                         task_key=key)
        self.assertEqual(r1["status"], "awaiting_approval")
        with self.assertRaises(ValueError):
            td.delegate(task_description="do X", from_agent_id=frm,
                        to_agent_id="agentC", task_key=key)

    def test_lock_released_after_completion(self):
        td = collab.TaskDelegation()
        frm = _uid("from")
        key = _uid("task")
        r1 = td.delegate(task_description="do X", from_agent_id=frm,
                         to_agent_id="agentB", task_key=key)
        td.accept_delegation(r1["delegation_id"], "agentB")
        td.submit_result(r1["delegation_id"], "agentB", {"ok": True})
        # 完成后锁释放，可重新委派同 task_key
        r2 = td.delegate(task_description="do X again", from_agent_id=frm,
                         to_agent_id="agentC", task_key=key)
        self.assertEqual(r2["status"], "pending")

    def test_task_key_recorded(self):
        td = collab.TaskDelegation()
        frm = _uid("from")
        key = _uid("task")
        r1 = td.delegate(task_description="do X", from_agent_id=frm,
                         to_agent_id="agentB", task_key=key)
        d = td.get_delegation(r1["delegation_id"])
        self.assertEqual(d["task_key"], key)


if __name__ == "__main__":
    unittest.main()
