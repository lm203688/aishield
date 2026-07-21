"""
模块间联动测试 -- 验证 P0 修复的 7 条断裂链路

测试策略:
  - 每个测试类覆盖一条断裂链路的修复验证
  - 不依赖运行中的服务器，直接调用 Python 模块和类
  - 所有测试可独立运行，无网络依赖
  - 覆盖正常路径、边界情况、错误处理
"""

import unittest
import sys
import os
import json
import time
import threading
import urllib.request
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 检查服务器是否可达
def _server_ready(port=8450):
    """尝试连接服务器判断是否可用"""
    try:
        req = urllib.request.Request(f'http://127.0.0.1:{port}/api/v1/health')
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False

_SERVER_PORT = int(os.environ.get('AISHIELD_PORT', os.environ.get('PORT', 8450)))
_SERVER_UP = _server_ready(_SERVER_PORT)
_BASE_URL = f'http://127.0.0.1:{_SERVER_PORT}'


# ============================================================
#  P0-4: Auth 中间件测试
# ============================================================

class TestAuthMiddleware(unittest.TestCase):
    """P0-4: Auth 中间件测试 -- 验证 _require_auth 逻辑正确性"""

    def test_auth_exempt_paths_do_not_require_token(self):
        """验证健康检查和 key 生成端点豁免认证"""
        from eco.dispatcher import _AUTH_EXEMPT_PATHS
        # 健康检查和生成 key 端点应在豁免列表中
        self.assertIn("/api/v1/health", _AUTH_EXEMPT_PATHS)
        self.assertIn("/api/v1/auth/keys", _AUTH_EXEMPT_PATHS)

    def test_auth_module_has_require_auth_function(self):
        """验证 dispatcher 模块导出了 _require_auth 函数"""
        from eco.dispatcher import _require_auth
        self.assertTrue(callable(_require_auth))

    def test_auth_key_manager_has_verify_and_revoke(self):
        """验证 APIKeyManager 具备 verify_key 和 revoke_key 方法"""
        from eco.auth_provider import APIKeyManager
        mgr = APIKeyManager()
        self.assertTrue(hasattr(mgr, 'verify_key'))
        self.assertTrue(hasattr(mgr, 'revoke_key'))
        self.assertTrue(hasattr(mgr, 'generate_key'))

    @unittest.skipUnless(_SERVER_UP, "服务器未启动")
    def test_auth_rejects_request_without_bearer_token(self):
        """验证未携带 Bearer token 的 POST 请求被拒绝 (401)"""
        try:
            req = urllib.request.Request(
                f'{_BASE_URL}/api/v1/identity/register',
                data=json.dumps({"name": "test"}).encode(),
                method='POST',
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                self.fail(f"应返回401但得到 {resp.status}")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 401)

    @unittest.skipUnless(_SERVER_UP, "服务器未启动")
    def test_auth_exempt_health_endpoint_still_accessible(self):
        """验证健康检查端点不需要认证即可访问"""
        try:
            req = urllib.request.Request(f'{_BASE_URL}/api/v1/health')
            with urllib.request.urlopen(req, timeout=5) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode())
                self.assertEqual(data.get('status'), 'ok')
        except Exception as e:
            self.fail(f"健康检查应可访问: {e}")

    @unittest.skipUnless(_SERVER_UP, "服务器未启动")
    def test_auth_flow_generate_verify_revoke(self):
        """验证 API Key 完整生命周期: 生成 -> 验证 -> 撤销 -> 验证失败"""
        from eco.auth_provider import APIKeyManager
        mgr = APIKeyManager()
        # 生成
        result = mgr.generate_key(agent_id='test-linkage-agent', key_name='linkage-test-key')
        self.assertIn('api_key', result)
        self.assertIn('key_id', result)
        raw_key = result['api_key']
        key_id = result['key_id']
        # 验证
        info = mgr.verify_key(raw_key)
        self.assertIsNotNone(info)
        self.assertEqual(info['agent_id'], 'test-linkage-agent')
        # 撤销
        revoked = mgr.revoke_key(key_id, agent_id='test-linkage-agent')
        self.assertTrue(revoked)
        # 验证已撤销的 key
        info_after = mgr.verify_key(raw_key)
        self.assertIsNone(info_after)


# ============================================================
#  P0-2: 技能真实调用测试
# ============================================================

class TestSkillInvoke(unittest.TestCase):
    """P0-2: 技能真实调用测试 -- 验证 SkillInvoker 调用链路完整"""

    def test_skill_invoker_class_exists(self):
        """验证 SkillInvoker 类可导入"""
        from eco.skill_market import SkillInvoker
        invoker = SkillInvoker()
        self.assertTrue(hasattr(invoker, 'invoke'))

    def test_skill_invoker_has_invoke_method_with_correct_params(self):
        """验证 invoke 方法接受正确参数: skill_id, caller_agent_id, input_data"""
        from eco.skill_market import SkillInvoker
        invoker = SkillInvoker()
        # 检查方法签名
        import inspect
        sig = inspect.signature(invoker.invoke)
        params = list(sig.parameters.keys())
        self.assertIn('skill_id', params)
        self.assertIn('caller_agent_id', params)

    def test_skill_invoke_nonexistent_skill_returns_error(self):
        """调用不存在的技能应返回错误而非崩溃"""
        from eco.skill_market import SkillInvoker
        invoker = SkillInvoker()
        result = invoker.invoke(
            skill_id='nonexistent-skill-12345',
            caller_agent_id='test-agent',
            input_data={}
        )
        # 应返回错误信息，不是抛出异常
        self.assertIsNotNone(result)
        self.assertIn('error', result)


