import sys

from colors import *
import util

import settings
import project
import commands

    
def init_user():
    settings.paths.load_paths()
    
    if util.mkdir_if_missing(settings.paths.rfa_user_dir):
        print(f"Created rfa user directory at '{settings.paths.rfa_user_dir}'.")
        
    settings.load_settings()


def main():
    init_user()

    # if no command is given:
    project.info.attempt_load_project()
        
    if project.info.is_project:
        util.print_color("green", f"-> Running for local project '{project.info.project_root}':")
    else:
        util.print_color("green", "-> Running without project: ")

    cmd_parser = commands.ArgumentProcessor()

    result = cmd_parser.process(sys.argv[1:])

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