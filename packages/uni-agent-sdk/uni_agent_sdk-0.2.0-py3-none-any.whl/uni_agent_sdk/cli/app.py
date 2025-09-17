"""CLI应用主逻辑"""

import argparse
import sys
from typing import Optional

def cli_app():
    """CLI应用主函数"""
    parser = argparse.ArgumentParser(
        prog="uni-agent",
        description="uni-agent-sdk 命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  uni-agent init my-agent      创建新的智能体项目
  uni-agent run               运行智能体
  uni-agent test              运行测试
  uni-agent --version         显示版本信息
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version="uni_agent_sdk 0.2.0"
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # init 命令
    init_parser = subparsers.add_parser("init", help="创建新的智能体项目")
    init_parser.add_argument("name", help="项目名称")
    init_parser.add_argument("--template", default="basic", help="项目模板")

    # run 命令
    run_parser = subparsers.add_parser("run", help="运行智能体")
    run_parser.add_argument("--config", "-c", help="配置文件路径")
    run_parser.add_argument("--debug", action="store_true", help="启用调试模式")

    # test 命令
    test_parser = subparsers.add_parser("test", help="运行测试")
    test_parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "init":
            from .commands import init_project
            init_project(args.name, args.template)
        elif args.command == "run":
            from .commands import run_agent
            run_agent(args.config, args.debug)
        elif args.command == "test":
            from .commands import run_tests
            run_tests(args.verbose)
    except ImportError as e:
        print(f"命令模块导入失败: {e}")
        print("请确保所有依赖已正确安装")
        sys.exit(1)