import pytest
import requests
import logging
import os
from config.env_config import Config
from api.auth_api import AuthApi
from common.redis_util import RedisUtil


@pytest.fixture(scope="session")
def base_url():
    return Config.get_base_url()


@pytest.fixture(scope="session")
def session(base_url):
    logging.info(f"\n--- 🚀 若依自动化攻防演练启动：连接 {base_url} ---")
    s = requests.Session()
    auth_api = AuthApi(s, base_url)

    # 🌟 V1.3.5 核心防御：完全隔断 CI 环境对 Redis 的物理依赖
    if os.getenv("RUN_ENV") == "ci":
        logging.info("☁️ [CI 模式] 直接使用伪造的验证码凭证")
        # 🌟 在 CI 模式下，我们直接手动给 session 塞入一个假 Token，跳过真实登录接口
        s.headers.update({"Authorization": "Bearer mock-token-ci-123456"})
        yield s
    else:
        # 本地真实执行逻辑
        uuid = auth_api.get_captcha_uuid()
        redis_db = RedisUtil(host=Config.REDIS_CONFIG["host"], port=Config.REDIS_CONFIG["port"],
                             password=Config.REDIS_CONFIG["password"], db=Config.REDIS_CONFIG["db"])
        real_code = redis_db.get_captcha_code(uuid)
        if not real_code:
            real_code = "12"
        redis_db.close()

    user = Config.ADMIN_USER
    res_login = auth_api.login(user['username'], user['password'], real_code, uuid)

    # 如果这里报错，去检查你的万能挡板是不是没返回 code 200
    if res_login.json().get("code") != 200:
        pytest.exit(f"❌ 致命错误：自动登录若依失败！响应数据：{res_login.text}")

    token = res_login.json().get("token")
    s.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})

    yield s
    s.close()