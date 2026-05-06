class BaseCommand:
    """命令基类"""
    
    def execute(self, args=None) -> str:
        """执行命令，返回输出"""
        raise NotImplementedError
