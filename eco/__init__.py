"""
AIShield 生态核心模块包

子模块:
  - identity:        Agent身份 + DID + 信誉系统
  - payment:         支付网关 + 计费系统
  - badge:           安全徽章 + 认证API
  - marketplace:     工具市场API
  - a2a_gateway:     A2A协议Gateway（兼容Google A2A v1.0）
  - collab:          Agent协作通信总线（消息总线/会话/委派）
  - auth_provider:   增强身份认证（API Key/作用域/审计）

使用方式:
    from eco import identity, payment, badge, marketplace, a2a_gateway, collab, auth_provider
"""

from eco import identity
from eco import payment
from eco import badge
from eco import marketplace
from eco import a2a_gateway
from eco import collab
from eco import auth_provider

# NOTE: 公共JSON持久化工具已提取至 api.utils（load_json / save_json）
#       各子模块当前仍使用各自的私有实现（_load_json / _save_json），
#       后续可逐步替换为 from api.utils import load_json, save_json 以统一基础设施。

__all__ = [
    "identity",
    "payment",
    "badge",
    "marketplace",
    "a2a_gateway",
    "collab",
    "auth_provider",
]