from commands.base import BaseCommand


class CdCommand(BaseCommand):
    """cd 命令"""
    
    def __init__(self, vfs=None):
        self.vfs = vfs
    
    def execute(self, args=None) -> str:
        if not self.vfs:
            return "bash: cd: virtual filesystem not available\n"
        if not args:
            self.vfs.current_dir = "/home/ubuntu"
            return ""
        node = self.vfs._resolve_path(args)
        if not node:
            return f"bash: cd: {args}: No such file or directory\n"
        if not node.is_directory():
            return f"bash: cd: {args}: Not a directory\n"
        self.vfs.current_dir = self.vfs._normalize_path(args)
        return ""
