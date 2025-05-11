#!/usr/bin/env python
"""Django管理命令行工具，用于管理任务。"""
import os
import sys


def main():
    """运行管理任务。"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docmgr.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入Django。确保它已安装并且在PYTHONPATH环境变量中？"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main() 