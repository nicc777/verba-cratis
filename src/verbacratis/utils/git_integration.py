"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import os
from git import Repo
from git import Git
from pathlib import Path
import traceback
import shutil
import tempfile
import random, string
from verbacratis.utils.file_io import create_tmp_dir


def random_word(length: int=16):
    letters = '{}{}{}'.format(
        string.ascii_lowercase,
        string.ascii_uppercase,
        string.digits
    )
    return ''.join(random.choice(letters) for i in range(length))


def git_clone_checkout_and_return_list_of_files(
    git_clone_url: str,
    branch: str='main',
    target_dir: str=None,
    ssh_private_key_path: str=None,
    set_no_verify_ssl: bool=False
)->str:
    """Clone a Git repository, and check out a branch

    Args:
        git_clone_url: A string containing the Git repository clone URL, for example `git@github.com:nicc777/verba-cratis-test-infrastructure.git`
        branch: String containing the branch name to check out. Default is `main`
        target_dir: A string containing the target directory. Default is `None` in which case a random temporary directory will be created and returned
        ssh_private_key_path: A string containing the SSH private key to use. Optional, and if value is `None`, the default transport (HTTPS) will be used.
        set_no_verify_ssl: A boolean that will not check SSL certificates if set to True (default=`False`). Useful when using self-signed certificates, but use with caution!!

    Returns:
        A string to the location of the cloned repository.

    Raises:
        Exception: In the event of an error
    """

    if target_dir is None:
        target_dir = create_tmp_dir(sub_dir=random_word())

    if ssh_private_key_path is not None:
        git_ssh_cmd = 'ssh -i {}'.format(ssh_private_key_path)
        Repo.clone_from(url=git_clone_url, to_path=target_dir, env=dict(GIT_SSH_COMMAND=git_ssh_cmd), branch=branch)
    elif set_no_verify_ssl is True:
        Repo.clone_from(url=git_clone_url, to_path=target_dir, env=dict(GIT_SSL_NO_VERIFY='1'), branch=branch)
    else:
        Repo.clone_from(git_clone_url, target_dir, branch=branch)

    return target_dir


def git_clone_checkout_and_return_list_of_files(
    git_clone_url: str,
    branch: str='main',
    relative_start_directory: str='/',
    include_files_regex: tuple=('*.yml$', '*.yaml$',),
    target_dir: str='/tmp',
    ssh_private_key_path: str=None,
    set_no_verify_ssl: bool=False
)->list:
    """Parse files from a Git repository matching a file pattern withing a branch and directory to return a SystemConfigurations instance
    """
    files_found = list()

    if git_clone_checkout_and_return_list_of_files(git_clone_url=git_clone_url, branch=branch, target_dir=target_dir) is True:
        pass

    # TODO Implement
    # 1) Walk and get all the files from the start directory matching the include_files_regex

    return files_found
