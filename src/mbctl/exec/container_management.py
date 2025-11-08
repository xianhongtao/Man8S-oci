import shutil
import os
from pathlib import Path

from mbctl.utils.man8log import logger
from mbctl.utils.man8config import config, ContainerTemplate, ContainerTemplateList


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


def remove_container(name: str) -> None:
    """删除指定的容器"""
    container_lib_root = Path(config["man8machines_path"]) / name
    container_system_root = Path(config["system_machines_path"]) / name
    container_nspawn_file = Path(config["system_nspawn_file_path"]) / f"{name}.nspawn"
    container_config_root = Path(config["man8machine_configs_path"]) / name
    container_storage_root = Path(config["man8machine_storage_path"]) / name

    targets = [
        ("库目录", container_lib_root),
        ("系统目录", container_system_root),
        ("nspawn 文件", container_nspawn_file),
        ("配置目录", container_config_root),
        ("存储目录", container_storage_root),
    ]

    existing = [(desc, p) for desc, p in targets if os.path.lexists(str(p))]
    if not existing:
        logger.error(f"容器 '{name}' 不存在。")
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
