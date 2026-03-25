# tests/test_user_add_ddt.py
import pytest
import allure
from api.user_api import UserApi
from common.file_util import read_yaml
from common.mysql_util import MysqlUtil
from config.env_config import Config

# 1. 提前读取好 YAML 里的用例数据列表
USER_CASES = read_yaml("data/user_add_data.yaml")


@allure.epic("若依中台质量保障体系")
@allure.feature("用户管理生命周期闭环验证")
class TestUserLifecycle:

    # 2. 启动数据驱动引擎！(解包 YAML 数据传入测试方法)
    @allure.issue("https://jira.yourcompany.com/browse/BUG-123", "点击跳转到对应的Jira缺陷单")
    @allure.testcase("https://testlink.com/cases/1", "关联的测试用例库地址")
    @pytest.mark.parametrize("case_info", USER_CASES)
    def test_add_user_lifecycle(self, session, base_url, case_info):

        # 动态设置 Allure 的标题，让每一条测试报告的名字都不一样！
        allure.dynamic.title(f"数据驱动: {case_info['case_title']}")

        user_api = UserApi(session, base_url)
        payload = case_info['payload']
        username = payload.get("userName")

        # ================== 阶段 0 - 强力前置清理（带保护版） ==================
        # 增加判断：只有不是 admin 的测试账号才执行清理
        if username and username != "admin":
            with allure.step(f"阶段0：前置扫地 - 物理删除可能存在的残留用户: {username}"):
                db_pre = MysqlUtil(**Config.MYSQL_CONFIG)
                delete_sql = "DELETE FROM sys_user WHERE user_name = %s"
                db_pre.conn.cursor().execute(delete_sql, (username,))
                db_pre.conn.commit()
                db_pre.close()

        # ================== 阶段一：创建数据 (Create) ==================
        with allure.step(f"阶段1：执行新增用户操作 - 账号: {username}"):
            res_add = user_api.add_user(payload)
            res_add_data = res_add.json()

        # ================== 阶段二：核心断言 (Assert) ==================
        with allure.step(f"阶段2：业务断言 - 预期状态码: {case_info['expected_code']}"):
            assert res_add_data.get("code") == case_info['expected_code'], f"状态码不符: {res_add.text}"
            assert case_info['expected_msg'] in res_add_data.get("msg", ""), "返回提示信息不符！"

        # ================== 阶段三：深层物理数据核对 (Database Assert) ==================
        # 如果这是一个正向用例，并且接口返回成功了，我们再去查数据库验证真伪！
        if case_info.get('is_success'):
            with allure.step("阶段3：绕过接口，直连 MySQL 数据库进行落库断言"):
                # 1. 唤醒数据库探针 (这里解包了 env_config.py 里的 MYSQL_CONFIG 字典)
                db = MysqlUtil(**Config.MYSQL_CONFIG)

                # 2. 写 SQL 去查这个刚刚被创建出来的用户
                sql = "SELECT user_name, nick_name, status, del_flag FROM sys_user WHERE user_name = %s"
                db_result = db.query_one(sql, (username,))

                # 3. 极其硬核的断言！防范“接口返回成功但数据库回滚”的幽灵 Bug
                assert db_result is not None, f"⚠️ 严重级 Bug: 接口返回成功，但数据库中根本没找到账号 {username}!"
                assert db_result['nick_name'] == payload['nickName'], "数据库落库的昵称与传入参数不一致！"
                assert db_result['status'] == '0', "刚创建的用户状态应该为正常(0)！"
                assert db_result['del_flag'] == '0', "刚创建的用户不应被标记为删除(del_flag=0)！"

                print(f"\n🔐 数据库核对完美通过！真实落库数据: {db_result}")

                # 用完关闭数据库连接，释放资源
                db.close()

        # ================== 阶段四：数据清理 (Teardown/Delete) ==================
        # 验证完数据库后，必须把造出来的数据删掉，保持测试环境干净！
        if case_info.get('is_success'):
            with allure.step("阶段4：闭环清理 - 查询动态 ID 并物理删除用户"):
                # 4.1 去列表里查出刚才新建的用户的动态 ID
                res_list = user_api.get_user_list(username)
                rows = res_list.json().get("rows", [])
                assert len(rows) > 0, f"清理数据失败：未查询到刚创建的用户 {username}!"

                # 提取 userId
                target_user_id = rows[0].get("userId")
                print(f"🔍 抓取到刚创建的新用户 ID: {target_user_id}，准备执行抹杀程序...")

                # 4.2 调用删除接口斩草除根
                res_del = user_api.delete_user(target_user_id)
                # ✅ 完整的正确代码
                assert res_del.json().get("code") == 200, "删除刚才创建的测试用户失败！"