import pytest
import requests
import os
import logging
from api.auth_api import AuthApi
from common.redis_util import RedisUtil
from config.env_config import Config


@pytest.fixture(scope="session")
def session(base_url):
    s = requests.Session()
    logging.info(f"\n--- 🚀 若依自动化演练启动：{base_url} ---")

    if os.getenv("RUN_ENV") == "ci":
        # ================== CI 通道：绝对隔离 ==================
        logging.info("☁️ [CI 模式] 注入虚拟 Token，跳过真实登录")
        s.headers.update({"Authorization": "Bearer mock-token-123456"})
        yield s
        # 🌟 这里的 yield 之后不会执行后续的登录语句
    else:
        # ================== 本地通道：实战演练 ==================
        auth_api = AuthApi(s, base_url)
        uuid = auth_api.get_captcha_uuid()

        redis_db = RedisUtil(**Config.REDIS_CONFIG)
        real_code = redis_db.get_captcha_code(uuid)
        redis_db.close()

        user = Config.ADMIN_USER
        res_login = auth_api.login(user['username'], user['password'], real_code or "12", uuid)

        if res_login.status_code == 200:
            token = res_login.json().get("token")
            s.headers.update({"Authorization": f"Bearer {token}"})
            logging.info("✅ 本地登录成功")

        yield s