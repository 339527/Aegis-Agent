# tests/test_ruoyi_login.py
import allure
from api.user_api import UserApi

@allure.epic("若依中台质量保障体系")
@allure.feature("核心鉴权链路攻防演练")
class TestRuoYiAuth:

    @allure.story("验证：全局拦截器能否成功突破 Redis 验证码并注入 Token")
    def test_verify_global_token_injection(self, session):
        """
        这个用例极度简单：
        如果代码能走到这里没有报错退出，说明 conftest.py 里的登录已经完美成功了！
        我们只需要断言一下 session 的 headers 里是不是真的被塞进了 Token。
        """
        with allure.step("检查全局 Session 头部是否包含 Authorization"):
            # 提取当前的 Headers
            current_headers = session.headers

            # 严格断言
            assert "Authorization" in current_headers, "全局 Token 注入失败！"
            assert current_headers["Authorization"].startswith("Bearer "), "Token 格式错误！"

            # 在终端打印出来秀一下
            print(f"\n🎉 【大获全胜】当前全局请求头已被自动化框架接管: {current_headers}")


    # 🟢 修改后：把 conftest.py 里的 base_url 也当做参数传进来！
    @allure.story("业务连通性验证：携带全局 Token 访问受保护接口")
    def test_get_user_info(self, session, base_url):
        with allure.step("1. 组装武器：实例化 UserApi"):
            # 🔴 修改前：user_api = UserApi(session, session.base_url)
            # 🟢 修改后：直接使用传进来的 base_url
            user_api = UserApi(session, base_url)

        with allure.step("2. 扣动扳机：发起获取用户信息请求"):
            res = user_api.get_current_user_info()

        # ... 下面的断言代码完全不用动 ...
        with allure.step("3. 检查靶标：多维度断言响应结果"):
            assert res.status_code == 200, f"网络请求失败，状态码: {res.status_code}"
            res_data = res.json()
            assert res_data.get("code") == 200, f"业务校验失败: {res.text}"

            actual_username = res_data.get("user", {}).get("userName")
            assert actual_username == "admin", f"预期为 admin，实际是: {actual_username}"

            permissions = res_data.get("permissions", [])[:3]
            print(f"\n👑 【王者归来】成功闯入若依后台！")
            print(f"👤 当前登录账号: {actual_username}")
            print(f"🔑 拥有最高权限集合 (节选): {permissions}")