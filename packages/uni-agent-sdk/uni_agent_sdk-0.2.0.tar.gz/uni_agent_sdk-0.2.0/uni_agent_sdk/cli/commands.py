"""CLI command implementations."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional

from .scaffold import ScaffoldError, create_scaffold


def init_project(name: str, template: str = "basic") -> bool:
    """Initialise a new agent project using the selected template."""
    print(f"🚀 创建新项目: {name}")
    print(f"📋 使用模板: {template}")

    try:
        project_dir = create_scaffold(Path.cwd(), name, template)
    except FileExistsError:
        print(f"❌ 错误: 目录 '{name}' 已存在")
        return False
    except ScaffoldError as exc:
        print(f"❌ 模板错误: {exc}")
        return False
    except Exception as exc:
        print(f"❌ 创建项目失败: {exc}")
        return False

    print("✅ 项目创建成功！")
    print("\n下一步:")
    print(f"  cd {project_dir.name}")
    print("  python -m venv .venv")
    print("  source .venv/bin/activate  # Windows: .venv\\Scripts\\activate")
    print("  pip install -r requirements.txt")
    print("  cp .env.example .env")
    print("  python -m {}.main".format(project_dir.name.replace('-', '_')))
    return True


def run_agent(config_file: Optional[str] = None, debug: bool = False) -> bool:
    """Run an agent entry point located in the current working directory."""
    print("🤖 启动智能体...")

    if debug:
        print("🐛 调试模式已启用")

    if config_file:
        print(f"📄 使用配置文件: {config_file}")
        if not os.path.exists(config_file):
            print(f"❌ 配置文件不存在: {config_file}")
            return False

    print("⚠️  请在项目目录中执行 `python -m <your_package>.main`")
    print("或运行你自定义的启动脚本。")
    return True


def run_tests(verbose: bool = False) -> bool:
    """Run pytest in the current working directory."""
    print("🧪 运行测试...")

    cmd = ["python", "-m", "pytest"]
    if verbose:
        cmd.append("-v")
    if os.path.exists("tests"):
        cmd.append("tests")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        print("❌ pytest 未安装，请先安装: pip install pytest")
        return False
    except Exception as exc:
        print(f"❌ 运行测试失败: {exc}")
        return False

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result.returncode == 0


__all__ = ["init_project", "run_agent", "run_tests"]
