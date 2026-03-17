# common/redis_util.py
import redis
import logging


class RedisUtil:
    def __init__(self, host='localhost', port=6379, password='', db=0):
        try:
            # 【核心知识点】：decode_responses=True 会自动把 Redis 返回的 byte 字节码解码成纯文本字符串
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

        # 若依源码中定义的 Redis Key 前缀就是 'captcha_codes:'
        key = f"captcha_codes:{uuid}"

        # 直接读取答案
        code = self.r.get(key)

        if code:
            # 若依的数学算术题结果，在 Redis 里存的可能是带双引号的，比如 "12"
            # 我们用 strip 把它剥干净，只保留纯数字或字母
            code = code.strip('"')
            return code
        else:
            logging.warning(f"⚠️ 未能在 Redis 中找到 key: {key} 的验证码！")
            return None

    def close(self):
        """用完即焚，关闭连接释放资源"""
        self.r.close()