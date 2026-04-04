import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from common.trace_context import get_trace_id


# =====================================================================
# 🎨 核心升级：自定义 ANSI 颜色格式化引擎
# =====================================================================
class ColoredFormatter(logging.Formatter):
    """强制接管终端颜色，拒绝 IDE/终端 瞎猜"""
    # 定义终端 ANSI 颜色码
    RESET = "\x1b[0m"
    GREY = "\x1b[38;20m"
    GREEN = "\x1b[32;20m"
    BOLD_YELLOW = "\x1b[33;1m"
    BOLD_RED = "\x1b[31;1m"
    MAGENTA = "\x1b[35;1m"

    # 日志模版 (精确到毫秒)
    FORMAT_STR = "%(asctime)s.%(msecs)03d | %(levelname)-8s | [%(threadName)s] | [%(trace_id)s] | %(message)s"

    # 级别与颜色的映射字典
    FORMATS = {
        logging.DEBUG: GREY + FORMAT_STR + RESET,
        logging.INFO: RESET + FORMAT_STR + RESET,
        logging.WARNING: BOLD_YELLOW + FORMAT_STR + RESET,  # 警告黄
        logging.ERROR: BOLD_RED + FORMAT_STR + RESET,  # 致命红
        logging.CRITICAL: MAGENTA + FORMAT_STR + RESET
    }

    def format(self, record):
        # 获取当前上下文的trace_id并添加到record中
        trace_id = get_trace_id()
        record.trace_id = trace_id
        log_fmt = self.FORMATS.get(record.levelno, self.FORMAT_STR)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


def setup_logger():
    # 确保日志目录存在
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, 'aegis_gateway.log')

    # 1. 统一控制台输出 (全量走 stdout，带 ANSI 颜色)
    unified_console_handler = logging.StreamHandler(sys.stdout)
    unified_console_handler.setFormatter(ColoredFormatter())
    unified_console_handler.setLevel(logging.INFO)

    # 2. 文件落盘输出 (绝对不能带颜色码，否则写进 TXT 里全是乱码)
    class PlainFormatter(logging.Formatter):
        def format(self, record):
            # 获取当前上下文的trace_id并添加到record中
            trace_id = get_trace_id()
            record.trace_id = trace_id
            return super().format(record)
    
    plain_format = PlainFormatter(
        fmt='%(asctime)s.%(msecs)03d | %(levelname)-8s | [%(threadName)s] | [%(trace_id)s] | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setFormatter(plain_format)
    file_handler.setLevel(logging.INFO)

    # 3. 根日志配置
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 防止 Pytest 或多次实例化导致重复添加 handler
    if not root_logger.handlers:
        root_logger.addHandler(unified_console_handler)
        root_logger.addHandler(file_handler)

    return root_logger


# 暴露单例句柄
logger = setup_logger()