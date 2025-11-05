import os
import shutil


def empty_and_copy_all_contents(src_dir: str, dst_dir: str):
    """
    递归复制 src_dir 下的所有文件和文件夹到 dst_dir 中。
    - src_dir 必须是一个 **目录** 而非 文件。
    - dst_dir 必须是一个 **目录** 而非 文件。或者dst_dir 不存在，则会创建之，如果 dst_dir 已存在，则会被删除然后重新创建。
    - 如果 src_dir 是一个符号链接，那么它必须是一个目标合法的、指向一个目录的符号链接。

    此命令等价于 shell 命令: rm -rf dst_dir/* && cp -a src_dir/* dst_dir/，
    会清空 dst_dir 中所有已有的内容，对于符号链接，会复制链接本身而不是链接指向的内容。

    参数:
        src_dir (str): 源目录路径
        dst_dir (str): 目标目录路径
    """


    # 检查 src_dir 是否存在且是目录或符号链接到目录
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"源目录不存在: {src_dir}")
    if not os.path.isdir(src_dir):
        raise NotADirectoryError(f"源路径不是目录: {src_dir}")

    # 如果 dst_dir 存在，则删除。
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)

    # 复制 src_dir -> dst_dir，保留符号链接本身
    shutil.copytree(src_dir, dst_dir, symlinks=True)
