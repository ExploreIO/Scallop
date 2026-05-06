from commands.base import BaseCommand


class MvCommand(BaseCommand):
    """mv 命令"""
    
    def __init__(self, vfs=None):
        self.vfs = vfs
    
    def execute(self, args=None) -> str:
        if not self.vfs:
            return "bash: mv: virtual filesystem not available\n"
        if not args:
            return "mv: missing operand\n"
        parts = args.split()
        if len(parts) < 2:
            return "mv: missing destination file operand\n"
        src = self.vfs._resolve_path(parts[0])
        if not src:
            return f"mv: cannot stat '{parts[0]}': No such file or directory\n"
        parent = self.vfs._resolve_path(self.vfs.current_dir)
        if parent.has_child(parts[1]):
            return f"mv: cannot create regular file '{parts[1]}': File exists\n"
        parent.add_child(src)
        src_parent = self.vfs._resolve_path(self.vfs.current_dir)
        if src_parent.has_child(parts[0]):
            src_parent.remove_child(parts[0])
        return ""
