import os
import shutil
import stat
import time
from pathlib import Path

import pandas as pd
import psutil


def bytes_conversion(size):
    """
    字节符号转换
    :param size: 字节大小（B）
    :return:
    """
    symbols = ('KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    prefix = dict()
    for i, s in enumerate(symbols, 1):  # 获取每个符号的字节数
        prefix[s] = 1 << i * 10
    for s in reversed(symbols):  # 判断文件大小所属的符号范围
        if int(size) >= prefix[s]:
            return '{:.2f} {}'.format(float(size) / prefix[s], s)
    return "{} B".format(size)


def get_mountpoints():
    """
    获取电脑中的磁盘驱动器
    :return: 驱动器列表
    """
    mountpoints = []
    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt':
            if 'cdrom' in part.opts or part.fstype == '':
                # skip cd-rom drives with no disk in it; they may raise
                # ENOENT, pop-up a Windows GUI error for a non-ready
                # partition or just hang.
                continue
        mountpoints.append(part.mountpoint)
    # 返回
    return mountpoints


def files_file_attribute(path: Path):
    """
    判断文件是否为隐藏文件或系统文件
    :param path: 文件路径
    :return: true:隐藏文件或系统文件, true:普通文件
    """
    # Linux操作系统
    if os.name == 'posix' and path.name[0] == '.':
        return True
    # Windows操作系统
    elif os.name == 'nt':
        import win32file
        import win32con
        file_flag = win32file.GetFileAttributesW(str(path))
        # 隐藏文件
        is_hiden = file_flag & win32con.FILE_ATTRIBUTE_HIDDEN
        # 系统文件
        is_system = file_flag & win32con.FILE_ATTRIBUTE_SYSTEM
        # 文件过滤
        if is_hiden or is_system:
            return True
    else:
        return False


def get_files(path: Path, hidden: bool = True):
    """
    获取目录下一级的文件信息
    :param path: 目录路径
    :param hidden: 是否过滤隐藏文件
    :return: 文件信息dataFrame
    """
    # 文件DataFrame
    files_dateFrame = pd.DataFrame(columns=['name', 'modified_date', 'type', 'size'])
    # 索引
    index = 0
    for file_path in path.iterdir():
        # 名称
        file_name = file_path.name
        # 过滤隐藏文件
        if files_file_attribute(file_path):
            continue
        # 修改日期
        modified_date = time.strftime("%Y-%m-%d %H:%M", time.localtime(file_path.stat().st_mtime))
        # 文件类型
        if file_path.is_file():
            file_type = 'file'
        else:
            file_type = 'folder'
        # 文件大小
        file_size = file_path.stat().st_size
        # 添加文件信息
        files_dateFrame.loc[index] = [file_name, modified_date, file_type, file_size]
        # 索引加1
        index = index + 1
    return files_dateFrame


def files_name_check(name):
    """
    检查文件/文件夹名称是否符合规范
    Args:
        name: 文件/文件夹名称
    """
    if name:
        return True
    else:
        return False


def files_exits(path):
    """
    路径path是否指向一个已存在的文件或目录:
    Args:
        path: 路径
    Returns: 是否存在
    """
    if path.exists():
        # 文件/文件夹存在
        return True
    else:
        # 文件/文件夹不存在
        return False


def files_file_create(path: Path, name: str):
    """
    创建文件
    'w' : open for writing, truncating the file first
    '+' : open a disk file for updating (reading and writing)
    打开一个文件用于读写。如果该文件已存在则打开文件，并从开头开始编辑，即原有内容会被删除。
    如果该文件不存在，创建新文件。
    Args:
        :param path: 文件路径
        :param name: 文件名称
    """
    # 创建文件
    file = open(str(path.joinpath(name)), mode='w')
    # 关闭文件
    file.close()


def files_folder_create(path: Path, name: str):
    """
    创建文件夹
    Args:
        path: 文件夹路径
        name: 文件夹名称
    如果 parents 为 true，任何找不到的父目录都会伴随着此路径被创建；它们会以默认权限被创建，而不考虑 mode 设置（模仿 POSIX 的 mkdir -p 命令）。
    如果 parents 为 false（默认），则找不到的父级目录会导致 FileNotFoundError 被抛出。
    如果 exist_ok 为 false（默认），则在目标已存在的情况下抛出 FileExistsError。
    """
    # 目录路径
    new_path = path.joinpath(name)
    # 创建目录
    new_path.mkdir(parents=True, exist_ok=True)


def remove_readonly(func, path, _):
    """清除只读属性并重新尝试删除"""
    path.chmod(stat.S_IWRITE)
    func(path)


def files_move(source_path: str, target_path: str):
    """
    移动文件
    Args:
        source_path: 源文件路径
        target_path: 目标目录路径
    Returns:
    """
    shutil.move(source_path, target_path)


def files_file_copy(source_path: str, target_path: str):
    """
    复制文件
    Args:
        source_path: 源文件路径
        target_path: 目标文件路径
    Returns:
    """
    shutil.copyfile(source_path, target_path)
    return


def files_folder_copy(source_path: str, target_path: str):
    """
    复制目录
    Args:
        source_path: 源目录路径
        target_path: 目标目录路径
    Returns:
    """
    shutil.copytree(source_path, target_path)
    return


def files_folder_size(path: Path) -> int:
    """
    Args:
        path: 文件夹路径
    Returns:文件夹大小（以字节为单位）
    """
    # 文件夹大小
    size = 0
    # 遍历文件夹
    for file in path.iterdir():
        if file.is_file():
            size += file.stat().st_size
        elif file.is_dir():
            size += files_folder_size(file)
    return size


def files_file_delete(path: Path):
    """
    删除文件
    Args:
        path: 文件路径
    Returns: 操作结果
    """
    # 删除文件
    # 如果 missing_ok 为False（默认），则如果路径不存在将会引发 FileNotFoundError。
    # 如果 missing_ok 为True，则 FileNotFoundError 异常将被忽略
    path.unlink(missing_ok=False)
    return


def files_folder_delete(path: Path):
    """
    删除文件或文件夹
    Args:
        path: 文件/文件夹路径
    Returns: 操作结果
    """
    # 删除文件夹
    shutil.rmtree(path, ignore_errors=False, onerror=remove_readonly)
    return


def file_delete(path: Path):
    """
    删除文件/文件夹
    :param path: 文件/文件夹路径
    :return:
    """
    if path.is_file():
        # 删除文件
        files_file_delete(path)
    elif path.is_dir():
        # 删除文件夹
        files_folder_delete(path)


def files_same_type(path1: Path, path2: Path):
    """
    判断两文件类型是否相同
    :param path1: 文件1路径
    :param path2: 文件2路径
    :return: True:两文件类型相同， False:两文件类型不同
    """
    if path1.is_file() and path2.is_file():
        return True
    elif path1.is_dir() and path2.is_dir():
        return True
    else:
        return False


def file_rename(old_path: Path, new_path: Path):
    """
    重命名文件/文件夹
    Args:
        old_path: 旧名称
        new_path: 新名称
    Returns: 操作结果
    """
    old_path.replace(new_path)
