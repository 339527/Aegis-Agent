import pytest
import logging
from ai_core.agents import AgentDispatcher  # 注意根据你的实际目录微调

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


# 🎯 核心魔法：告诉 Pytest 这是一个异步测试用例！
@pytest.mark.asyncio
async def test_router_circuit_breaker():
    print("\n" + "=" * 50)
    print("🚀 Aegis-Agent V1.6 [智能路由与成本熔断] 极限压测启动")
    print("=" * 50 + "\n")

    # 1. 实例化核心中枢
    dispatcher = AgentDispatcher()

    # ==========================================
    # 🧪 测试用例 1：白嫖拦截 (闲聊降级)
    # ==========================================
    print(">>> 🟢 [阶段 1] 发起低价值闲聊请求...")
    res_mock = await dispatcher.process_task("你好，在吗？")
    print(f"   [前端收到响应]: {res_mock}\n")

    # ==========================================
    # 🧪 测试用例 2：模拟业务高峰，疯狂消耗 Token
    # ==========================================
    print(">>> 🟡 [阶段 2] 注入状态：修改路由器的账本，假装用掉了 48000 Token...")
    dispatcher.router.record_usage(48000)

    # 此时发正常业务，依然能通过
    res_normal = await dispatcher.process_task("帮我查询ID为133的用户")
    print(f"   [前端收到响应]: (大模型正常放行干活...)\n")

    # 假设查询耗费了 2500 Token
    dispatcher.router.record_usage(2500)

    # ==========================================
    # 🧪 测试用例 3：触发真理防线 (熔断器生效)
    # ==========================================
    print(">>> 🔴 [阶段 3] 预算已超 50000 阈值，发起高危请求...")
    # 此时必须熔断！
    res_meltdown = await dispatcher.process_task("立刻帮我分析日志！")
    print(f"   [前端收到响应]: {res_meltdown}")

    # 物理断言 (Assert)：用代码验证是不是真的返回了熔断提示
    assert "熔断" in res_meltdown, "❌ 糟糕，熔断器没生效！"

    print("\n🎯 压测完美通过：财务防线坚不可摧！")

# 删掉了原来的 if __name__ == "__main__" 块，全权交给 Pytest 接管