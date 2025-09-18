import os
from git import Repo

from prefect import get_run_logger

logger = get_run_logger()

def clone_repo(git_pat, git_url, clone_base_path):
    # Retrieve environment variables
    access_token = git_pat # os.environ.get('GIT_PAT')
    repo_url = git_url # os.environ.get('GIT_URL')
    
    if not access_token or not repo_url:
        raise ValueError("Environment variables GIT_PAT or GIT_URL are not set")

    # Correctly format the URL with the PAT
    if 'https://' in repo_url:
        # Splitting the URL and inserting the PAT
        parts = repo_url.split('https://', 1)
        repo_url = f'https://{access_token}@{parts[1]}'
    else:
        raise ValueError("URL must begin with https:// for PAT authentication")

    # Directory where the repo will be cloned
    repo_path = os.path.join(clone_base_path, 'manifest-repo')

    # Clone the repository
    if not os.path.exists(repo_path):
        logger.info(f"Cloning repository into {repo_path}")
        repo = Repo.clone_from(repo_url, repo_path)
        logger.info("Repository cloned successfully.")
    else:
        logger.info(f"Repository already exists at {repo_path}")