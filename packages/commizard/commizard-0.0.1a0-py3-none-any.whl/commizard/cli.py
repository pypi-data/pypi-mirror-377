from . import commands
from . import start
from .output import *


# TODO: see issues #2 and #3
def main() -> None:
    """
    This is the entry point of the program. calls some functions at the start,
    then jumps into an infinite loop.
    """
    if not start.check_git_installed():
        print_error("git not installed")
        return

    if not start.local_ai_available():
        print_warning("local AI not available")

    if not start.is_inside_working_tree():
        print_error("not inside work tree")
        return

    start.print_welcome()

    while True:
        user_input = input("CommiZard> ").strip()
        if user_input in ("exit", "quit"):
            print("Goodbye!")
            break
        commands.parser(user_input)


if __name__ == "__main__":
    main()
