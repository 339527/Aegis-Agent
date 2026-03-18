# 文件：api/auth_api.py
from common.base_api import BaseApi

class AuthApi(BaseApi):
    """若依鉴权中心 API 封装"""
    def get_captcha_uuid(self):
        mock_data = {"code": 200, "uuid": "mock-uuid-ci"}
        res = self.request("GET", "/captchaImage", mock_data=mock_data)
        assert res.status_code == 200, f"获取验证码接口异常！响应: {res.text}"
        return res.json().get("uuid")

    def login(self, username, password, code, uuid):
        payload = {"username": username, "password": password, "code": code, "uuid": uuid}
        mock_data = {"code": 200, "token": "mock-token-ci-123456"}
        res = self.request("POST", "/login", json=payload, mock_data=mock_data)
        return res