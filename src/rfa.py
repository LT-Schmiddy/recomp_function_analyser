import sys

from colors import *
import util

import settings
import project
import commands


def main():
    settings.current.load_paths()
    
    if util.mkdir_if_missing(settings.current.paths.rfa_user_dir):
        print(f"Created rfa user directory at '{settings.paths.rfa_user_dir}'.")
        
    settings.current.load_settings()

    cmd_parser = commands.CommandProcessor()

    result = cmd_parser.process(sys.argv[1:])

    if result is None or (isinstance(result, int) and result == 0):
        util.print_color("green", "Command completed successfully!")
        settings.current.save_settings()
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