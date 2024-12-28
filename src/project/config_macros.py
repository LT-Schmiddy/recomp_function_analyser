import shutil
from typing import Union, Callable

import settings

class ConfigMacroProcessor:
    class ConfigMacroDef:
        name: str
        _value: str | Callable
        
        def __init__(self, name: str, value: str | Callable):
            self.name = name
            self._value = value
        
        @property
        def match_str(self):
            return "${" + self.name + "}"
        
        @property
        def value(self):
            if callable(self._value):
                return self._value()
            
            return self._value
        
        def should_process(self, in_str: str):
            return self.match_str in in_str
        
        def process(self, in_str: str) -> str:
            return in_str.replace(self.match_str, self.value)

    
    
    macros: list[ConfigMacroDef]
    
    def __init__(self):
        self.macros = [
            ConfigMacroProcessor.ConfigMacroDef("DEFAULT_PREPROC", lambda: settings.current.preprocessing.default_cmd)
        ]
        
    def add_macro(self, name: str, value: str | Callable):
        self.macros.append(ConfigMacroProcessor.ConfigMacroDef(name, value))
    
    def should_recurse(self, item):
        return isinstance(item, list) or isinstance(item, dict)
        
    def process_recurse(self, item: dict | list) -> dict | list:
        if isinstance(item, list):
            self.process_list(item)
        elif isinstance(item, dict):
            self.process_dict(item)
            
        return item
    
    def process_list(self, in_list: list):
        for i in range(0, len(in_list)):
            if self.should_recurse(in_list[i]):
                self.process_recurse(in_list[i])
            else:
                in_list[i] = self.process_non_recurse(in_list[i])
    
    def process_dict(self, in_dict: dict):
        for key in list(in_dict.keys()):
            if self.should_recurse(in_dict[key]):
                self.process_recurse(in_dict[key])
            else:
                in_dict[key] = self.process_non_recurse(in_dict[key])
                
    def process_non_recurse(self, item) -> str:
        if isinstance(item, str):
            
            # If the string was updated via a macro, we'll set the entire process to run again.
            # This allows for the evaluation of nested macros.
            # TODO: prevent recursive macros from creating an infinite loop. somehow.
            needs_update: bool = True
            while needs_update:
                needs_update = False
                for macro in self.macros:
                    if macro.should_process(item):
                        item = macro.process(item)
                        needs_update = True
        
        return item
    
    