from .node import Node


class File(Node):
    """文件节点"""
    
    def __init__(self, name, content="", permissions="644", owner="ubuntu", group="ubuntu"):
        super().__init__(name, permissions, owner, group)
        self.content = content
    
    def is_file(self) -> bool:
        return True
    
    def read(self) -> str:
        return self.content
    
    def size(self) -> int:
        return len(self.content)
