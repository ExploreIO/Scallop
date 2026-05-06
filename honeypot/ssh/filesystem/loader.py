from .file import File
from .directory import Directory


class FileSystemLoader:
    """虚拟文件系统加载器"""
    
    @staticmethod
    def build_default() -> Directory:
        """构建默认的 Ubuntu 用户目录结构"""
        root = Directory("/")
        
        # /home
        home_dir = Directory("home", owner="root", group="root")
        
        # /home/ubuntu
        ubuntu_dir = Directory("ubuntu")
        
        # 隐藏文件
        ubuntu_dir.add_child(File(
            ".bashrc",
            content=(
                "# ~/.bashrc: executed by bash(1) for non-login shells.\n"
                "\n"
                "# If not running interactively, don't do anything\n"
                "case $- in\n"
                "    *i*) ;;\n"
                "      *) return;;\n"
                "esac\n"
                "\n"
                "# set a fancy prompt\n"
                "PS1='${debian_chroot:+($debian_chroot)}\\u@\\h:\\w\\$ '\n"
                "\n"
                "# some more ls aliases\n"
                "alias ll='ls -alF'\n"
                "alias la='ls -A'\n"
                "alias l='ls -CF'\n"
            ),
            permissions="644"
        ))
        
        ubuntu_dir.add_child(File(
            ".profile",
            content=(
                "# ~/.profile: executed by the command interpreter for login shells.\n"
                "\n"
                "# if running bash\n"
                "if [ -n \"$BASH_VERSION\" ]; then\n"
                "    # include .bashrc if it exists\n"
                "    if [ -f \"$HOME/.bashrc\" ]; then\n"
                "        . \"$HOME/.bashrc\"\n"
                "    fi\n"
                "fi\n"
                "\n"
                "PATH=\"$HOME/bin:$HOME/.local/bin:$PATH\"\n"
            ),
            permissions="644"
        ))
        
        ubuntu_dir.add_child(File(
            ".bash_logout",
            content=(
                "# ~/.bash_logout: executed by bash(1) when login shell exits.\n"
                "\n"
                "# when leaving the console clear the screen to increase readability\n"
                "if [ \"$SHLVL\" = 1 ]; then\n"
                "    [ -x /usr/bin/clear_console ] && /usr/bin/clear_console -q\n"
                "fi\n"
            ),
            permissions="644"
        ))
        
        # /home/ubuntu/.ssh
        ssh_dir = Directory(".ssh", permissions="700")
        ssh_dir.add_child(File(
            "authorized_keys",
            content="",
            permissions="600"
        ))
        ubuntu_dir.add_child(ssh_dir)
        
        # /home/ubuntu/.cache
        cache_dir = Directory(".cache", permissions="700")
        ubuntu_dir.add_child(cache_dir)
        
        # /home/ubuntu/.config
        config_dir = Directory(".config", permissions="700")
        ubuntu_dir.add_child(config_dir)
        
        # /home/ubuntu/Documents
        docs_dir = Directory("Documents", permissions="755")
        ubuntu_dir.add_child(docs_dir)
        
        # /home/ubuntu/Downloads
        downloads_dir = Directory("Downloads", permissions="755")
        ubuntu_dir.add_child(downloads_dir)
        
        # 组装目录树
        home_dir.add_child(ubuntu_dir)
        root.add_child(home_dir)
        
        return root
