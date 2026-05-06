class BaseModule:
    """HTTP 蜜罐模块基类"""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def setup(self, app):
        """初始化时调用，注册 Flask 路由/钩子"""
        pass
