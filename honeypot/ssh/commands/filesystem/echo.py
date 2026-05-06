from commands.base import BaseCommand
from filesystem import File


class EchoCommand(BaseCommand):
    """echo 命令"""
    
    def __init__(self, vfs=None):
        self.vfs = vfs
    
    def execute(self, args=None) -> str:
        if not args:
            return "\n"
        
        if '>' in args:
            parts = args.split('>')
            content = parts[0].strip()
            filename = parts[1].strip()
            
            if not self.vfs:
                return f"bash: echo: virtual filesystem not available\n"
            
            parent = self.vfs._resolve_path(self.vfs.current_dir)
            if not parent or not parent.is_directory():
                return f"bash: echo: {filename}: No such file or directory\n"
            
            if parent.has_child(filename):
                existing = parent.get_child(filename)
                if existing.is_file():
                    existing.content = content
            else:
                parent.add_child(File(filename, content=content))
            return ""
        else:
            return args + "\n"
