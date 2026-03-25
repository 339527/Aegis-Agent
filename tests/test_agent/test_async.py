import asyncio
import time
import pytest


# 模拟大模型极度缓慢的 API 响应（固定 3 秒）
async def mock_ai_audit_task(task_id):
    print(f"🕒 [任务 {task_id}] 蓝队保安开始请求大模型，预计耗时 3 秒...")
    await asyncio.sleep(3)  # 模拟网络 I/O 挂起，交出 CPU 控制权
    print(f"✅ [任务 {task_id}] 审核完毕，放行！")
    return True


@pytest.mark.asyncio
async def test_agent_concurrent_audits():
    print("\n" + "=" * 50)
    print("🚀 启动 Aegis-Agent V2.5 并发压力测试 (Pytest 架构版)...")

    start_time = time.time()

    # 模拟 10 个红队 Agent 同时发起高危调用
    tasks = [mock_ai_audit_task(i) for i in range(1, 11)]

    # asyncio.gather 核心发力：瞬间将 10 个请求并发甩出去
    await asyncio.gather(*tasks)

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\n🏁 压测结束！并发处理 10 个请求，总耗时: {total_time:.2f} 秒")
    print("=" * 50 + "\n")

    # 🛑 架构师的物理断言：
    # 如果是同步阻塞（串行），耗时会是 10 * 3 = 30秒
    # 如果是真正的异步高并发，耗时应该无限接近 3 秒
    assert total_time < 4.0, f"❌ 糟糕！耗时高达 {total_time} 秒，你的系统退化成了串行阻塞！"