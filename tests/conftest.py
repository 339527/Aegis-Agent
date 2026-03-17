# tests/conftest.py
import pytest
import requests
import logging
from config.env_config import Config
from api.auth_api import AuthApi
from common.redis_util import RedisUtil


@pytest.fixture(scope="session")
def base_url():
    """按需动态获取当前环境的 URL"""
    return Config.get_base_url()


@pytest.fixture(scope="session")
def session(base_url):
    """
    企业级全局鉴权拦截器 (Session 级别，全局只跑一次)
    核心任务：窃取验证码 -> 登录若依 -> 提取 Token -> 注入全局 Header
    """
    logging.info(f"\n--- 🚀 若依自动化攻防演练启动：连接 {base_url} ---")

    # 1. 创建全局唯一的 HTTP 长连接对象
    s = requests.Session()

    # 2. 实例化若依的鉴权特种兵
    auth_api = AuthApi(s, base_url)

    # 3. 连上本地的 Redis 武器库
    redis_db = RedisUtil(host=Config.REDIS_CONFIG["host"],
                         port=Config.REDIS_CONFIG["port"],
                         password=Config.REDIS_CONFIG["password"],
                         db=Config.REDIS_CONFIG["db"])

    # ---------------- ⚡ 开始破壁 ⚡ ----------------

    # 动作 A：去若依门口拿一个 UUID（并触发后端把验证码存进 Redis）
    uuid = auth_api.get_captcha_uuid()
    logging.info(f"🕵️‍♂️ 成功截获门禁 UUID: {uuid}")

    # 动作 B：转身潜入 Redis，根据 UUID 把验证码的底牌偷出来
    real_code = redis_db.get_captcha_code(uuid)

    # 容错：如果 Redis 没配好或者没拿到，给个默认算术值 "12" 碰碰运气
    if not real_code:
        logging.warning("⚠️ Redis 中未找到验证码，尝试使用默认值 '12' 盲猜...")
        real_code = "12"
    else:
        logging.info(f"🔓 Redis 破壁成功！提取到真实验证码答案: {real_code}")

    # 动作 C：拿着账密和偷来的验证码，大摇大摆地发起合法登录！
    user = Config.ADMIN_USER
    res_login = auth_api.login(user['username'], user['password'], real_code, uuid)

    # 如果登录失败，直接拉响警报，终止整个测试框架运行！
    if res_login.json().get("code") != 200:
        pytest.exit(f"❌ 致命错误：自动登录若依失败！响应数据：{res_login.text}")

    # 动作 D：登录成功，提取若依大门的至高权利凭证（Bearer Token）
    token = res_login.json().get("token")
    logging.info(f"✅ 若依大门已敞开，获得全局 Bearer Token: {token[:15]}...")

    # ---------------- 💉 全局注入 ----------------

    # 将 Token 永久焊死在这个 Session 的 Header 里，之后的所有请求将自带超管权限！
    s.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })

    # 功成身退，关闭 Redis 连接
    redis_db.close()

    # 把这个装配了 Token 的超级武器（Session）交出去，供所有测试用例使用
    yield s

    # ---------------- 🛑 测试结束清理 ----------------
    logging.info("\n--- 🛑 测试套件执行完毕，关闭全局网络连接 ---")
    s.close()