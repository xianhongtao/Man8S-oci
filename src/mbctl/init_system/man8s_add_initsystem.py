#!/usr/bin/env python3
"""
man8s_add_initsystem.py

相当于 man8s-add-initsystem.sh 的 Python 版本

用法: python3 man8s_add_initsystem.py <MACHINE_PATH>

此脚本会将主机的 busybox 复制到 <MACHINE_PATH>/bin，确保存在指向 busybox 的 `sh` 链接，
将 man8lib 的 man8s-init 脚本复制到 <MACHINE_PATH>/man8s-init，并将 udhcpc 的默认脚本安装到
<MACHINE_PATH>/usr/share/udhcpc/default.script。
"""

from __future__ import annotations

import os
import shutil
import stat
import sys
from pathlib import Path

from mbctl.utils.man8config import config
from mbctl.utils.man8log import logger
from mbctl.resources import copy_resdir_content_to_target_folder, get_file_content_as_str


HOST_BUSYBOX = Path(config["host_busybox_path"])

# 向指定的机器路径安装 init 系统，如果已经存在则覆盖。相当于重新安装init系统。
def install_init_system_to_machine(machine_path_str: str) -> None:
    machine_path = Path(machine_path_str).resolve()

    bin_dir = machine_path / "bin"
    # sbin_dir = machine_path / "sbin"
    man8s_init_dir = machine_path / "man8s-init"
    udhcpc_target_dir = machine_path / "usr" / "share" / "udhcpc"

    # 1. 确保目标目录存在
    for d in (bin_dir, udhcpc_target_dir, man8s_init_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 2. 复制 busybox
    if not HOST_BUSYBOX.exists():
        raise FileNotFoundError(f"主机上的 busybox 未找到：{HOST_BUSYBOX}")

    dest_busybox = bin_dir / "busybox"
    shutil.copy2(HOST_BUSYBOX, dest_busybox)
    # 保留可执行位
    dest_busybox.chmod(dest_busybox.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # 3. 确保 /bin/sh 指向 busybox 的符号链接
    sh_link = bin_dir / "sh"
    # 通常情况下，容器会提供自己的 /bin/sh，如果容器没有提供，则创建一个指向 busybox 的链接。
    if not sh_link.exists():
        sh_link.symlink_to("busybox")

    # 4. 复制 man8lib/man8s-init/* 到 <machine>/man8s-init/。如果man8s_init_dir存在，则摧毁重建。
    if man8s_init_dir.exists():
        logger.info(f"删除 {man8s_init_dir} 处已存在的 man8s-init 目录")
        shutil.rmtree(man8s_init_dir)
    copy_resdir_content_to_target_folder("mbctl.resources.man8s-init", man8s_init_dir)

    # 5. 安装 udhcpc-default.script。如果存在则覆盖。
    if udhcpc_target_dir.exists():
        logger.info(f"删除 {udhcpc_target_dir} 处已存在的 udhcpc 目录")
        shutil.rmtree(udhcpc_target_dir)
    copy_resdir_content_to_target_folder("mbctl.resources.busybox-networking", udhcpc_target_dir)

    # 6. 确保 udhcpc/default.script 、 /man8s-init/00-init.sh 可执行
    for script in (udhcpc_target_dir / "default.script", man8s_init_dir / "00-init.sh"):
        script.chmod(script.stat().st_mode | stat.S_IEXEC)
