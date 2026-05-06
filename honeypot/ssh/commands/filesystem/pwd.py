from commands.base import BaseCommand


class PwdCommand(BaseCommand):
    """pwd 命令"""
    
    def __init__(self, vfs=None):
        self.vfs = vfs
    
    def execute(self, args=None) -> str:
        if not self.vfs:
            return "bash: pwd: virtual filesystem not available\n"
        return self.vfs.current_dir + "\n"
