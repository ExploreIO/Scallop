from commands.base import BaseCommand


class CpCommand(BaseCommand):
    """cp 命令"""
    
    def __init__(self, vfs=None):
        self.vfs = vfs
    
    def execute(self, args=None) -> str:
        if not self.vfs:
            return "bash: cp: virtual filesystem not available\n"
        if not args:
            return "cp: missing operand\n"
        parts = args.split()
        if len(parts) < 2:
            return "cp: missing destination file operand\n"
        src = self.vfs._resolve_path(parts[0])
        if not src or not src.is_file():
            return f"cp: cannot stat '{parts[0]}': No such file or directory\n"
        parent = self.vfs._resolve_path(self.vfs.current_dir)
        if parent.has_child(parts[1]):
            return f"cp: cannot create regular file '{parts[1]}': File exists\n"
        from filesystem import File
        parent.add_child(File(parts[1], content=src.read()))
        return ""
