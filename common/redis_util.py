import os
import redis
import logging
from unittest.mock import MagicMock  # 企业级挡板神器

class RedisUtil:
    def __init__(self, host='localhost', port=6379, password='', db=0):
        # 🛡️ 核心：云端环境感知与物理拦截
        if os.getenv("RUN_ENV") == "ci":
            logging.info("☁️ [企业级挡板] CI环境检测到：已拦截真实 Redis 连接，启用 Mock 对象")
            self.r = MagicMock()
            # 【高级技巧】伪造 Redis 的返回值。当代码执行 self.r.get() 时，永远返回一个假的验证码
            self.r.get.return_value = '"12"'
            return

        # ============ 下面是本地真实的物理连接逻辑 ============
        try:
            # decode_responses=True 会自动把 Redis 返回的 byte 字节码解码成纯文本字符串
            self.r = redis.Redis(
                host=host,
                port=port,
                password=password,
                db=db,
                decode_responses=True
            )
            # ping 一下，测试是否真的连上了
            self.r.ping()
            logging.info(f"🟢 Redis 缓存直连成功 [{host}:{port}]")
        except Exception as e:
            logging.error(f"🔴 Redis 连接致命失败，请检查本地 Redis 是否启动: {e}")
            raise e

    def get_captcha_code(self, uuid):
        """黑科技：根据 UUID 从若依缓存中窃取验证码答案"""
        key = f"captcha_codes:{uuid}"
        code = self.r.get(key)

        if code:
            code = code.strip('"')
            return code
        else:
            logging.warning(f"⚠️ 未能在 Redis 中找到 key: {key} 的验证码！")
            return None

    def close(self):
        """用完即焚，关闭连接释放资源"""
        self.r.close()