import os
from git import Repo
from git import Git
from pathlib import Path
import traceback
import shutil
import tempfile


def remove_tmp_dir_recursively(dir: str)->bool:
    try:
        os.remove(dir)
    except:
        traceback.print_exc()
    try:
        shutil.rmtree(dir)
        return True
    except:
        traceback.print_exc()
        return False


def create_tmp_dir(sub_dir: str)->str:
    tmp_dir = '{}{}{}'.format(tempfile.gettempdir(), os.sep, sub_dir)
    try:
        remove_tmp_dir_recursively(dir=tmp_dir)
        os.mkdir(tmp_dir)
    except:
        traceback.print_exc()
        return None
    return tmp_dir


repo_url = 'git@github.com:nicc777/verba-cratis-test-infrastructure.git'

home = str(Path.home())
default_ssh_private_key = '{}{}.ssh/id_rsa'.format(home, os.sep)


git_ssh_identity_file = os.getenv('SSH_PRIV_KEY', default_ssh_private_key)
git_ssh_cmd = 'ssh -i {}'.format(git_ssh_identity_file)

destination = create_tmp_dir(sub_dir='test_git_clone')
print('Cloning to {}'.format(destination))

Repo.clone_from(repo_url, destination, env=dict(GIT_SSH_COMMAND=git_ssh_cmd))

