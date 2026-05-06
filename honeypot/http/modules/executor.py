import os
import importlib
import inspect
from pathlib import Path
from modules.base import BaseModule

_module_registry = {}


def _discover_modules():
    """递归扫描 modules/ 下的所有子目录，自动发现并注册模块"""
    modules_dir = Path(__file__).parent
    
    for py_file in modules_dir.rglob("*.py"):
        if py_file.name.startswith("__") or py_file.name in ("base.py", "executor.py"):
            continue
        
        rel_path = py_file.relative_to(modules_dir.parent)
        module_parts = list(rel_path.parts[:-1]) + [py_file.stem]
        module_name = ".".join(module_parts)
        
        try:
            module = importlib.import_module(module_name)
            
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseModule) and obj != BaseModule:
                    module_key = name.replace("Module", "").lower()
                    _module_registry[module_key] = obj
        except Exception as e:
            print(f"[WARN] Failed to load module from {module_name}: {e}")


def get_all_modules():
    """获取所有已注册的模块类"""
    if not _module_registry:
        _discover_modules()
    return _module_registry.copy()


_discover_modules()
