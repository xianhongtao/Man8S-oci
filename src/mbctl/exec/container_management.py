import shutil
import os
from pathlib import Path
from enum import Enum, auto
from typing import List, Optional

from mbctl.utils.man8log import logger
from mbctl.utils.man8config import config, ContainerTemplate, ContainerTemplateList

# ContainerPart 枚举并扩展 remove_container 支持按部分删除
class ContainerPart(Enum):
    """容器可删除的模块枚举"""
    LIBRARY = auto()     # 库目录
    SYSTEM = auto()      # 系统目录
    NSPAWN = auto()      # nspawn 文件
    CONFIG = auto()      # 配置目录
    STORAGE = auto()     # 存储目录

def check_and_delete(target: str) -> bool:
    """检查路径是否存在，如果存在则删除，返回是否删除成功"""

    if os.path.lexists(target):
        try:
            if os.path.isdir(target) and not os.path.islink(target):
                shutil.rmtree(target)
                logger.info(f"Existing directory '{target}' removed.")
            else:
                os.remove(target)
                logger.info(f"Existing file or symlink '{target}' removed.")
            return True
        except Exception as e:
            logger.error(f"Error removing '{target}': {e}")
            return False
    return True

def check_container_running(name: str) -> bool:
    """检查指定的容器是否正在运行，以后应该模块化使用machinectl的API。"""
    # .#PTNginx1.lck
    container_lck_file_location = Path(config["man8machines_path"]) / f".#{name}.lck"
    return container_lck_file_location.exists()


def remove_container(name: str, parts: Optional[List[ContainerPart]] = None) -> None:
    """删除指定的容器或容器的指定部分
    parts 为 None 表示删除所有部分；否则只删除列表中指定的模块。
    """
    container_lib_root = Path(config["man8machines_path"]) / name
    container_system_root = Path(config["system_machines_path"]) / name
    container_nspawn_file = Path(config["system_nspawn_file_path"]) / f"{name}.nspawn"
    container_config_root = Path(config["man8machine_configs_path"]) / name
    container_storage_root = Path(config["man8machine_storage_path"]) / name

    # 映射枚举到描述与路径
    mapping = {
        ContainerPart.LIBRARY: ("库目录", container_lib_root),
        ContainerPart.SYSTEM: ("系统目录", container_system_root),
        ContainerPart.NSPAWN: ("nspawn 文件", container_nspawn_file),
        ContainerPart.CONFIG: ("配置目录", container_config_root),
        ContainerPart.STORAGE: ("存储目录", container_storage_root),
    }

    if parts is None:
        # 删除所有部分
        targets = list(mapping.values())
    else:
        # 验证并构建只包含指定部分的目标列表
        invalid = [p for p in parts if not isinstance(p, ContainerPart) or p not in mapping]
        if invalid:
            logger.error(f"无效的部分指定: {invalid}")
            return
        targets = [mapping[p] for p in parts]

    # 只保留实际存在的路径
    existing = [(desc, p) for desc, p in targets if os.path.lexists(str(p))]
    if not existing:
        if parts is None:
            logger.error(f"容器 '{name}' 不存在。")
        else:
            logger.error(f"容器 '{name}' 指定的部分不存在。")
        return
    else:
        if check_container_running(name):
            logger.error(f"容器 '{name}' 正在运行，无法删除。请先停止容器。")
            return

        deleted = []
        for desc, p in existing:
            if check_and_delete(str(p)):
                deleted.append(desc)

        if deleted:
            logger.info(f"容器 '{name}' 已删除: {', '.join(deleted)}。")


def clear_cache_dir() -> None:
    """清理临时缓存目录"""
    temp_dir = config["temp_dir"]
    check_and_delete(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    logger.info(f"临时缓存目录 '{temp_dir}' 已清理。")
