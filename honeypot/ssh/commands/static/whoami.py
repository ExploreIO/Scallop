from commands.base import BaseCommand


class WhoamiCommand(BaseCommand):
    """whoami 命令"""
    
    def execute(self, args=None) -> str:
        return "ubuntu\n"
