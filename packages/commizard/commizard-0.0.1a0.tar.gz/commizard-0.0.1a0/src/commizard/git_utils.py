import subprocess


# fixme: see issue #9
def run_git_command(args: list[str]) -> subprocess.CompletedProcess:
    """
    Run a git command with the given args.

    Returns:
        a CompletedProcess object
    """
    cmd = ['git'] + args
    return subprocess.run(cmd, capture_output=True, text=True)


def is_inside_working_tree() -> bool:
    """
    Check if we're inside a working directory (can execute commit and diff
    commands)
    """
    out = run_git_command(["rev-parse", "--is-inside-work-tree"])
    return out.returncode == 0 and out.stdout.strip() == "true"


def is_changed() -> bool:
    """
    Check if we have changed files
    """
    out = run_git_command(["diff", "--name-only"])
    return (out.returncode == 0) and (out.stdout.strip() != "")


def get_diff() -> str:
    """
    Get the diff from the current working directory.

    Returns:
        the diff as a string
    """
    if not is_changed():
        return ""

    out = run_git_command(["--no-pager", "diff"])

    if out.returncode == 0:
        return out.stdout.strip()
