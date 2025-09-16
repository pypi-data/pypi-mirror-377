import os
import shutil

import urllib3
import functools
import platform
import subprocess
from log import log
from typing import List, Optional, Set, Union
from git import Repo,GitCommandError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enter_and_leave_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if args:
            if kwargs:
                log.info(f"begin to run function {func.__name__},args is {args},kwargs is {kwargs}")
            else:
                log.info(f"begin to run function {func.__name__},args is {args}")
        else:
            if kwargs:
                log.info(f"begin to run function {func.__name__},kwargs is {kwargs}")
            else:
                log.info(f"begin to run function {func.__name__}")
        try:
            result = func(*args, **kwargs)
            log_str=f"finish run function {func.__name__},result type is {type(result)}, and result is {result}"
            log.info(log_str)
            return result
        except Exception as e:
            log.error(f"failed to run functon {func.__name__} error message is : {e}")
            raise e
    return wrapper

class ExecResult:
    def __init__(self,stdout,stderr,exit_code):
        self.stdout=stdout
        self.stderr=stderr
        self.exit_code=exit_code

class Server():
    def __init__(self,home="/home/my_home"):
        """
        初始化类实例，检查操作系统兼容性并创建指定的主目录

        参数:
            home: 主目录路径，默认为"/home/my_home"

        异常:
            RuntimeError: 当操作系统不支持或目录创建失败时抛出
        """
        # 检查操作系统平台
        self.__platform = platform.system()
        self.__validate_platform()

        # 初始化并验证主目录
        self.__home = self.__initialize_home_directory(home)

    def __initialize_home_directory(self, home: str) -> str:
        """
        初始化主目录，确保目录存在

        参数:
            home: 要创建的主目录路径

        返回:
            成功创建的主目录路径

        异常:
            RuntimeError: 当目录创建失败时抛出
        """
        try:
            # 优先使用Python内置方法创建目录（更跨平台且安全）
            if not self.__directory_exists(home):
                log.info(f"开始创建主目录: {home}")
                self.__create_directory(home)

            # 验证目录是否成功创建
            if not self.__directory_exists(home):
                raise RuntimeError(f"主目录创建后验证失败: {home}不存在")

            log.info(f"主目录初始化成功: {home}")
            return home

        except Exception as e:
            error_msg = f"主目录创建失败: {str(e)}"
            log.error(error_msg)
            raise RuntimeError(error_msg) from e

    def __validate_platform(self) -> None:
        """验证操作系统是否为Linux，不支持则抛出异常"""
        if self.__platform == "Linux":
            log.info(f"当前操作系统: {self.__platform} (支持)")
        else:
            raise RuntimeError(
                f"不支持的操作系统: {self.__platform}，仅支持Linux"
            )

    def __create_directory(self, path: str) -> None:
        """使用Python内置方法创建目录（含父目录）"""
        try:
            # 使用exist_ok=True避免重复创建错误
            shutil.os.makedirs(path, exist_ok=True)
        except PermissionError:
            raise RuntimeError(f"权限不足，无法创建目录: {path}")
        except OSError as e:
            raise RuntimeError(f"系统错误，创建目录失败: {path}, 错误: {str(e)}")

    def __directory_exists(self, path: str) -> bool:
        """检查目录是否存在且为有效目录"""
        return shutil.os.path.exists(path) and shutil.os.path.isdir(path)

    @enter_and_leave_function
    def exec_command(self, command: Union[str, List[str]]) -> ExecResult:
        """
        执行系统命令并返回执行结果

        参数:
            command: 要执行的命令，可以是字符串或字符串列表
                     列表形式更安全，避免shell注入风险

        返回:
            ExecResult对象，包含命令执行的stdout、stderr和exit_code
        """
        try:
            # 执行命令，捕获 stdout 和 stderr
            # 使用shell=True时command可为字符串，否则应为列表
            shell = isinstance(command, str)
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=shell,
                encoding='utf-8',
                errors='replace'  # 处理编码错误
            )

            # 返回封装的结果对象
            return ExecResult(
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode
            )

        except Exception as e:
            # 处理执行过程中的异常（如命令不存在等）
            return ExecResult(
                stdout="",
                stderr=f"执行命令时发生异常: {str(e)}",
                exit_code=-1
            )

    @enter_and_leave_function
    def git_clone(self, repo_url: str, branch: str, dest_path: str) -> bool:
        """
        克隆指定Git仓库的指定分支到目标路径

        功能说明：
            1. 检查目标路径是否已存在，避免覆盖现有文件
            2. 自动创建目标路径的父目录（如果不存在）
            3. 克隆指定分支到目标路径并验证结果
            4. 验证克隆后的仓库分支是否与预期一致

        参数：
            repo_url: Git仓库的URL地址（例如：https://github.com/example/repo.git）
            branch: 需要克隆的分支名称（例如：main、dev）
            dest_path: 本地目标路径，克隆后的仓库将存储在此路径下

        返回：
            bool: 克隆成功且验证通过返回True，否则返回False

        异常处理：
            捕获Git命令执行异常和其他通用异常，并记录警告日志
        """
        try:
            # 检查目标路径是否已存在
            if os.path.exists(dest_path):
                # 检查是否为已存在的Git仓库
                git_dir = os.path.join(dest_path, '.git')
                if os.path.isdir(git_dir):
                    log.warn(f"目标路径 '{dest_path}' 已存在且为Git仓库，无法克隆")
                    return False
                else:
                    log.warn(f"目标路径 '{dest_path}' 已存在但不是Git仓库，无法克隆")
                    return False

            # 确保父目录存在
            parent_dir = os.path.dirname(dest_path)
            if parent_dir and not os.path.exists(parent_dir):
                # exist_ok=True 避免多线程场景下的目录创建冲突
                os.makedirs(parent_dir, exist_ok=True)
                log.debug(f"已自动创建父目录: {parent_dir}")

            # 执行克隆操作
            log.info(f"开始克隆仓库: {repo_url} 分支: {branch} 到路径: {dest_path}")
            repo = Repo.clone_from(
                url=repo_url,
                to_path=dest_path,
                branch=branch
            )

            # 验证仓库是否为裸仓库（异常情况）
            if repo.bare:
                log.warn(f"克隆失败，创建了裸仓库: {dest_path}")
                return False

            # 验证当前分支是否与预期一致
            current_branch = repo.active_branch.name
            if current_branch != branch:
                log.warn(
                    f"克隆成功但分支不匹配 - "
                    f"实际分支: {current_branch}, 预期分支: {branch}"
                )
                return False

            # 所有验证通过
            log.info(
                f"克隆成功 - "
                f"目标路径: {dest_path}, 当前分支: {current_branch}"
            )
            return True

        except GitCommandError as e:
            log.warn(f"Git命令执行失败: {str(e)}")
            return False
        except Exception as e:
            log.warn(f"克隆过程中发生未知错误: {str(e)}")
            return False

    @enter_and_leave_function
    def find_all_file(
            self,
            root_dir: str,
            suffix: Optional[str] = None,
            with_suffix: bool = True,
            recursive: bool = True,
            exclude_dirs: Optional[List[str]] = None,
            exclude_files: Optional[List[str]] = None,
            absolute_path: bool = True,
            only_file_name: bool = False
    ) -> List[str]:
        """
        查找指定目录下符合条件的所有文件名称或路径

        参数:
            root_dir: 查找的根目录
            suffix: 文件名后缀过滤（如".txt"或"txt"），为None则不过滤
            with_suffix: 是否包含文件后缀（仅在返回文件名时生效）
            recursive: 是否递归查找子目录
            exclude_dirs: 要排除的目录名称列表（支持全称匹配）
            exclude_files: 要排除的文件名称列表（支持全称匹配）
            absolute_path: 是否返回绝对路径（仅在不返回纯文件名时生效）
            only_file_name: 是否只返回文件名（不包含路径）

        返回:
            符合条件的文件路径或名称列表（去重后按查找顺序排列）
        """
        # 处理排除列表（转为集合提高查找效率）
        exclude_dirs_set: Set[str] = set(exclude_dirs) if exclude_dirs else set()
        exclude_files_set: Set[str] = set(exclude_files) if exclude_files else set()

        # 验证根目录有效性
        root_dir = os.path.abspath(root_dir)
        if not os.path.isdir(root_dir):
            raise NotADirectoryError(f"根目录不存在或不是目录: {root_dir}")

        # 统一处理后缀格式（确保以点开头）
        if suffix is not None and not suffix.startswith('.'):
            suffix = f'.{suffix}'

        result: List[str] = []
        seen: Set[str] = set()  # 用于去重

        # 遍历目录
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # 排除指定目录（修改dirnames影响os.walk递归行为）
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs_set]

            for filename in filenames:
                # 排除指定文件
                if filename in exclude_files_set:
                    continue

                # 后缀过滤
                if suffix is not None and not filename.endswith(suffix):
                    continue

                # 处理文件名（是否包含后缀）
                processed_name = filename if with_suffix else os.path.splitext(filename)[0]

                # 根据参数决定返回内容
                if only_file_name:
                    # 只返回文件名（去重）
                    if processed_name not in seen:
                        seen.add(processed_name)
                        result.append(processed_name)
                else:
                    # 构建文件路径
                    full_path = os.path.join(dirpath, filename)
                    # 处理路径格式（绝对/相对）
                    if absolute_path:
                        display_path = os.path.abspath(full_path)
                    else:
                        display_path = os.path.relpath(full_path, root_dir)

                    # 处理路径中的文件名是否包含后缀
                    if not with_suffix:
                        # 只移除文件名部分的后缀，保留路径结构
                        dir_part, file_part = os.path.split(display_path)
                        display_path = os.path.join(dir_part, os.path.splitext(file_part)[0])

                    # 路径去重
                    if display_path not in seen:
                        seen.add(display_path)
                        result.append(display_path)

            # 非递归模式：只处理顶层目录
            if not recursive:
                break

        return result