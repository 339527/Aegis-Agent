import os
import pytest
import time
import sys
import shutil
from config.log_config import logger

if __name__ == '__main__':
    print("🚀 启动 Agent 双轨防御系统全量巡检...")

    # 1. 核心动作：捕获测试结果状态码！
    # 如果测试全通过，返回 0；如果 AI 拦截到了越权/注入，返回非 0
    exit_code = pytest.main()

    # 2. 环境感知逻辑：智能判断当前是不是本地电脑
    print("\n⏳ 测试引擎熄火，开始结算战报...")
    time.sleep(1)

    # shutil.which 可以探测系统里有没有装 allure 这个软件
    # 如果是你本地电脑，肯定能找到；如果是 Gitee 云端裸机，就会返回 None
    if shutil.which("allure"):
        print("💻 检测到本地 Allure 环境，正在编译静态 HTML 报告...")
        os.system("allure generate ./reports/allure_raw -o ./reports/allure_report --clean")
        print("✅ Allure 报告编译完成！请在左侧目录找到 index.html 并在浏览器打开。")
    else:
        print("☁️ 当前处于云端 CI 环境，无 allure 组件，跳过 HTML 报告生成。")

    # 3. 终极物理阻断（解决“假绿”陷阱的核心）
    if exit_code != 0:
        print(f"\n🚨 [高危] 发现异常！防御网被击穿或 AI 引擎主动熔断 (Exit Code: {exit_code})！")
        print("💥 强制中止流水线！")
        sys.exit(exit_code)  # 把真实的非 0 失败码甩给 Gitee，流水线瞬间爆红！

    print("\n🎉 所有防御节点测试通过！流水线准许放行！")
    sys.exit(0)