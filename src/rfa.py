import sys

from colors import *
import util

import settings
import project
import commands

    
def init_user():
    settings.paths.load_paths()
    
    if util.mkdir_if_missing(settings.paths.rfa_user_dir):
        print(f"Created rfa user directory at '{settings.path_handler.rfa_user_dir}'.")
        
    settings.load_settings()


def print_cmd_list():
    for cmd, desc in commands.get_command_desc().items():
        print(f"\t{cmd} - {desc}")


def args_len_check():
    if len(sys.argv) < 2:
        util.print_error("FATAL ERROR: No command given. Valid commands are:")
        print_cmd_list()

        sys.exit(1)


def main():
    init_user()

    # if no command is given:
    args_len_check()
    project.info.attempt_load_project()
        
    if project.info.is_project:
        util.print_color("green", f"-> Running for local project '{project.info.project_root}':")
    else:
        util.print_color("green", "-> Running without project: ")

    cmd = sys.argv[1]
    cmds = commands.get_commands()

    # if command is not valid:
    if cmd not in cmds:
        util.print_error(f"FATAL ERROR '{cmd}' is not a valid command. Valid commands are:")
        print_cmd_list()
        sys.exit(1)

    # Initialize and execute command:
    cmd_runner = cmds[cmd]()
    result = cmd_runner.run(sys.argv[2:])

    if result is None:
        util.print_color("green", "Command completed successfully!")
        settings.save_settings()
        sys.exit(0)

    elif isinstance(result, str):
        util.print_error(f"FATAL ERROR: {result}")
        sys.exit(1)

    elif isinstance(result, int):
        util.print_error(f"FATAL ERROR: Error code {result}")
        sys.exit(result)

    else:
        util.print_error(f"FATAL ERROR: Unknown cause - {result}")
        sys.exit(1)

if __name__ == "__main__":
    main()