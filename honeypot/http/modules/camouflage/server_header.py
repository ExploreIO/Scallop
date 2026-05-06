import random
import time
from flask import request
from modules.base import BaseModule


class ServerHeaderModule(BaseModule):
    """Server 头随机化模块：同一IP在24小时内返回相同Server头"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.headers_pool = config.get('server_headers', ['nginx/1.24.0']) if config else ['nginx/1.24.0']
        self._ip_assignments = {}
        self._window_seconds = 86400
    
    def get_server_header(self, ip=None):
        """根据IP获取一致的Server头"""
        if ip is None:
            ip = request.remote_addr
        
        now = time.time()
        
        if ip in self._ip_assignments:
            header, timestamp = self._ip_assignments[ip]
            if now - timestamp < self._window_seconds:
                return header
        
        header = random.choice(self.headers_pool)
        self._ip_assignments[ip] = (header, now)
        return header
    
    def setup(self, app):
        """注册 after_request 钩子"""
        
        @app.after_request
        def set_server_header(response):
            ip = request.remote_addr
            response.headers['Server'] = self.get_server_header(ip)
            return response
