from commands.base import BaseCommand
from filesystem import File


class TouchCommand(BaseCommand):
    """touch 命令"""
    
    def __init__(self, vfs=None):
        self.vfs = vfs
    
    def execute(self, args=None) -> str:
        if not self.vfs:
            return "bash: touch: virtual filesystem not available\n"
        if not args:
            return "touch: missing operand\n"
        parent = self.vfs._resolve_path(self.vfs.current_dir)
        if not parent or not parent.is_directory():
            return f"touch: cannot touch '{args}': No such file or directory\n"
        if parent.has_child(args):
            return ""
        parent.add_child(File(args, content=""))
        return ""
