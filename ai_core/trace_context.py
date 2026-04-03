import contextvars
import uuid
from typing import Optional

# 创建ContextVar来存储trace_id
trace_id_var = contextvars.ContextVar('trace_id', default=None)


def get_trace_id() -> str:
    """获取当前上下文的trace_id，如果不存在则生成新的"""
    trace_id = trace_id_var.get()
    if trace_id is None:
        trace_id = f"REQ-{uuid.uuid4().hex[:8]}"
        trace_id_var.set(trace_id)
    return trace_id


def set_trace_id(trace_id: str) -> None:
    """设置当前上下文的trace_id"""
    trace_id_var.set(trace_id)


def clear_trace_id() -> None:
    """清除当前上下文的trace_id"""
    trace_id_var.set(None)
