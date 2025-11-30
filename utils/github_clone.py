"""Utility for cloning GitHub repositories"""
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from git import Repo
from utils.logger import get_logger

logger = get_logger()


def clone_github_repo(github_url: str, target_dir: Optional[str] = None) -> Path:
    """
    Clone a GitHub repository to a temporary or specified directory
    
    Args:
        github_url: GitHub repository URL (e.g., https://github.com/user/repo.git)
        target_dir: Optional target directory. If None, uses a temp directory.
    
    Returns:
        Path to the cloned repository
    """
    try:
        # Clean up the URL
        if github_url.endswith('.git'):
            repo_url = github_url
        elif 'github.com' in github_url:
            # Convert https://github.com/user/repo to https://github.com/user/repo.git
            repo_url = github_url if github_url.endswith('.git') else f"{github_url}.git"
        else:
            raise ValueError(f"Invalid GitHub URL: {github_url}")
        
        # Determine target directory
        if target_dir:
            target_path = Path(target_dir)
            if target_path.exists():
                logger.warning(f"Target directory exists, removing: {target_path}")
                shutil.rmtree(target_path)
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            # Use temporary directory
            target_path = Path(tempfile.mkdtemp(prefix="github_repo_"))
        
        logger.info(f"Cloning {repo_url} to {target_path}")
        
        # Clone the repository
        Repo.clone_from(repo_url, str(target_path))
        
        logger.info(f"Successfully cloned repository to {target_path}")
        return target_path
        
    except Exception as e:
        logger.error(f"Failed to clone repository: {e}")
        raise


def is_github_url(url: str) -> bool:
    """Check if a URL is a GitHub repository URL"""
    return 'github.com' in url.lower() or url.endswith('.git')

