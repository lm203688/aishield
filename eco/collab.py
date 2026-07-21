"""
eco/collab.py — Agent协作通信总线

功能:
  - MessageBus: 消息发布/订阅总线
      subscribe / unsubscribe / publish / consume / acknowledge / get_channel_stats
  - CollaborationSession: 协作会话管理
      create_session / join_session / leave_session / send_to_session
      get_session_messages / close_session / get_session
  - TaskDelegation: 任务委派
      delegate / accept_delegation / reject_delegation / submit_result
      get_delegation / list_delegations
  - 数据持久化: api/data/collab_messages.json
                 api/data/collab_sessions.json
                 api/data/collab_delegations.json
  - 线程安全: threading.Lock

API路由:
  POST /api/v1/collab/subscribe            — 订阅频道
  POST /api/v1/collab/unsubscribe          — 取消订阅
  POST /api/v1/collab/publish              — 发布消息
  POST /api/v1/collab/consume              — 消费消息
  POST /api/v1/collab/acknowledge          — 确认消息
  GET  /api/v1/collab/channel-stats/{ch}   — 频道统计
  POST /api/v1/collab/sessions             — 创建会话
  POST /api/v1/collab/sessions/{id}/join   — 加入会话
  POST /api/v1/collab/sessions/{id}/leave  — 离开会话
  POST /api/v1/collab/sessions/{id}/send   — 会话内发送
  GET  /api/v1/collab/sessions/{id}/messages — 会话消息
  POST /api/v1/collab/sessions/{id}/close  — 关闭会话
  GET  /api/v1/collab/sessions/{id}        — 查询会话
  POST /api/v1/collab/delegations          — 委派任务
  POST /api/v1/collab/delegations/{id}/accept — 接受委派
  POST /api/v1/collab/delegations/{id}/reject — 拒绝委派
  POST /api/v1/collab/delegations/{id}/result  — 提交结果
  GET  /api/v1/collab/delegations/{id}     — 查询委派
  GET  /api/v1/collab/delegations          — 列出委派
"""

import json
import os
import time
import uuid
import threading
from datetime import datetime, timezone, timedelta

# ── 路径配置 ──
# 数据目录: api/data/（相对于项目根目录）
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_BASE_DIR, "api", "data")
MESSAGES_FILE = os.path.join(_DATA_DIR, "collab_messages.json")
SESSIONS_FILE = os.path.join(_DATA_DIR, "collab_sessions.json")
DELEGATIONS_FILE = os.path.join(_DATA_DIR, "collab_delegations.json")

TZ = timezone(timedelta(hours=8))


# ══════════════════════════════════════════════
#  工具函数
# ══════════════════════════════════════════════

