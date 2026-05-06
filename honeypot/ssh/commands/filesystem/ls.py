from commands.base import BaseCommand


class LsCommand(BaseCommand):
    """ls 命令"""
    
    def __init__(self, vfs=None):
        self.vfs = vfs
    
    def execute(self, args=None) -> str:
        if not self.vfs:
            return "bash: ls: virtual filesystem not available\n"
        
        if args == '-la' or args == '-al':
            return self.vfs.list_dir(show_all=True, show_long=True)
        elif args == '-a':
            return self.vfs.list_dir(show_all=True)
        elif args == '-l':
            return self.vfs.list_dir(show_long=True)
        else:
            return self.vfs.list_dir()
