import subprocess

import pyperclip

from . import llm_providers
from . import output


# TODO: see issue #4
def handle_commit_req(opts: list) -> int:
    """
    commits the generated prompt according to options:
        If none specified, commits both the Title and the Body
        If passed body or title like : commit body, or: commit title,
        only commits the parts specified.

    Args:
        opts: a list of options following the commit command passed to the cli.

    Returns:
        a status code: 0 for success, 1 for failure, 2 for incorrect
        prompt input.
    """
    if opts == []:
        out = subprocess.run(
            ["git", "commit", "-a", "-m", gen_head, "-m", gen_body],
            capture_output=True)
    elif opts[0] in ("-h", "--help"):
        # TODO: Do something for the helps. This will get super bad super quick
        print("""options:\n
        The commit command will commit both the title and the body by default.\n
        head | title: Just commit the head, ignore the body.\n
        body: Commit the body without the head""")
    elif opts[0] in ("head", "title"):
        out = subprocess.run(
            ["git", "commit", "-a", "-m", gen_head], capture_output=True)
    elif opts[0] == "body":
        out = subprocess.run(
            ["git", "commit", "-a", "-m", gen_body], capture_output=True)
    else:
        output.print_error(f"Error: {opts[0]} is not a valid commit command.")
        return 2


# TODO: implement
def print_help(opts: list) -> None:
    """
    prints a list of all commands and a brief description

    Args:
        opts: a specific command that the user needs help with

    Returns:
        None
    """
    pass


def copy_command(opts: list) -> None:
    """
    copies the generated prompt to clipboard according to options passed.

    Args:
        opts: list of options following the command
    """
    if llm_providers.gen_message == None:
        output.print_warning("No generated message found."
                             " Please run 'generate' first.")
        return

    pyperclip.copy(llm_providers.gen_message)
    output.print_success("Copied to clipboard.")


def start_model(opts: list[str]) -> None:
    """
    Get the model (either local or online) ready for generation based on the
    options passed.
    """
    if llm_providers.available_models is None:
        llm_providers.init_model_list()

    # TODO: we can get partial name of the model. For example, the user writes:
    #       start codellama instead of: start codellama:7b-instruct . implement
    #       that

    model_name = opts[0]

    if model_name not in llm_providers.available_models:
        output.print_error(f"{model_name} Not found.")
        return
    llm_providers.select_model(model_name)


def print_available_models(opts: list) -> None:
    """
    prints the available models according to options passed.
    """
    llm_providers.init_model_list()
    for model in llm_providers.available_models:
        print(model)


def generate_message(opts: list) -> None:
    """
    generate and print a commit message
    """
    llm_providers.generate()


supported_commands = {"commit": handle_commit_req,
                      "help": print_help,
                      "cp": copy_command,
                      "start": start_model,
                      "list": print_available_models,
                      "gen": generate_message,
                      "generate": generate_message
                      }


def parser(user_input: str) -> int:
    """
    Parse the user input and call appropriate functions

    Args:
        user_input: The user input to be parsed

    Returns:
        a status code: 0 for success, 1 for unrecognized command
    """
    commands = user_input.split()
    if commands[0] in list(supported_commands.keys()):
        # call the function from the dictionary with the rest of the commands
        # passed as arguments to it
        supported_commands[commands[0]](commands[1:])
        return 0
    else:
        return 1
