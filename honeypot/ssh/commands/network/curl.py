from commands.base import BaseCommand


class CurlCommand(BaseCommand):
    """curl 命令"""
    
    def execute(self, args=None) -> str:
        if not args:
            return "curl: try 'curl --help' for more information\n"
        return f"curl: (6) Could not resolve host: {args.split()[-1]}\n"