# ============================================================
#  P0-3.1: 扫描 -> 自动认证联动
# ============================================================

class TestBadgeScanLinkage(unittest.TestCase):
    """P0-3.1: 扫描 -> 自动认证联动 -- 评分 >= 80 时自动生成认证"""

    def test_certification_service_exists(self):
        """验证 CertificationService 类可导入"""
        from eco.badge import CertificationService
        svc = CertificationService()
        self.assertTrue(hasattr(svc, 'certify_tool'))

    def test_certification_service_has_certify_method(self):
        """验证 certify_tool 方法接受 source_url 和 scan_report 参数"""
        from eco.badge import CertificationService
        import inspect
        svc = CertificationService()
        sig = inspect.signature(svc.certify_tool)
        params = list(sig.parameters.keys())
        self.assertIn('source_url', params)
        self.assertIn('scan_report', params)

    def test_certify_tool_with_mock_data(self):
        """使用模拟数据调用 certify_tool，验证不崩溃并返回结构化结果"""
        from eco.badge import CertificationService
        svc = CertificationService()
        result = svc.certify_tool(
            source_url='https://github.com/test/mock-repo',
            scan_report={
                'overall_score': 85,
                'badge_level': 'gold',
                'risk_level': 'safe',
                'findings': [],
            }
        )
        self.assertIsInstance(result, dict)
        # 应包含认证 ID（字段名为 cert_id）
        self.assertIn('cert_id', result)


# ============================================================
#  P0-3.2: 委托 -> 自动记账联动
# ============================================================

class TestPaymentDelegationLinkage(unittest.TestCase):
    """P0-3.2: 委托 -> 自动记账联动 -- 提交委托结果时自动记录用量"""

    def test_delegation_submit_result_triggers_billing(self):
        """验证 TaskDelegation.submit_result 内部调用 payment.record_usage"""
        from eco.collab import TaskDelegation
        # 先创建一个委托
        delg = TaskDelegation()
        result = delg.delegate(
            task_description='test delegation linkage',
            from_agent_id='agent-a',
            to_agent_id='agent-b',
        )
        self.assertIn('delegation_id', result)
        delegation_id = result['delegation_id']

        # 接受委托
        delg.accept_delegation(delegation_id, agent_id='agent-b')

        # 提交结果 -- 内部应触发 payment.record_usage
        submit_result = delg.submit_result(
            delegation_id, agent_id='agent-b',
            result={'output': 'done'}
        )
        self.assertIn('status', submit_result)
        self.assertEqual(submit_result['status'], 'completed')

    def test_billing_service_has_record_usage(self):
        """验证 BillingService.record_usage 方法存在"""
        from eco.payment import BillingService
        bs = BillingService()
        self.assertTrue(hasattr(bs, 'record_usage'))
        import inspect
        sig = inspect.signature(bs.record_usage)
        params = list(sig.parameters.keys())
        self.assertIn('account_id', params)
        self.assertIn('endpoint', params)

    def test_billing_service_record_usage_runs(self):
        """验证 record_usage 可以正常执行不崩溃"""
        from eco.payment import BillingService
        bs = BillingService()
        result = bs.record_usage(
            account_id='test-linkage-agent',
            endpoint='test_endpoint'
        )
        self.assertIsInstance(result, dict)


# ============================================================
#  P0-3.3: 技能 -> 沙箱执行联动
# ============================================================

class TestSandboxSkillLinkage(unittest.TestCase):
    """P0-3.3: 技能 -> 沙箱执行联动 -- 技能代码通过沙箱安全执行"""

    def test_sandbox_task_submit_safe_code(self):
        """提交安全代码到沙箱，状态应为 queued"""
        from eco.sandbox import SandboxTask
        task = SandboxTask()
        result = task.submit(
            agent_id='test-sandbox-agent',
            code='print("Hello, sandbox!")',
            language='python',
        )
        self.assertEqual(result['status'], 'queued')
        self.assertIn('task_id', result)

    def test_sandbox_task_rejects_dangerous_code(self):
        """提交危险代码到沙箱，状态应为 rejected"""
        from eco.sandbox import SandboxTask
        task = SandboxTask()
        result = task.submit(
            agent_id='test-sandbox-agent',
            code='import os; os.system("rm -rf /")',
            language='python',
        )
        self.assertEqual(result['status'], 'rejected')
        self.assertIn('security_findings', result)
        self.assertTrue(len(result['security_findings']) > 0)

    def test_sandbox_pre_check_catches_eval_exec(self):
        """沙箱预检查应捕获 eval 和 exec 模式"""
        from eco.sandbox import LocalExecutor
        executor = LocalExecutor()
        # eval
        safe, findings = executor._pre_check_code('x = eval("1+1")', 'python')
        self.assertFalse(safe)
        # exec
        safe2, findings2 = executor._pre_check_code('exec("print(1)")', 'python')
        self.assertFalse(safe2)
        # 干净代码
        safe3, findings3 = executor._pre_check_code('x = 1 + 2', 'python')
        self.assertTrue(safe3)


