# 根据存储的配置重新创建一个Man8s容器的rootfs，不会再询问挂载点等信息。
# 一般用于容器升级。

import os
from mbctl.get_bundle.oci_convert import oci_convert_protect_dirs
from mbctl.init_system.man8s_add_initsystem import install_init_system_to_machine
from mbctl.config_formats.man8s_config import Man8SContainerInfo
from mbctl.config_formats.oci_config import OCIConfig
from mbctl.exec.create_nspawn_container_from_oci_url import (
    generate_env_config_from_configs,
    generate_nspawn_config_from_configs,
    write_env_file,
)
from mbctl.get_bundle.get_oci import fetch_oci_to_rootfs
from mbctl.utils.file_operate import empty_and_copy_all_contents
from mbctl.utils.man8log import logger
from mbctl.utils.man8config import config

from .container_management import remove_container, ContainerPart

def recreate_man8s_container_rootfs(
    man8s_container_info: Man8SContainerInfo,
):
    # 1. 删除已有的容器 rootfs 目录（如果存在的话）
    remove_container(
        man8s_container_info.name,
        parts=[
            ContainerPart.LIBRARY,
            ContainerPart.SYSTEM,
        ],
    )

    # 2. 从 OCI 镜像重新创建容器 rootfs
    if not man8s_container_info.oci_image_url:
        raise ValueError(
            f"容器 '{man8s_container_info.name}' 缺少 OCI 镜像 URL，无法重新创建 rootfs。"
        )
    fetch_oci_to_rootfs(
        man8s_container_info.oci_image_url, man8s_container_info.container_dir_str
    )

    # 3. 安装 man8s-init
    install_init_system_to_machine(man8s_container_info.container_dir_str)

    # 4：在 system_machines_path 下创建指向容器目录的符号链接，正式启用容器。
    os.symlink(
        man8s_container_info.container_dir_str,
        os.path.join(config["system_machines_path"], man8s_container_info.name),
    )

    # 5：对容器rootfs后处理，保护/run和/tmp目录
    protect_dir_result = oci_convert_protect_dirs(
        man8s_container_info.container_dir_str
    )
    for dir in protect_dir_result:
        logger.info(f"已保护容器内目录 {dir} -> {dir}.man8sprotected 。")

