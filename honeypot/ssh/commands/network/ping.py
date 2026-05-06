from commands.base import BaseCommand


class PingCommand(BaseCommand):
    """ping 命令"""
    
    def execute(self, args=None) -> str:
        if not args:
            return "ping: usage error: Destination address required\n"
        target = args.split()[-1]
        return (
            f"PING {target} (93.184.216.34) 56(84) bytes of data.\n"
            f"64 bytes from {target} (93.184.216.34): icmp_seq=1 ttl=56 time=14.2 ms\n"
            f"64 bytes from {target} (93.184.216.34): icmp_seq=2 ttl=56 time=14.5 ms\n"
            f"64 bytes from {target} (93.184.216.34): icmp_seq=3 ttl=56 time=14.1 ms\n"
            f"--- {target} ping statistics ---\n"
            f"3 packets transmitted, 3 received, 0% packet loss, time 2003ms\n"
        )
