from filesystem import FileSystemLoader, Directory, File
from datetime import datetime
import random


class VirtualFS:
    """虚拟文件系统管理器"""
    
    def __init__(self):
        self.root = FileSystemLoader.build_default()
        self.current_dir = "/home/ubuntu"
    
    def _normalize_path(self, path: str) -> str:
        """规范化路径，处理 .. 和 ."""
        if path.startswith("/"):
            parts = [p for p in path.split("/") if p]
        else:
            current_parts = [p for p in self.current_dir.split("/") if p]
            parts = current_parts + [p for p in path.split("/") if p]
        
        # 处理 .. 和 .
        resolved = []
        for part in parts:
            if part == "..":
                if resolved:
                    resolved.pop()
            elif part != ".":
                resolved.append(part)
        
        return "/" + "/".join(resolved) if resolved else "/"
    
    def _resolve_path(self, path: str) -> File | Directory | None:
        """解析路径，返回节点"""
        normalized = self._normalize_path(path)
        
        if normalized == "/":
            return self.root
        
        parts = [p for p in normalized.split("/") if p]
        current = self.root
        
        for part in parts:
            if not current.is_directory() or not current.has_child(part):
                return None
            current = current.get_child(part)
        
        return current
    
    def get_node(self, path: str):
        """获取节点"""
        return self._resolve_path(path)
    
    def list_dir(self, path: str = None, show_all=False, show_long=False) -> str:
        """列出目录内容"""
        target_path = path if path else self.current_dir
        node = self._resolve_path(target_path)
        
        if not node or not node.is_directory():
            return f"ls: cannot access '{target_path}': No such file or directory\n"
        
        children = node.list_children()
        if not show_all:
            children = [c for c in children if not c.startswith(".")]
        
        if not children:
            return ""
        
        if show_long:
            output = f"total {len(children) * 4}\n"
            for name in sorted(children):
                child = node.get_child(name)
                if child.is_directory():
                    perms = f"drwxr-xr-x"
                    size = "4096"
                else:
                    perms = f"-rw-r--r--"
                    size = str(child.size()).rjust(5)
                
                time_str = child.modified.strftime("%b %d %H:%M")
                output += f"{perms} 1 {child.owner} {child.group} {size} {time_str} {name}\n"
            return output
        else:
            return "  ".join(sorted(children)) + "\n"
    
    def read_file(self, path: str) -> str:
        """读取文件内容"""
        node = self._resolve_path(path)
        if not node:
            return f"cat: {path}: No such file or directory\n"
        if not node.is_file():
            return f"cat: {path}: Is a directory\n"
        content = node.read()
        return content if content else ""
