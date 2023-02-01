"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

# TODO - Implement Git integration


def git_clone_checkout_and_return_list_of_files(git_clone_url: str, branch: str='main', target_dir: str='/tmp')->bool:
    # TODO Implement
    # 1) Clone the repo
    # 2) Checkout the branch
    return False


def git_clone_checkout_and_return_list_of_files(
    git_clone_url: str,
    branch: str='main',
    relative_start_directory: str='/',
    include_files_regex: tuple=('*.yml$', '*.yaml$',),
    target_dir: str='/tmp'
)->list:
    """Parse files from a Git repository matching a file pattern withing a branch and directory to return a SystemConfigurations instance
    """
    files_found = list()

    if git_clone_checkout_and_return_list_of_files(git_clone_url=git_clone_url, branch=branch, target_dir=target_dir) is True:
        pass

    # TODO Implement
    # 1) Walk and get all the files from the start directory matching the include_files_regex

    return files_found
