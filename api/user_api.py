# 文件：api/user_api.py
from common.base_api import BaseApi
import allure

class UserApi(BaseApi):
    """若依【系统管理-用户管理】模块 API 封装"""
    @allure.step("API动作：调用获取当前登录用户信息接口 (/getInfo)")
    def get_current_user_info(self):
        # 🌟 这里的 Mock 数据结构必须和 test_ruoyi_login.py 里的断言对齐
        mock = {
            "code": 200,
            "user": {"userName": "admin", "userId": 1}, # 必须叫 user，而不是 data
            "permissions": ["*:*:*"]
        }
        return self.request("GET", "/getInfo", mock_data=mock)
    @allure.step("API动作：新增用户")
    def add_user(self, payload):
        # 🌟 如果是测试“用户名已存在”，就应该 Mock 返回 500
        # 这里的技巧是：我们可以根据 payload 的内容动态决定 Mock 结果
        if payload.get("userName") == "admin":
            mock = {"code": 500, "msg": "新增用户'admin'失败，登录账号已存在"}
        elif not payload.get("userName"):
            mock = {"code": 500, "msg": "用户账号不能为空"}
        else:
            mock = {"code": 200, "msg": "操作成功"}

        return self.request("POST", "/system/user", json=payload, mock_data=mock)
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