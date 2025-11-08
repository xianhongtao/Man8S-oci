import os

from mbctl.resources import copy_resdir_file_to_target_file


def shell_container(name: str, exec_cmd_list: list[str] = []) -> None:
    """在指定的容器中打开一个 shell"""

    # 如果没有提供命令，则默认使用 /bin/busybox sh
    if exec_cmd_list == []:
        exec_cmd_list = ["/bin/busybox", "sh"]
    # 生成一个临时文件
    script_location = "/tmp/man8shell.sh"
    copy_resdir_file_to_target_file("mbctl.resources.utils", "man8shell.sh", script_location)
    args = ["/bin/bash", script_location, name] + exec_cmd_list
    os.execvp(args[0], args)
