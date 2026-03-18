# 文件：api/user_api.py
from common.base_api import BaseApi
import allure

class UserApi(BaseApi):
    """若依【系统管理-用户管理】模块 API 封装"""
    @allure.step("API动作：调用获取当前登录用户信息接口 (/getInfo)")
    def get_current_user_info(self):
        return self.request("GET", "/getInfo")

    @allure.step("API动作：新增用户")
    def add_user(self, payload):
        mock_data = {"code": 200, "msg": "Mock新增成功"}
        return self.request("POST", "/system/user", json=payload, mock_data=mock_data)

    @allure.step("API动作：根据用户名查询用户列表")
    def get_user_list(self, username):
        # 提供精准的查询 Mock 结构，防止后续断言报错
        mock_data = {"code": 200, "rows": [{"userId": 999, "userName": username, "status": "0"}]}
        return self.request("GET", "/system/user/list", params={"userName": username}, mock_data=mock_data)

    def update_user(self, payload):
        mock_data = {"code": 200, "msg": "Mock修改成功"}
        return self.request("PUT", "/system/user", json=payload, mock_data=mock_data)

    @allure.step("API动作：删除用户")
    def delete_user(self, user_ids):
        mock_data = {"code": 200, "msg": "Mock删除成功"}
        return self.request("DELETE", f"/system/user/{user_ids}", mock_data=mock_data)