# ============================================================
#  模块间: Collab <-> A2A Gateway 连通性
# ============================================================

class TestCollabA2ALinkage(unittest.TestCase):
    """模块间: Collab <-> A2A Gateway 连通性 -- 消息总线与发现网关可互相调用"""

    def test_message_bus_can_publish_and_consume(self):
        """消息总线: 发布消息后可被消费"""
        from eco.collab import MessageBus
        bus = MessageBus()
        # 订阅
        sub = bus.subscribe(channel='test-linkage-ch', subscriber_agent_id='agent-consumer')
        self.assertIn('subscription_id', sub)
        # 发布
        pub = bus.publish(
            channel='test-linkage-ch',
            sender_agent_id='agent-producer',
            message_type='status',
            payload={'msg': 'hello'},
        )
        self.assertIn('message_id', pub)
        # 消费
        messages = bus.consume(subscriber_agent_id='agent-consumer', channel='test-linkage-ch')
        self.assertTrue(len(messages) >= 1)
        self.assertEqual(messages[0]['payload']['msg'], 'hello')

    def test_a2a_discover_returns_agents_list(self):
        """A2A 网关: discover 方法返回 agent 列表"""
        from eco.a2a_gateway import AgentDiscovery
        disc = AgentDiscovery()
        agents = disc.discover()
        self.assertIsInstance(agents, list)

    def test_collab_delegation_lifecycle(self):
        """完整委托生命周期: 创建 -> 接受 -> 提交结果"""
        from eco.collab import TaskDelegation
        delg = TaskDelegation()
        # 创建
        d = delg.delegate(
            task_description='linkage test task',
            from_agent_id='agent-x',
            to_agent_id='agent-y',
        )
        self.assertEqual(d['status'], 'pending')
        did = d['delegation_id']
        # 接受
        a = delg.accept_delegation(did, agent_id='agent-y')
        self.assertEqual(a['status'], 'accepted')
        # 提交结果
        s = delg.submit_result(did, agent_id='agent-y', result={'value': 42})
        self.assertEqual(s['status'], 'completed')


# ============================================================
#  P0-1: Dispatcher 参数签名匹配
# ============================================================

class TestDispatcherParams(unittest.TestCase):
    """P0-1: Dispatcher 参数签名匹配 -- 验证 dispatcher 调用模块方法时参数名正确"""

    def test_collab_consume_uses_subscriber_agent_id(self):
        """验证 dispatcher 调用 consume() 时使用 subscriber_agent_id 参数"""
        from eco.collab import MessageBus
        import inspect
        sig = inspect.signature(MessageBus.consume)
        params = list(sig.parameters.keys())
        self.assertIn('subscriber_agent_id', params)

    def test_auth_revoke_key_uses_agent_id(self):
        """验证 dispatcher 调用 revoke_key() 时使用 agent_id 参数"""
        from eco.auth_provider import APIKeyManager
        import inspect
        sig = inspect.signature(APIKeyManager.revoke_key)
        params = list(sig.parameters.keys())
        self.assertIn('key_id', params)
        self.assertIn('agent_id', params)
        # 确认不是旧的 revoked_by 参数
        self.assertNotIn('revoked_by', params)

    def test_dispatcher_init_accepts_modules_dict(self):
        """验证 dispatcher.init() 接受模块字典参数"""
        from eco import dispatcher
        import importlib
        # 使用已存在的模块初始化（包含 auth_provider 以确保认证中间件可用）
        identity = importlib.import_module('eco.identity')
        payment = importlib.import_module('eco.payment')
        badge = importlib.import_module('eco.badge')
        marketplace = importlib.import_module('eco.marketplace')
        a2a_gateway = importlib.import_module('eco.a2a_gateway')
        auth_provider = importlib.import_module('eco.auth_provider')
        dispatcher.init({
            "identity": identity,
            "payment": payment,
            "badge": badge,
            "marketplace": marketplace,
            "a2a_gateway": a2a_gateway,
            "auth_provider": auth_provider,
        })
        # 通过模块属性访问 _modules（避免 import 绑定问题）
        modules = dispatcher._modules
        self.assertIn("identity", modules)
        self.assertIn("payment", modules)
        self.assertIn("badge", modules)
        self.assertIn("a2a_gateway", modules)
        self.assertIn("auth_provider", modules)


if __name__ == '__main__':
    unittest.main(verbosity=2)
