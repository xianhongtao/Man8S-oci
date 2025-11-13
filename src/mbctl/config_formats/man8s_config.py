from mbctl.utils.man8config import config

from pathlib import Path
from typing import Optional
from mbctl.config_formats.env_file_tools import parse_env_file


# Man8SContainerInfo 是一个Man8S容器的基本信息。它通常由配置文件与用户的命令行参数共同指定，表达这个Man8S容器的基本属性。
class Man8SContainerInfo:

    def __init__(
        self,
        name: str,
        oci_image_url: Optional[str] = None,
        template: Optional[str] = None,
        ygg_address: Optional[str] = None,
    ):
        self.name = name
        self.oci_image_url = oci_image_url
        self.template = template
        self.ygg_address = ygg_address

        # user_defined_mount_point 用于添加用户自定义的挂载点配置。
        # 这个配置只是“用户期望设置的挂载点”，真正的挂载点需要在生成nspawn配置文件时处理。
        # 这个配置会被用于生成nspawn配置文件。
        # 实际是 mount_point -> mount_target 的列表。 point 指的是容器内的路径， target 指的是宿主机的路径。
        self.user_defined_mount_points: list[tuple[str, str]] = []

        self.container_dir = Path(config["man8machines_path"]) / self.name
        self.container_dir_str = str(self.container_dir)
        self.container_config_dir = Path(config["man8machine_configs_path"]) / self.name
        self.container_storage_dir = (
            Path(config["man8machine_storage_path"]) / self.name
        )

    @staticmethod
    def from_env_file_of_container(container_name: str):
        # 在加载之前，只是创建一个基本的basic_container_info方便后续操作，之后会丢掉。
        basic_container_info = Man8SContainerInfo(container_name)
        env_vars = parse_env_file(basic_container_info.get_container_man8env_config_path_str())

        name = env_vars.get("MAN8S_CONTAINER_NAME", container_name)
        oci_image_url = env_vars.get("MAN8S_CONTAINER_OCI_URL")
        template = env_vars.get("MAN8S_CONTAINER_TEMPLATE")
        ygg_address = env_vars.get("MAN8S_CONTAINER_YGG_ADDRESS")

        return Man8SContainerInfo(
            name=name,
            oci_image_url=oci_image_url,
            template=template,
            ygg_address=ygg_address,
        )

    # 添加用户自定义的挂载点的方便方法
    def add_user_defined_mount_point(self, source: str, target: str):
        self.user_defined_mount_points.append((source, target))

    # 这里都是一些方便函数。
    def get_container_storage_path(self, container_abs_path: Path) -> Path:
        # 将容器内的绝对路径映射到存储路径中的相对路径
        relative_path = container_abs_path.relative_to("/")
        return self.container_storage_dir / relative_path

    def get_container_path(self, container_abs_path: Path) -> Path:
        relative_path = container_abs_path.relative_to("/")
        return self.container_dir / relative_path

    def get_container_path_str(self, container_abs_path: str = "/") -> str:
        return str(self.get_container_path(Path(container_abs_path)))

    def get_container_storage_path_str(self, container_abs_path: str = "/") -> str:
        return str(self.get_container_storage_path(Path(container_abs_path)))

    def get_container_config_path(self, container_abs_path: Path) -> Path:
        # 将容器内的绝对路径映射到配置路径中的相对路径
        relative_path = container_abs_path.relative_to("/")
        return self.container_config_dir / relative_path

    def get_container_config_path_str(self, container_abs_path: str = "/") -> str:
        return str(self.get_container_config_path(Path(container_abs_path)))

    def get_container_man8env_config_path_str(self):
        return str(self.container_config_dir / "man8env.env")

    def get_container_system_nspawn_file_path_str(self):
        return str(Path(config["system_nspawn_file_path"]) / f"{self.name}.nspawn")

    def get_container_nspawn_config_path_str(self):
        return str(self.container_config_dir / "container.nspawn")

    def check_is_storage_path(self, path: str) -> bool:
        # 检查给定路径是否在容器的存储路径下
        try:
            storage_path = self.get_container_storage_path(Path(path))
            return Path(path).resolve().is_relative_to(storage_path.resolve())
        except ValueError:
            return False
