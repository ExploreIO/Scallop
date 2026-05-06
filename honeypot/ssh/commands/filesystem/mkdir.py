from commands.base import BaseCommand
from filesystem import Directory


class MkdirCommand(BaseCommand):
    """mkdir 命令"""
    
    def __init__(self, vfs=None):
        self.vfs = vfs
    
    def execute(self, args=None) -> str:
        if not self.vfs:
            return "bash: mkdir: virtual filesystem not available\n"
        if not args:
            return "mkdir: missing operand\n"
        parent = self.vfs._resolve_path(self.vfs.current_dir)
        if not parent or not parent.is_directory():
            return f"mkdir: cannot create directory '{args}': No such file or directory\n"
        if parent.has_child(args):
            return f"mkdir: cannot create directory '{args}': File exists\n"
        parent.add_child(Directory(args))
        return ""
