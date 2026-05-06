from commands.base import BaseCommand


class UnameCommand(BaseCommand):
    """uname 命令"""
    
    def execute(self, args=None) -> str:
        if args == '-a':
            return "Linux server 5.15.0-91-generic #101-Ubuntu SMP Tue Nov 14 13:30:08 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux\n"
        else:
            return "Linux\n"
