import os
import importlib
import inspect
from pathlib import Path
from commands.base import BaseCommand

# 命令注册表
_command_registry = {}


def _discover_commands():
    """递归扫描 commands/ 下的所有子目录，自动发现并注册命令"""
    commands_dir = Path(__file__).parent
    
    for py_file in commands_dir.rglob("*.py"):
        # 跳过 __init__.py, base.py, executor.py
        if py_file.name.startswith("__") or py_file.name in ("base.py", "executor.py"):
            continue
        
        # 计算相对路径，如 "static/whoami.py"
        rel_path = py_file.relative_to(commands_dir)
        # 构建模块路径，如 "commands.static.whoami"
        module_parts = ["commands"] + list(rel_path.parts[:-1]) + [py_file.stem]
        module_name = ".".join(module_parts)
        
        try:
            module = importlib.import_module(module_name)
            
            # 查找模块中继承 BaseCommand 的类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseCommand) and obj != BaseCommand:
                    # 使用类名去掉"Command"后缀并转小写作为命令名
                    cmd_name = name.replace("Command", "").lower()
                    _command_registry[cmd_name] = obj
        except Exception as e:
            print(f"[WARN] Failed to load command from {module_name}: {e}")


def get_command_class(cmd_name: str):
    """获取命令类"""
    if not _command_registry:
        _discover_commands()
    return _command_registry.get(cmd_name)


def get_all_commands():
    """获取所有已注册的命令"""
    if not _command_registry:
        _discover_commands()
    return _command_registry.copy()


# 初始化时自动发现
_discover_commands()
