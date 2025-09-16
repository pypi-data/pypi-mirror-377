import os
import urllib3
import functools
import platform
import subprocess
from log import log
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
        self.__platform = platform.system()
        if self.__platform == "linux":
            log.info(f"Current platform is {self.__platform}.")
        else:
            raise RuntimeError(f"Currently do not support {self.__platform} only support linux.")
        try:
            rs=self.exec_command(f"mkdir -p {home}")
            if rs.exit_code != 0:
                raise RuntimeError(f"failed to create home directory {home}, error message is {rs.stderr}")
            self.__home=home
        except Exception as e:
            log.error(f"failed to create home directory {home}, error message is {e}")
            raise e

    @enter_and_leave_function
    def exec_command(self, command):
        log.info(f"begin to exec command {command}")
        try:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            log.info(f"stdout is {result.stdout}, stderr is {result.stderr}, exit_code is {result.returncode}")
            rs = ExecResult(stdout=result.stdout, stderr=result.stderr, exit_code=result.returncode)
            return rs
        except subprocess.CalledProcessError as e:
            log.warning(f"failed to run command {command},stderr is {e.stderr}, exit_code is {e.returncode}")
            rs = ExecResult(stdout=e.stdout, stderr=e.stderr, exit_code=e.returncode)
            return rs

    @enter_and_leave_function
    def git_clone(self,repo_url,branch,dest_path):
        try:
            if os.path.exists(dest_path):
                if os.path.isdir(os.path.join(dest_path, '.git')):
                    log.warn(f"dest_path '{dest_path}' already exist and it is git repos.")
                    return False
                else:
                    log.warn(f"dest_path '{dest_path}' already exist but it is not git repos.")
                    return False

            parent_dir = os.path.dirname(dest_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            repo = Repo.clone_from(
                url=repo_url,
                to_path=dest_path,
                branch=branch
            )

            if repo.bare:
                log.warn("failed to git clone but create empty dir")
                return False

            current_branch = repo.active_branch.name
            if current_branch != branch:
                log.warn(f"git clone successful but branch is: {current_branch}, expected: {branch}")
                return False
            log.info(f"git clone successful dest_path: {dest_path}\ncurrent branch: {current_branch}")
            return True

        except GitCommandError as e:
            log.warn(f"failed to run git command: {str(e)}")
            return False
        except Exception as e:
            log.warn(f"error : {str(e)}")
            return False