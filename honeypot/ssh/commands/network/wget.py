from commands.base import BaseCommand


class WgetCommand(BaseCommand):
    """wget 命令"""
    
    def execute(self, args=None) -> str:
        if not args:
            return "wget: missing URL\n"
        return f"--2026-05-05 01:00:00--  {args}\nResolving {args}... failed: Name or service not known.\nwget: unable to resolve host address\n"
