import inspect
from commands import get_command_class, get_all_commands


class CommandExecutor:
    """命令执行器"""
    
    def __init__(self, vfs=None):
        self.vfs = vfs
    
    def execute(self, cmd_name: str, args: str = None, context: dict = None) -> str:
        """执行命令"""
        cmd_class = get_command_class(cmd_name)
        
        if not cmd_class:
            return f"bash: {cmd_name}: command not found\n"
        
        # 检查是否需要 VFS 注入
        needs_vfs = self._command_needs_vfs(cmd_class)
        
        if needs_vfs and not self.vfs:
            return f"bash: {cmd_name}: virtual filesystem not available\n"
        
        # 创建命令实例（带或不带 VFS）
        if needs_vfs:
            cmd = cmd_class(vfs=self.vfs)
        else:
            cmd = cmd_class()
        
        return cmd.execute(args)
    
    def _command_needs_vfs(self, cmd_class) -> bool:
        """检查命令是否需要 VFS（通过检查构造函数是否接受 vfs 参数）"""
        try:
            sig = inspect.signature(cmd_class.__init__)
            return 'vfs' in sig.parameters
        except:
            return False
    
    def get_available_commands(self) -> list:
        """获取可用命令列表"""
        return list(get_all_commands().keys())
