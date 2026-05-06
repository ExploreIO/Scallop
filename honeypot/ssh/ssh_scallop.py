import asyncio
import asyncssh
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import json
from datetime import datetime, timedelta
import random
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from commands.executor import CommandExecutor
from filesystem import VirtualFS

# 日志文件
LOG_FILE = Path("logs/honeypot.log")
# 登录时间记录文件
LOGIN_TIME_FILE = Path("logs/.last_login")
# 全局变量：存储捕获的密码
captured_password = ''
# 全局虚拟文件系统（所有连接共享）
global_vfs = VirtualFS()
# 命令执行器（注入 VFS）
cmd_executor = CommandExecutor(vfs=global_vfs)

def log_attack(ip, username, password, commands, action='session_end'):
    """记录攻击行为"""
    log_entry = {
        'time': datetime.now().isoformat(),
        'ip': ip,
        'username': username,
        'password': password,
        'commands': commands,
        'action': action
    }
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        f.flush()  # 立即写入磁盘
    print(f"[LOG] {action} - {ip} - {username}:{password} - {len(commands)} commands")


def get_last_login_info():
    """获取上次登录信息"""
    if LOGIN_TIME_FILE.exists():
        try:
            with open(LOGIN_TIME_FILE, 'r') as f:
                data = json.load(f)
                return data.get('time'), data.get('ip', '10.0.0.1')
        except:
            pass
    
    # 首次登录或文件损坏，使用一个合理的默认时间
    # 模拟服务器已经运行了一段时间，有历史登录记录
    now = datetime.now()
    default_time = now - timedelta(days=random.randint(2, 5), hours=random.randint(1, 12))
    return default_time.strftime("%a %b %d %H:%M:%S %Y"), '10.0.0.1'


def save_login_info(ip):
    """保存本次登录信息供下次使用"""
    now = datetime.now()
    data = {
        'time': now.strftime("%a %b %d %H:%M:%S %Y"),
        'ip': ip
    }
    with open(LOGIN_TIME_FILE, 'w') as f:
        json.dump(data, f)


def format_login_time(time_str):
    """格式化登录时间"""
    return time_str


class HoneypotHandler(asyncssh.SSHServer):
    """SSH 蜜罐处理器"""
    
    def begin_auth(self, username):
        """开始认证"""
        return True
    
    def password_auth_supported(self):
        """支持密码认证"""
        return True
    
    def validate_password(self, username, password):
        """验证密码 - 蜜罐接受所有密码"""
        global captured_password
        print(f"[*] 登录尝试: {username}:{password}")
        captured_password = password  # 保存真实密码
        return True


async def handle_client(process):
    """处理客户端连接"""
    global captured_password
    try:
        peername = process.get_extra_info('peername', ('unknown', 0))
        ip = peername[0] if isinstance(peername, tuple) else 'unknown'
        username = process.get_extra_info('username', 'root')
        password = captured_password if captured_password else 'unknown'
        commands = []
        
        print(f"[+] 新连接: {ip} - {username}")
        
        # 记录登录成功
        log_attack(ip, username, password, commands, 'login_success')
        
        # 获取上次登录信息（真实服务器行为）
        last_login_time, last_login_ip = get_last_login_info()
        
        # 发送欢迎信息
        welcome = (
            f"Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-91-generic x86_64)\n"
            f"\n"
            f"Last login: {last_login_time} from {last_login_ip}\n"
        )
        process.stdout.write(welcome)
        await process.stdout.drain()
        
        # 保存本次登录信息
        save_login_info(ip)
        
        while True:
            process.stdout.write(f"{username}@server:~$ ")
            await process.stdout.drain()
            
            try:
                cmd = await process.stdin.readline()
            except asyncssh.BreakReceived:
                print(f"[+] 收到 Break 信号，关闭连接")
                log_attack(ip, username, password, commands, 'session_end')
                process.close()
                return
            
            if not cmd:
                break
            
            cmd = cmd.strip()
            commands.append(cmd)
            
            if cmd == 'exit' or cmd == 'logout':
                process.stdout.write("logout\n")
                await process.stdout.drain()
                log_attack(ip, username, password, commands, 'session_end')
                process.close()
                return
            
            # 执行命令
            if cmd:
                parts = cmd.split()
                cmd_name = parts[0]
                cmd_args = parts[1] if len(parts) > 1 else None
                output = cmd_executor.execute(cmd_name, cmd_args)
            else:
                output = ""
            
            process.stdout.write(output)
            await process.stdout.drain()
            
            # 实时记录每条命令
            log_attack(ip, username, password, [cmd], 'command')
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


def generate_ssh_key():
    """生成 SSH 密钥"""
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # 保存私钥
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    with open('ssh_key', 'wb') as f:
        f.write(private_pem)
    
    print("[*] SSH 密钥生成完成")

async def main():
    print("SSH 蜜罐运行中，端口 2222...")
    
    # 自动生成密钥（如果不存在）
    if not Path('ssh_key').exists():
        print("[*] 检测到缺少 SSH 密钥，正在生成...")
        generate_ssh_key()
    
    await asyncssh.create_server(
        lambda: HoneypotHandler(),
        '0.0.0.0',
        2222,
        server_host_keys=['ssh_key'],
        process_factory=handle_client,
        server_version='OpenSSH_8.9p1 Ubuntu-3ubuntu0.6'
    )
    
    await asyncio.Event().wait()

asyncio.run(main())
