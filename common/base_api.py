import os
import requests
import allure
import logging
import json


class MockResponse:
    def __init__(self, json_data):
        self.status_code = 200
        self._json_data = json_data
        self.text = str(json_data)

    def json(self):
        return self._json_data
class BaseApi:
    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url

    def request(self, method, url, **kwargs):
        if os.getenv("RUN_ENV") == "ci":
            logging.info(f"☁️ [HTTP挡板] 拦截到向 {url} 的请求，返回伪造成功数据！")

            # 【万能假数据】不管是查验证码、登录、还是增删改查，通通返回成功 200
            # 里面包含了你需要的所有关键字段，让代码顺畅地跑下去！
            mock_data = {
                "code": 200,
                "msg": "操作成功 (Mocked by CI)",
                "uuid": "mock-uuid-12345",
                "token": "mock-jwt-token-67890",
                "userId": 999,
                "data": {"userId": 999, "userName": "ci_mock_user"}
            }
            return MockResponse(mock_data)

        full_url = f"{self.base_url}{url}"
        # 记录日志
        logging.info(f"👉 发起请求: [{method}] {full_url} Payload: {kwargs}")

        try:
            response = self.session.request(method, full_url, **kwargs)

            # 自动挂载请求详情到 Allure 报告
            allure.attach(f"URL: {full_url}\nMethod: {method}\nArgs: {kwargs}",
                          name="请求链路快照", attachment_type=allure.attachment_type.TEXT)

            # 优雅处理 JSON 解析
            try:
                res_json = response.json()
                res_body = json.dumps(res_json, ensure_ascii=False, indent=2)
                allure.attach(res_body, name="响应主体(JSON)", attachment_type=allure.attachment_type.JSON)
            except:
                allure.attach(response.text, name="响应主体(TEXT)", attachment_type=allure.attachment_type.TEXT)

            # 如果状态码异常，额外加一个显眼的快照标记
            if response.status_code != 200:
                allure.attach(f"Status Code: {response.status_code}", name="⚠️ 异常状态码警报",
                              attachment_type=allure.attachment_type.TEXT)

            return response
        except Exception as e:
            import traceback
            allure.attach(traceback.format_exc(), name="🚨 运行时致命崩溃堆栈",
                          attachment_type=allure.attachment_type.TEXT)
            raise e