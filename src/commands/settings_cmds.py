import argparse, json
from typing import Any
from pathlib import Path

import settings

from commands import SubCommandBase, CommandProcessorArgs

class SettingsCommand(SubCommandBase):
    name: str = "settings"
    kwargs: dict = {"aliases": ["s"], "help": "Displays current rfa user settings. Settings file is store in '~/.rfa'."}

    # Only defined for the sake of annotations. Isn't actually necessary, and doesn't do anything.
    class SettingsGetCommandArgs(CommandProcessorArgs):
        attribute: str
        value: str

    def setup_args(self):
        self.subparsers = self.parser.add_subparsers(
            dest="action",
            title="Settings action",
            description="Settings action to perform",
            help="Additional settings help",
        )
        
        self.get_parser = self.subparsers.add_parser(
            "get", aliases=["g"], help="Displays current settings."
        )
        self.get_parser.set_defaults(settings_cmd_func=lambda x: self.process_get(x))
        
        self.set_parser = self.subparsers.add_parser(
            "set", aliases=["s"], help="Sets settings to new value (not working perfectly yet)."
        )
        self.set_parser.set_defaults(settings_cmd_func=lambda x: self.process_set(x))
        self.set_parser.add_argument(
            "value",
            type=str,
            default="",
            help="The new value for the attribute.",
        )

        for i in [self.set_parser, self.get_parser]:
            i.add_argument(
                "-a",
                "--attribute",
                type=str,
                default="",
                help="A path to a specific attribute, delimited by period (.) characters.",
            )

    def process(self, args: SettingsGetCommandArgs) -> Any:
        if hasattr(args, "settings_cmd_func"):
            return args.settings_cmd_func(args)

        return None

    def process_get(self, args: SettingsGetCommandArgs) -> Any:
        print(json.dumps(settings.current.get(args.attribute), indent=4))
        
    def process_set(self, args: SettingsGetCommandArgs) -> Any:
        try:
            save_val = json.loads(args.value)
            print("Is valid JSON")
        except json.JSONDecodeError as e:
            print("Not valid json. Assuming string.")
            save_val = args.value
        
        # print(save_val)
        settings.current.set(args.attribute, save_val)
        
