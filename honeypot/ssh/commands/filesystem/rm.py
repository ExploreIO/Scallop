from commands.base import BaseCommand


class RmCommand(BaseCommand):
    """rm 命令"""
    
    def __init__(self, vfs=None):
        self.vfs = vfs
    
    def execute(self, args=None) -> str:
        if not self.vfs:
            return "bash: rm: virtual filesystem not available\n"
        if not args:
            return "rm: missing operand\n"
        parent = self.vfs._resolve_path(self.vfs.current_dir)
        if not parent or not parent.is_directory():
            return f"rm: cannot remove '{args}': No such file or directory\n"
        if not parent.has_child(args):
            return f"rm: cannot remove '{args}': No such file or directory\n"
        parent.remove_child(args)
        return ""