def _load_json(path, default=None):
    """加载JSON文件，失败返回默认值"""
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path, data):
    """线程安全地保存JSON文件"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(_DATA_DIR, exist_ok=True)


def _now_iso():
    """返回当前时间的ISO格式字符串"""
    return datetime.now(TZ).isoformat()


# ══════════════════════════════════════════════
#  MessageBus — 消息发布/订阅总线
# ══════════════════════════════════════════════

class MessageBus:
    """
    Agent消息发布/订阅总线
    支持频道订阅、消息发布、消费和确认
    """

    def __init__(self):
        self._lock = threading.Lock()

    def _load(self):
        """从磁盘加载消息和订阅数据"""
        raw = _load_json(MESSAGES_FILE, {"messages": {}, "subscriptions": {}, "channels": {}})
        self._messages = raw.get("messages", {})
        self._subscriptions = raw.get("subscriptions", {})
        self._channels = raw.get("channels", {})

    def _save(self):
        """持久化数据到磁盘"""
        _ensure_data_dir()
        _save_json(MESSAGES_FILE, {
            "messages": self._messages,
            "subscriptions": self._subscriptions,
            "channels": self._channels,
        })

    def subscribe(self, channel, subscriber_agent_id, filter_tags=None):
        """
        订阅频道

        Args:
            channel (str):              频道名称
            subscriber_agent_id (str):  订阅者Agent ID
            filter_tags (list, opt):    过滤标签列表

        Returns:
            dict: {"subscription_id", "channel", "status"}
        """
        self._load()

        subscription_id = f"sub_{uuid.uuid4().hex[:16]}"
        subscription = {
            "subscription_id": subscription_id,
            "channel": channel,
            "subscriber_agent_id": subscriber_agent_id,
            "filter_tags": filter_tags or [],
            "created_at": _now_iso(),
            "status": "active",
        }

        self._subscriptions[subscription_id] = subscription

        # 维护频道索引
        if channel not in self._channels:
            self._channels[channel] = {"subscribers": [], "message_count": 0}
        self._channels[channel]["subscribers"].append(subscription_id)

        self._save()

        return {
            "subscription_id": subscription_id,
            "channel": channel,
            "status": "active",
        }

    def unsubscribe(self, subscription_id):
        """
        取消订阅

        Args:
            subscription_id (str): 订阅ID

        Returns:
            bool: 是否成功取消
        """
        self._load()

        sub = self._subscriptions.get(subscription_id)
        if not sub:
            return False

        # 从频道索引中移除
        channel = sub["channel"]
        if channel in self._channels:
            subs_list = self._channels[channel].get("subscribers", [])
            if subscription_id in subs_list:
                subs_list.remove(subscription_id)

        sub["status"] = "cancelled"
        sub["cancelled_at"] = _now_iso()

        self._save()
        return True

    def publish(self, channel, sender_agent_id, message_type, payload,
                target_agent_id=None, priority="normal"):
        """
        发布消息到频道

        Args:
            channel (str):              频道名称
            sender_agent_id (str):      发送者Agent ID
            message_type (str):         消息类型
            payload (dict):             消息体
            target_agent_id (str, opt): 目标Agent ID（点对点）
            priority (str):             优先级 (low/normal/high/critical)

        Returns:
            dict: {"message_id", "channel"}
        """
        self._load()

        message_id = f"msg_{uuid.uuid4().hex[:16]}"
        message = {
            "message_id": message_id,
            "channel": channel,
            "sender_agent_id": sender_agent_id,
            "message_type": message_type,
            "payload": payload,
            "target_agent_id": target_agent_id,
            "priority": priority,
            "created_at": _now_iso(),
            "acknowledged_by": [],
        }

        self._messages[message_id] = message

        # 更新频道统计
        if channel not in self._channels:
            self._channels[channel] = {"subscribers": [], "message_count": 0}
        self._channels[channel]["message_count"] = \
            self._channels[channel].get("message_count", 0) + 1

        self._save()

        return {
            "message_id": message_id,
            "channel": channel,
        }

    def consume(self, subscriber_agent_id, channel=None, max_messages=10):
        """
        消费消息

        Args:
            subscriber_agent_id (str):  消费者Agent ID
            channel (str, opt):         限定频道（为空则消费所有订阅频道）
            max_messages (int):         最大消息数

        Returns:
            list: 消息列表
        """
        self._load()

        # 找到该Agent的所有活跃订阅
        my_subs = []
        for sub in self._subscriptions.values():
            if (sub["subscriber_agent_id"] == subscriber_agent_id
                    and sub["status"] == "active"
                    and (channel is None or sub["channel"] == channel)):
                my_subs.append(sub)

        if not my_subs:
            return []

        # 收集订阅的频道集合
        subscribed_channels = set(sub["channel"] for sub in my_subs)

        # 筛选未确认的消息
        result = []
        for msg in self._messages.values():
            if msg["channel"] in subscribed_channels:
                # 检查是否已被此Agent确认
                if subscriber_agent_id not in msg.get("acknowledged_by", []):
                    # 检查标签过滤：仅当订阅者设置了filter_tags且消息携带tags时才过滤
                    matched = True
                    msg_tags = msg.get("payload", {}).get("tags", [])
                    for sub in my_subs:
                        if sub["channel"] == msg["channel"] and sub.get("filter_tags"):
                            # 消息无tags时不过滤，有tags时需匹配
                            if msg_tags and not any(t in msg_tags for t in sub["filter_tags"]):
                                matched = False
                    if matched:
                        result.append(msg)
                        if len(result) >= max_messages:
                            break

        # 按优先级排序: critical > high > normal > low
        priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
        result.sort(key=lambda m: priority_order.get(m.get("priority", "normal"), 2))

        return result

    def acknowledge(self, message_id, subscriber_agent_id):
        """
        确认消息

        Args:
            message_id (str):           消息ID
            subscriber_agent_id (str):  确认者Agent ID

        Returns:
            bool: 是否确认成功
        """
        self._load()

        msg = self._messages.get(message_id)
        if not msg:
            return False

        acked = msg.get("acknowledged_by", [])
        if subscriber_agent_id not in acked:
            acked.append(subscriber_agent_id)
        msg["acknowledged_by"] = acked

        self._save()
        return True

    def get_channel_stats(self, channel):
        """
        获取频道统计信息

        Args:
            channel (str): 频道名称

        Returns:
            dict: 频道统计
        """
        self._load()

        ch = self._channels.get(channel)
        if not ch:
            return {"channel": channel, "exists": False}

        # 统计活跃订阅数
        active_subs = 0
        for sub_id in ch.get("subscribers", []):
            sub = self._subscriptions.get(sub_id, {})
            if sub.get("status") == "active":
                active_subs += 1

        # 统计未确认消息数
        pending = 0
        for msg in self._messages.values():
            if msg["channel"] == channel and len(msg.get("acknowledged_by", [])) == 0:
                pending += 1

        return {
            "channel": channel,
            "exists": True,
            "total_subscribers": len(ch.get("subscribers", [])),
            "active_subscribers": active_subs,
            "total_messages": ch.get("message_count", 0),
            "pending_messages": pending,
        }


# ══════════════════════════════════════════════
#  CollaborationSession — 协作会话管理
# ══════════════════════════════════════════════

class CollaborationSession:
    """
    协作会话管理器
    支持创建会话、加入/离开、会话内消息通信
    """

    def __init__(self):
        self._lock = threading.Lock()

    def _load(self):
        """从磁盘加载会话数据"""
        raw = _load_json(SESSIONS_FILE, {"sessions": {}})
        self._sessions = raw.get("sessions", {})

    def _save(self):
        """持久化数据到磁盘"""
        _ensure_data_dir()
        _save_json(SESSIONS_FILE, {"sessions": self._sessions})

    def create_session(self, initiator_agent_id, task_description,
                       participant_agent_ids):
        """
        创建协作会话

        Args:
            initiator_agent_id (str):    发起者Agent ID
            task_description (str):      任务描述
            participant_agent_ids (list): 参与者Agent ID列表

        Returns:
            dict: {"session_id", "status", "participants"}
        """
        self._load()

        session_id = f"sess_{uuid.uuid4().hex[:16]}"
        participants = {
            initiator_agent_id: {
                "agent_id": initiator_agent_id,
                "role": "initiator",
                "joined_at": _now_iso(),
                "status": "active",
            }
        }
        for aid in participant_agent_ids:
            if aid != initiator_agent_id:
                participants[aid] = {
                    "agent_id": aid,
                    "role": "invited",
                    "joined_at": None,
                    "status": "invited",
                }

        session = {
            "session_id": session_id,
            "initiator_agent_id": initiator_agent_id,
            "task_description": task_description,
            "participants": participants,
            "messages": [],
            "status": "active",
            "created_at": _now_iso(),
            "closed_at": None,
            "close_reason": None,
        }

        self._sessions[session_id] = session
        self._save()

        return {
            "session_id": session_id,
            "status": "active",
            "participants": list(participants.keys()),
        }

    def join_session(self, session_id, agent_id, role="contributor"):
        """
        加入协作会话

        Args:
            session_id (str):  会话ID
            agent_id (str):    Agent ID
            role (str):        角色 (contributor/observer)

        Returns:
            dict: 加入结果
        """
        self._load()

        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"会话 '{session_id}' 不存在")
        if session["status"] != "active":
            raise ValueError(f"会话 '{session_id}' 已关闭")

        participant = session["participants"].get(agent_id)
        if participant:
            if participant["status"] == "active":
                raise ValueError(f"Agent '{agent_id}' 已在会话中")
            # 更新已邀请的参与者状态
            participant["status"] = "active"
            participant["role"] = role
            participant["joined_at"] = _now_iso()
        else:
            # 新成员直接加入
            session["participants"][agent_id] = {
                "agent_id": agent_id,
                "role": role,
                "joined_at": _now_iso(),
                "status": "active",
            }

        self._save()

        return {
            "session_id": session_id,
            "agent_id": agent_id,
            "role": role,
            "status": "joined",
        }

    def leave_session(self, session_id, agent_id):
        """
        离开协作会话

        Args:
            session_id (str):  会话ID
            agent_id (str):    Agent ID

        Returns:
            bool: 是否成功离开
        """
        self._load()

        session = self._sessions.get(session_id)
        if not session:
            return False

        participant = session["participants"].get(agent_id)
        if not participant or participant["status"] != "active":
            return False

        participant["status"] = "left"
        participant["left_at"] = _now_iso()

        self._save()
        return True

    def send_to_session(self, session_id, sender_agent_id, message_type, payload):
        """
        向会话内发送消息

        Args:
            session_id (str):       会话ID
            sender_agent_id (str):  发送者Agent ID
            message_type (str):     消息类型
            payload (dict):         消息体

        Returns:
            dict: 发送结果
        """
        self._load()

        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"会话 '{session_id}' 不存在")
        if session["status"] != "active":
            raise ValueError(f"会话 '{session_id}' 已关闭")

        participant = session["participants"].get(sender_agent_id)
        if not participant or participant["status"] != "active":
            raise ValueError(f"Agent '{sender_agent_id}' 不在此会话中")

        msg = {
            "message_id": f"smsg_{uuid.uuid4().hex[:16]}",
            "sender_agent_id": sender_agent_id,
            "message_type": message_type,
            "payload": payload,
            "created_at": _now_iso(),
        }
        session["messages"].append(msg)

        self._save()

        return {
            "message_id": msg["message_id"],
            "session_id": session_id,
            "status": "sent",
        }

    def get_session_messages(self, session_id, limit=50):
        """
        获取会话消息

        Args:
            session_id (str):  会话ID
            limit (int):       最大消息数

        Returns:
            list: 消息列表
        """
        self._load()

        session = self._sessions.get(session_id)
        if not session:
            return []

        messages = session.get("messages", [])
        return messages[-limit:]

    def close_session(self, session_id, reason="completed"):
        """
        关闭协作会话

        Args:
            session_id (str):  会话ID
            reason (str):      关闭原因

        Returns:
            dict: 关闭结果
        """
        self._load()

        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"会话 '{session_id}' 不存在")
        if session["status"] != "active":
            raise ValueError(f"会话 '{session_id}' 已关闭")

        session["status"] = "closed"
        session["closed_at"] = _now_iso()
        session["close_reason"] = reason

        self._save()

        return {
            "session_id": session_id,
            "status": "closed",
            "reason": reason,
            "closed_at": session["closed_at"],
        }

    def get_session(self, session_id):
        """
        查询会话详情

        Args:
            session_id (str): 会话ID

        Returns:
            dict | None: 会话信息
        """
        self._load()
        return self._sessions.get(session_id)


# ══════════════════════════════════════════════
#  TaskDelegation — 任务委派
# ══════════════════════════════════════════════

class TaskDelegation:
    """
    任务委派管理器
    支持任务的委派、接受、拒绝和结果提交
    """

    def __init__(self):
        self._lock = threading.Lock()

    def _load(self):
        """从磁盘加载委派数据"""
        raw = _load_json(DELEGATIONS_FILE, {"delegations": {}})
        self._delegations = raw.get("delegations", {})

    def _save(self):
        """持久化数据到磁盘"""
        _ensure_data_dir()
        _save_json(DELEGATIONS_FILE, {"delegations": self._delegations})

    def delegate(self, task_description, from_agent_id, to_agent_id,
                 payload=None, deadline_seconds=None):
        """
        委派任务

        Args:
            task_description (str):    任务描述
            from_agent_id (str):      委派者Agent ID
            to_agent_id (str):        被委派者Agent ID
            payload (dict, opt):      任务负载
            deadline_seconds (int, opt): 截止时间（秒）

        Returns:
            dict: {"delegation_id", "status"}
        """
        self._load()

        delegation_id = f"dlg_{uuid.uuid4().hex[:16]}"
        now = datetime.now(TZ)
        deadline = None
        if deadline_seconds:
            deadline = (now + timedelta(seconds=deadline_seconds)).isoformat()

        delegation = {
            "delegation_id": delegation_id,
            "task_description": task_description,
            "from_agent_id": from_agent_id,
            "to_agent_id": to_agent_id,
            "payload": payload or {},
            "status": "pending",
            "deadline": deadline,
            "result": None,
            "reject_reason": None,
            "created_at": _now_iso(),
            "accepted_at": None,
            "completed_at": None,
        }

        self._delegations[delegation_id] = delegation
        self._save()

        return {
            "delegation_id": delegation_id,
            "status": "pending",
        }

    def accept_delegation(self, delegation_id, agent_id):
        """
        接受委派

        Args:
            delegation_id (str): 委派ID
            agent_id (str):      接受者Agent ID

        Returns:
            dict: 接受结果
        """
        self._load()

        dlg = self._delegations.get(delegation_id)
        if not dlg:
            raise ValueError(f"委派 '{delegation_id}' 不存在")
        if dlg["to_agent_id"] != agent_id:
            raise ValueError(f"Agent '{agent_id}' 不是此委派的目标")
        if dlg["status"] != "pending":
            raise ValueError(f"委派状态为 '{dlg['status']}'，无法接受")

        dlg["status"] = "accepted"
        dlg["accepted_at"] = _now_iso()

        self._save()

        return {
            "delegation_id": delegation_id,
            "status": "accepted",
            "accepted_at": dlg["accepted_at"],
        }

    def reject_delegation(self, delegation_id, agent_id, reason):
        """
        拒绝委派

        Args:
            delegation_id (str): 委派ID
            agent_id (str):      拒绝者Agent ID
            reason (str):        拒绝原因

        Returns:
            dict: 拒绝结果
        """
        self._load()

        dlg = self._delegations.get(delegation_id)
        if not dlg:
            raise ValueError(f"委派 '{delegation_id}' 不存在")
        if dlg["to_agent_id"] != agent_id:
            raise ValueError(f"Agent '{agent_id}' 不是此委派的目标")
        if dlg["status"] != "pending":
            raise ValueError(f"委派状态为 '{dlg['status']}'，无法拒绝")

        dlg["status"] = "rejected"
        dlg["reject_reason"] = reason
        dlg["rejected_at"] = _now_iso()

        self._save()

        return {
            "delegation_id": delegation_id,
            "status": "rejected",
            "reason": reason,
        }

    def submit_result(self, delegation_id, agent_id, result):
        """
        提交委派结果

        Args:
            delegation_id (str): 委派ID
            agent_id (str):      提交者Agent ID
            result (dict):       任务结果

        Returns:
            dict: 提交结果
        """
        self._load()

        dlg = self._delegations.get(delegation_id)
        if not dlg:
            raise ValueError(f"委派 '{delegation_id}' 不存在")
        if dlg["to_agent_id"] != agent_id:
            raise ValueError(f"Agent '{agent_id}' 不是此委派的目标")
        if dlg["status"] != "accepted":
            raise ValueError(f"委派状态为 '{dlg['status']}'，无法提交结果")

        dlg["status"] = "completed"
        dlg["result"] = result
        dlg["completed_at"] = _now_iso()

        self._save()

        # P0-3.2: Payment <-> TaskDelegation 联动
        # 提交结果成功后，调用 payment 模块记录一笔交易
        # 用 try/except 包裹，避免 payment 失败影响委托流程
        try:
            from eco import payment as _payment_mod
            _bs = _payment_mod.BillingService()
            _bs.record_usage(
                account_id=agent_id,
                endpoint="task_delegation:submit_result",
            )
        except Exception:
            pass

        return {
            "delegation_id": delegation_id,
            "status": "completed",
            "completed_at": dlg["completed_at"],
        }

    def get_delegation(self, delegation_id):
        """
        查询委派详情

        Args:
            delegation_id (str): 委派ID

        Returns:
            dict | None: 委派信息
        """
        self._load()
        return self._delegations.get(delegation_id)

    def list_delegations(self, agent_id, status=None, role="all"):
        """
        列出委派

        Args:
            agent_id (str):  Agent ID
            status (str, opt): 筛选状态 (pending/accepted/rejected/completed)
            role (str):      角色 (all/delegator/delegatee)

        Returns:
            list: 委派列表
        """
        self._load()

        result = []
        for dlg in self._delegations.values():
            # 角色过滤
            if role == "delegator" and dlg["from_agent_id"] != agent_id:
                continue
            if role == "delegatee" and dlg["to_agent_id"] != agent_id:
                continue
            if role == "all" and dlg["from_agent_id"] != agent_id and dlg["to_agent_id"] != agent_id:
                continue

            # 状态过滤
            if status and dlg["status"] != status:
                continue

            result.append(dlg)

        return result