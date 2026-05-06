from commands.base import BaseCommand


class CatCommand(BaseCommand):
    """cat 命令"""
    
    def __init__(self, vfs=None):
        self.vfs = vfs
    
    def execute(self, args=None) -> str:
        if not self.vfs:
            return "bash: cat: virtual filesystem not available\n"
        
        if not args:
            return "cat: missing operand\n"
        return self.vfs.read_file(args)
