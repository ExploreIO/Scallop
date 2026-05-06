from .node import Node


class Directory(Node):
    """目录节点"""
    
    def __init__(self, name, permissions="755", owner="ubuntu", group="ubuntu"):
        super().__init__(name, permissions, owner, group)
        self.children = {}
    
    def is_directory(self) -> bool:
        return True
    
    def add_child(self, node: Node):
        """添加子节点"""
        self.children[node.name] = node
    
    def get_child(self, name: str) -> Node:
        """获取子节点"""
        return self.children.get(name)
    
    def list_children(self) -> list:
        """列出所有子节点名称"""
        return list(self.children.keys())
    
    def has_child(self, name: str) -> bool:
        """检查是否存在子节点"""
        return name in self.children
    
    def remove_child(self, name: str):
        """移除子节点"""
        if name in self.children:
            del self.children[name]
