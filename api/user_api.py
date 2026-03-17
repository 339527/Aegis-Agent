# api/user_api.py
from common.base_api import BaseApi
import allure

class UserApi(BaseApi):
    """
    若依【系统管理-用户管理】模块 API 封装
    """

    @allure.step("API动作：调用获取当前登录用户信息接口 (/getInfo)")
    def get_current_user_info(self):
        """获取当前登录用户的详细信息"""
        return self.request("GET", "/getInfo")

    @allure.step("API动作：新增用户")
    def add_user(self, payload):
        """生命周期起点：新增用户"""
        return self.request("POST", "/system/user", json=payload)

    @allure.step("API动作：根据用户名查询用户列表")
    def get_user_list(self, username):
        """生命周期中继：为了获取动态生成的 user_id"""
        return self.request("GET", "/system/user/list", params={"userName": username})

    def update_user(self, payload):
        """修改用户接口"""
        return self.request("PUT", "/system/user", json=payload)  # 注意：若依的修改接口通常是 PUT 请求

    @allure.step("API动作：删除用户")
    def delete_user(self, user_ids):
        """生命周期终点：数据清理（支持批量删除，传参格式如 '101,102'）"""
        return self.request("DELETE", f"/system/user/{user_ids}")