from pathlib import Path
from flask import render_template_string
from modules.base import BaseModule


class TemplateEngineModule(BaseModule):
    """模板引擎模块：读取 templates/ 目录下的 HTML 模板"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.template_dir = Path(__file__).parent.parent.parent / "templates"
        self._cache = {}
    
    def _read_template(self, name):
        """读取模板文件"""
        if name in self._cache:
            return self._cache[name]
        
        file_path = self.template_dir / f"{name}.html"
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            self._cache[name] = content
            return content
        return None
    
    def get_login_page(self, **context):
        """获取登录页 HTML"""
        html = self._read_template("login")
        if html:
            return render_template_string(html, **context)
        return self._fallback_login()
    
    def get_error_page(self, message="Invalid credentials"):
        """获取错误页 HTML"""
        html = self._read_template("error")
        if html:
            return render_template_string(html, message=message)
        return self._fallback_error(message)
    
    def _fallback_login(self):
        """备用登录模板"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign In</title>
</head>
<body>
    <form action="/login" method="POST">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Sign In</button>
    </form>
    {{ extra_scripts|safe }}
</body>
</html>'''
    
    def _fallback_error(self, message):
        """备用错误模板"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error</title>
</head>
<body>
    <p>{message}</p>
    <a href="javascript:history.back()">Go back</a>
    {{ extra_scripts|safe }}
</body>
</html>'''
    
    def reload_template(self, name):
        """重新加载模板（热更新）"""
        if name in self._cache:
            del self._cache[name]
        return self._read_template(name)
