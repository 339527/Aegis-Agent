import pytest
import asyncio
import time
from unittest.mock import patch, AsyncMock
from ai_core.agents import AgentDispatcher, agent_tool
from config.log_config import logger


@agent_tool(risk_level="LOW")
async def async_sleep_tool(sleep_time=1):
    """异步休眠工具，用于模拟处理时间"""
    await asyncio.sleep(sleep_time)
    return f"异步休眠 {sleep_time} 秒完成"


@pytest.mark.asyncio
@patch('ai_core.agents.TaskExecutor.parse_intention')
@patch('ai_core.agents.AgentDispatcher.async_audit')
async def test_concurrent_stress_with_async_sleep(mock_async_audit, mock_parse_intention):
    """验证高并发请求下，Dispatcher 是否能保持稳定（带异步休眠）"""
    # Mock 意图解析，直接返回工具调用结果
    mock_parse_intention.return_value = ("async_sleep_tool", {"sleep_time": 1})
    # Mock 安全审计，直接返回安全结果
    mock_async_audit.return_value = {"is_safe": True, "risk_analysis": "[PASS] 安全"}
    
    dispatcher = AgentDispatcher()
    start_time = time.time()
    
    # 创建工具映射
    func_map = {"async_sleep_tool": async_sleep_tool}
    
    # 并发 5 个请求，每个请求调用异步休眠工具
    tasks = []
    for i in range(5):
        prompt = f"性能测试请求 {i}"
        tasks.append(dispatcher.process_task(prompt, function_map=func_map))
    
    logger.info("开始并发压测，5个请求同时执行...")
    results = await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    logger.info(f"并发压测完成，总耗时: {duration:.2f}s")
    logger.info(f"执行结果: {results}")
    
    # 验证结果数量
    assert len(results) == 5
    
    # 验证异步特性：如果是真正的异步执行，5个并发任务的总耗时应该接近1秒（而不是5秒）
    assert 0.9 <= duration <= 1.5, f"并发压测耗时 {duration:.2f}s 不符合异步预期（应该接近1秒）"
    
    # 验证每个任务都成功执行
    for i, result in enumerate(results):
        assert "异步休眠 1 秒完成" in str(result), f"第 {i+1} 个任务执行失败: {result}"
    
    # 验证 mock 被调用了正确的次数
    assert mock_parse_intention.call_count == 5
    assert mock_async_audit.call_count == 5
    
    logger.info("并发测试通过，异步调度正常工作！")