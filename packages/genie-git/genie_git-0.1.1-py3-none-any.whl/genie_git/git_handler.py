"""Handles git operations."""

import git


def get_repository_changes(exclude_files: list[str] = []) -> str:
    """Get the staged changes in the repository.

    Args:
        exclude_files: List of files to exclude from the diff.

    Returns:
        String containing the diff

    """
    repo = git.Repo(".", search_parent_directories=True)

    exclude_files_argument = " ".join([f":(exclude){file}" for file in exclude_files])

    if not exclude_files_argument:
        staged_diff = repo.git.diff("--staged")
    else:
        staged_diff = repo.git.diff("--staged", exclude_files_argument)

    return staged_diff


def get_log(number_of_commits: int = 5) -> str:
    """Return the last n commit messages.

    Args:
        number_of_commits: Number of commit messages to return (default: 5)

    Returns:
        String containing the commit messages

    """
    repo = git.Repo(".", search_parent_directories=True)
    return repo.git.log(f"-{number_of_commits}", "--pretty=format:%s")
