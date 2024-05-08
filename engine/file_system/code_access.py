from functools import wraps
import os
import shutil
from django.conf import settings
import git


def needs_code_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Cloning logic moved from TaskEngine
        if os.path.exists(settings.REPO_DIR):
            shutil.rmtree(settings.REPO_DIR)
        git_repo_url = f"https://x-access-token:{{kwargs.get('github_token')}}@github.com/{{kwargs.get('github_project')}}.git"
        git.Repo.clone_from(git_repo_url, settings.REPO_DIR)
        print("Cloning repository...")
        return func(*args, **kwargs)
    return wrapper
