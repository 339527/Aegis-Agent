import os
import logging
from logging.handlers import TimedRotatingFileHandler


def setup_logger():
    # 1. 自动创建日志目录（防止第一次运行报错）
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, 'aegis_gateway.log')

    # 2. 核心：大厂日志格式（时间 + 级别 + 线程/协程 + 咱们刚写的 TraceID 所在的 message）
    log_format = logging.Formatter(
        fmt='%(asctime)s.%(msecs)03d | %(levelname)-8s | [%(threadName)s] | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 3. 拦截器一：控制台输出（开发调试用，有颜色最好，这里用基础的）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)

    # 4. 拦截器二：文件输出（生产环境查 Bug 救命用）
    # TimedRotatingFileHandler: 每天午夜自动把旧日志打包备份（比如 aegis_gateway.log.2026-03-24），保留最近 30 天
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',  # 每天午夜切割
        interval=1,  # 间隔 1 天
        backupCount=30,  # 只保留最近 30 天日志，防止把服务器硬盘撑爆
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)

    # 5. 获取根日志记录器，清空默认 handler，挂载我们自己的
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 防止重复添加 handler 导致日志打两遍
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


# 暴露出初始化方法
logger = setup_logger()