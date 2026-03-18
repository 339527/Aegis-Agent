import os
import requests
import allure
import logging
import json

class MockResponse:
    def __init__(self, json_data):
        self.status_code = 200
        self._json_data = json_data
        self.text = json.dumps(json_data, ensure_ascii=False)

    def json(self):
        return self._json_data

class BaseApi:
    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url

    # 🌟 核心改动：增加 mock_data 参数接收业务层传来的假数据
    def request(self, method, url, mock_data=None, **kwargs):
        # 🌟 强化逻辑：CI 模式下的“物理隔离”
        if os.getenv("RUN_ENV") == "ci":
            if mock_data is not None:
                logging.info(f"☁️ [HTTP挡板] 拦截到向 {url} 的请求，返回伪造数据！")
                return MockResponse(mock_data)
            else:
                # 如果没传 mock_data，在 CI 环境下直接伪造一个通用的响应，防止崩溃
                logging.warning(f"⚠️ [CI 警告] 请求 {url} 未配置 Mock 数据，已返回默认成功响应！")
                return MockResponse({"code": 200, "msg": "CI 默认 Mock 成功", "data": {}})

        full_url = f"{self.base_url}{url}"
        logging.info(f"👉 发起请求: [{method}] {full_url} Payload: {kwargs}")

        try:
            response = self.session.request(method, full_url, **kwargs)
            allure.attach(f"URL: {full_url}\nMethod: {method}\nArgs: {kwargs}",
                          name="请求链路快照", attachment_type=allure.attachment_type.TEXT)
            try:
                res_json = response.json()
                res_body = json.dumps(res_json, ensure_ascii=False, indent=2)
                allure.attach(res_body, name="响应主体(JSON)", attachment_type=allure.attachment_type.JSON)
            except:
                allure.attach(response.text, name="响应主体(TEXT)", attachment_type=allure.attachment_type.TEXT)

            if response.status_code != 200:
                allure.attach(f"Status Code: {response.status_code}", name="⚠️ 异常状态码警报",
                              attachment_type=allure.attachment_type.TEXT)
            return response
        except Exception as e:
            import traceback
            allure.attach(traceback.format_exc(), name="🚨 运行时致命崩溃堆栈",
                          attachment_type=allure.attachment_type.TEXT)
            raise e