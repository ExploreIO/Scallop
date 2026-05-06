from commands.base import BaseCommand
from datetime import datetime


class DateCommand(BaseCommand):
    """date 命令"""
    
    def execute(self, args=None) -> str:
        now = datetime.now()
        return now.strftime("%a %b %d %H:%M:%S %Z %Y\n")
