from commands.base import BaseCommand


class HostnameCommand(BaseCommand):
    """hostname 命令"""
    
    def execute(self, args=None) -> str:
        return "server\n"
