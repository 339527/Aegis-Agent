# run.py
import os
import pytest
import time

if __name__ == '__main__':
    print("🚀 开始执行自动化测试用例...")

    # 1. 执行 pytest 测试
    # 由于我们在 pytest.ini 里已经配了 addopts = -vs --alluredir=./reports/allure_raw --clean-alluredir
    # 所以这里直接调 pytest.main() 就会自动去读 ini 文件的配置
    pytest.main()

    print("\n⏳ 测试执行完毕，正在将原始数据编译为静态 HTML 报告...")
    time.sleep(1)  # 稍微停顿一下，确保原始数据全部写入磁盘

    # 2. 利用系统命令，生成静态 HTML 报告
    # -o ./reports/allure_report : 指定静态网页输出的目录
    # --clean : 每次生成前，先清空上一次的旧网页数据
    os.system("allure generate ./reports/allure_raw -o ./reports/allure_report --clean")

    print("\n✅ Allure 报告编译完成！")
    print("👉 请在左侧目录找到 reports/allure_report/index.html，右键选择浏览器打开！")