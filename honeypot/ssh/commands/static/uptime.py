from commands.base import BaseCommand
import random
from datetime import datetime


class UptimeCommand(BaseCommand):
    """uptime 命令"""
    
    def execute(self, args=None) -> str:
        now = datetime.now()
        hours = now.hour
        return f" {now.strftime('%H:%M:%S')} up {random.randint(10, 100)} days, {hours}:{random.randint(0, 59):02d},  1 user,  load average: 0.{random.randint(0, 99):02d}, 0.{random.randint(0, 49):02d}, 0.{random.randint(0, 29):02d}\n"
