# api/auth_api.py
from common.base_api import BaseApi


class AuthApi(BaseApi):
    """
    若依鉴权中心 API 封装
    继承自 BaseApi，直接白嫖底层的 Allure 日志记录和异常容错机制！
    """

    def get_captcha_uuid(self):
        """
        步骤 1：触发后端生成验证码，并提取专属的 UUID
        """
        # 🚨 注意：这里调用的不是 requests.get，而是我们自己封装的 self.request！
        res = self.request("GET", "/captchaImage")

        # 简单的业务阻断：如果验证码都拿不到，后面也不用跑了
        assert res.status_code == 200, f"获取验证码接口异常！响应: {res.text}"

        return res.json().get("uuid")

    def login(self, username, password, code, uuid):
        """
        步骤 2：携带全量情报，发起终极登录，换取 Token
        """
        payload = {
            "username": username,
            "password": password,
            "code": code,
            "uuid": uuid
        }

        # 同样调用底层的 self.request，这会把 Payload 完美打印到控制台和报告里
        res = self.request("POST", "/login", json=payload)
        return res