from datetime import datetime


class Node:
    """文件系统节点基类"""
    
    def __init__(self, name, permissions="644", owner="ubuntu", group="ubuntu"):
        self.name = name
        self.permissions = permissions
        self.owner = owner
        self.group = group
        now = datetime.now()
        self.created = now
        self.modified = now
    
    def is_file(self) -> bool:
        return False
    
    def is_directory(self) -> bool:
        return False
