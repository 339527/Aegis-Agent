import pytest
import asyncio
import time
from unittest.mock import patch, AsyncMock
from ai_core.agents import AgentDispatcher
from config.log_config import logger


@pytest.mark.asyncio
@patch('ai_core.agents.TaskExecutor.parse_intention')
async def test_concurrent_stress(mock_parse_intention):
    """验证高并发请求下，Dispatcher 是否能保持稳定"""
    # Mock 底层的模型调用，消除网络 I/O 耗时
    mock_parse_intention.return_value = ("NO_ACTION", "性能测试响应")
    
    dispatcher = AgentDispatcher()
    start_time = time.time()

    # 并发 5 个请求，验证异步调度能力
    tasks = [dispatcher.process_task(f"性能压测请求 {i}") for i in range(5)]
    results = await asyncio.gather(*tasks)

    duration = time.time() - start_time
    logger.info(f"🚀 并发压测完成，总耗时: {duration:.2f}s")
    
    # 验证结果数量
    assert len(results) == 5
    
    # 严格断言：总耗时必须小于 5 秒（验证异步调度能力）
    assert duration < 5, f"并发压测耗时 {duration:.2f}s 超过预期的 5s"
    
    # 验证 mock 被调用了正确的次数
    assert mock_parse_intention.call_count == 5