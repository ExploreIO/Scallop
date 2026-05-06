from commands.base import BaseCommand


class IdCommand(BaseCommand):
    """id 命令"""
    
    def execute(self, args=None) -> str:
        return "uid=1000(ubuntu) gid=1000(ubuntu) groups=1000(ubuntu),4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev)\n"
