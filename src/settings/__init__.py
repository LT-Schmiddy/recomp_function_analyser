import sys, os, json
from pathlib import Path

from colors import *
import util
from . import path_handler


def default_settings_dict():
    return {
        "preprocessing": {
            "default_cmd": "clang",
            "default_flags": [
                "-E"
            ]
        }
    }

class SettingsWrapperBase:
    s_dict: dict
    attribute_delimiter: str
    
    def __init__(self, s_dict: dict):
        self.attribute_delimiter = "."
        self.s_dict = s_dict
        
    def traverse_attributes(self, attribute_path: list[str]):
        lookup_obj = self.s_dict
        for i in attribute_path:
            if isinstance(lookup_obj, list):
                lookup_obj = lookup_obj[int(i)]
            else:
                lookup_obj = lookup_obj[i]
        
        return lookup_obj
        
    def get(self, key: str = "") -> bool | int | float | str | list | dict:
        attribute_path = key.split(self.attribute_delimiter)
        attribute_name = attribute_path.pop()
        
        lookup_obj = self.traverse_attributes(attribute_path)
        
        # If no name, return the object itself
        if attribute_name == "":
            return lookup_obj
        
        if isinstance(lookup_obj, list):
            return lookup_obj[int(attribute_name)]
        else:
            return lookup_obj[attribute_name]
    
    def set(self, key: str, value: bool | int | float | str | list | dict):
        attribute_path = key.split(self.attribute_delimiter)
        attribute_name = attribute_path.pop()
        
        lookup_obj = self.traverse_attributes(attribute_path)
        
        if isinstance(lookup_obj, list):
            lookup_obj[int(attribute_name)] = value
        else:
            lookup_obj[attribute_name] = value
    
    def contains(self, key: str) -> bool:
        return key in self.s_dict

class SettingsWrapper(SettingsWrapperBase):
    class PreprocessorSettings(SettingsWrapperBase):
        
        @property
        def default_cmd(self):
            return self.s_dict["default_cmd"]
        
        @default_cmd.setter
        def default_cmd(self, value: str):
            self.s_dict["default_cmd"] = value
            
        @property
        def default_flags(self):
            return self.s_dict["default_flags"]
        
        @default_flags.setter
        def default_flags(self, value: str):
            self.s_dict["default_flags"] = value
    
    preprocessing: PreprocessorSettings
    paths = path_handler.PathHandler
    
    def __init__(self, s_dict: dict):
        super().__init__(s_dict)
        
        self.preprocessing = SettingsWrapper.PreprocessorSettings(s_dict["preprocessing"])
        self.paths = path_handler.PathHandler()

    def load_paths(self):
        self.paths.load_paths()
    
    def save_settings(self, path: Path = None, settings_dict: dict = None):
        if path is None:
            path = self.paths.rfa_user_settings_path
            
        if settings_dict is None:
            settings_dict = self.s_dict
        
        util.save_json_config(path, settings_dict)


    def load_settings(self, path: Path = None, settings_dict: dict = None):
        if path is None:
            path = self.paths.rfa_user_settings_path
            
        if settings_dict is None:
            settings_dict = self.s_dict
        
        util.load_json_config(path, settings_dict)


current = SettingsWrapper(default_settings_dict())


