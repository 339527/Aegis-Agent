import time
from config.log_config import logger
import os
import pytest
import sys
import shutil

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("环境变量加载成功")
except ImportError:
    logger.warning("dotenv 库未安装，跳过环境变量加载")


def run_regression_tests():
    """运行常规回归测试（使用 Mock）"""
    logger.info("\n启动常规回归测试（Mock 模式）...")
    logger.info("测试范围：所有测试用例，排除高烈度演练测试")
    
    # 设置环境变量，强制使用 Mock
    os.environ["USE_MOCK_AUDIT"] = "True"
    os.environ["USE_MOCK_AI"] = "True"
    
    # 运行测试，排除 real_ai 标记的测试
    exit_code = pytest.main(["-m", "not real_ai"])
    
    if exit_code == 0:
        logger.info("常规回归测试通过！")
    else:
        logger.error(f"常规回归测试失败 (Exit Code: {exit_code})")
    
    return exit_code


def run_real_ai_tests():
    """运行高烈度演练测试（使用真实 AI）"""
    logger.info("\n启动高烈度演练测试（真实 AI 模式）...")
    logger.info("警告：此测试将消耗真实的 API Token")
    
    # 设置环境变量，使用真实 AI
    os.environ["USE_MOCK_AUDIT"] = "False"
    os.environ["USE_MOCK_AI"] = "False"
    os.environ["USE_REAL_ATTACKER_AI"] = "True"
    
    # 检查 API Key 是否配置
    if not os.getenv("ZHIPU_API_KEY"):
        logger.error("错误：未配置 ZHIPU_API_KEY 环境变量")
        logger.info("请在 .env 文件中配置 ZHIPU_API_KEY")
        return 1
    
    # 运行测试，只包含 real_ai 标记的测试
    exit_code = pytest.main(["-m", "real_ai"])
    
    if exit_code == 0:
        logger.info("高烈度演练测试完成！")
    else:
        logger.error(f"高烈度演练测试失败 (Exit Code: {exit_code})")
    
    return exit_code


def run_all_tests():
    """运行所有测试（包含常规回归和高烈度演练）"""
    logger.info("\n启动全量测试...")
    
    # 不设置环境变量，让每个测试根据自己的标记决定使用什么模式
    # - 标记为 @pytest.mark.real_ai 的测试使用真实 AI
    # - 其他测试使用 Mock 模式
    
    # 运行所有测试
    exit_code = pytest.main()
    
    if exit_code == 0:
        logger.info("全量测试通过！")
    else:
        logger.error(f"全量测试失败 (Exit Code: {exit_code})")
    
    return exit_code


def show_menu():
    """显示交互式菜单"""
    print("\n" + "="*50)
    print("    Aegis-Agent 测试运行器")
    print("="*50)
    print(" 1. 常规回归测试 (Mock 模式)")
    print(" 2. 高烈度演练测试 (真实 AI)")
    print(" 3. 全量测试")
    print(" 4. 退出")
    print("="*50)


def main():
    """主函数"""
    while True:
        show_menu()
        try:
            choice = input("请选择测试模式 (1-4): ")
            
            if choice == "1":
                exit_code = run_regression_tests()
            elif choice == "2":
                exit_code = run_real_ai_tests()
            elif choice == "3":
                exit_code = run_all_tests()
            elif choice == "4":
                logger.info("退出程序")
                sys.exit(0)
            else:
                print("无效的选择，请重新输入")
                continue
            
            # 生成 Allure 报告
            if shutil.which("allure"):
                logger.info("检测到本地 Allure 环境，正在编译静态 HTML 报告...")
                os.system("allure generate ./reports/allure_raw -o ./reports/allure_report --clean")
                logger.info("Allure 报告编译完成！请在左侧目录找到 index.html 并在浏览器打开。")
            else:
                logger.info("当前环境无 allure 组件，跳过 HTML 报告生成。")
            
            # 检查测试结果
            if exit_code != 0:
                logger.info(f"\n[高危] 发现异常！防御网被击穿或 AI 引擎主动熔断 (Exit Code: {exit_code})！")
                sys.exit(exit_code)
            
            logger.info("\n测试完成！")
            
        except KeyboardInterrupt:
            logger.info("\n用户中断，退出程序")
            sys.exit(0)
        except Exception as e:
            logger.error(f"运行出错: {e}", exc_info=True)
            sys.exit(1)


if __name__ == '__main__':
    main()