import os
import stat
import datetime
from typing import List
from .history import get_history_items
from .colors import cyan, green, blue, yellow, red

EXIT_COMMAND = "exit"

BUILTIN_COMMANDS = {
    "cd": "Change the shell working directory.",
    "pwd": "Print the name of the current working directory.",
    "ls": "List directory contents with details.",
    "dir": "List directory contents with details (alias for ls).",
    EXIT_COMMAND: "Exit the shell.",
    "help": "Display information about builtin commands.",
    "history": "Display the command history list."
}

def is_builtin(command: str) -> bool:
    return command in BUILTIN_COMMANDS

def execute_builtin(args: List[str]) -> bool:
    command = args[0]
    
    if command == EXIT_COMMAND:
        # Exit ditangani secara khusus di shell loop, tapi kita bisa return False
        return False
        
    if command == "cd":
        try:
            target_dir = os.path.expanduser(args[1]) if len(args) > 1 else os.path.expanduser("~")
            os.chdir(target_dir)
        except Exception as e:
            print(red(f"cd: {e}"))
        return True
        
    elif command == "pwd":
        try:
            print(f"Current Directory: {green(os.getcwd())}")
        except Exception as e:
            print(red(f"pwd: {e}"))
        return True
        
    elif command in ("ls", "dir"):
        try:
            path = args[1] if len(args) > 1 else '.'
            if not os.path.exists(path):
                print(red(f"ls: cannot access '{path}': No such file or directory"))
                return True
                
            items = os.listdir(path) if os.path.isdir(path) else [path]
            
            print(f"\n    Directory: {green(os.path.abspath(path))}\n")
            print(f"{'Mode':<18} {'LastWriteTime':<20} {'Length':>10} Name")
            print(f"{'----':<18} {'-------------':<20} {'------':>10} ----")
            
            for item in sorted(items):
                item_path = os.path.join(path, item) if os.path.isdir(path) else item
                try:
                    s = os.stat(item_path)
                    is_dir = stat.S_ISDIR(s.st_mode)
                    
                    win_mode = ('d' if is_dir else '-') + ('a' if not is_dir else '-') + '---'
                    mtime = datetime.datetime.fromtimestamp(s.st_mtime).strftime('%m/%d/%Y %I:%M %p')
                    length = str(s.st_size) if not is_dir else ''
                    colored_name = blue(item) if is_dir else (green(item) if os.access(item_path, os.X_OK) else item)
                    
                    print(f"{win_mode:<18} {mtime:<20} {length:>10} {colored_name}")
                except OSError:
                    continue
            print()
        except Exception as e:
            print(red(f"{command}: {e}"))
        return True
        
    elif command == "help":
        print(cyan("\n=== PySh - The Python Shell ==="))
        print(yellow("Built-in commands:"))
        for cmd, desc in BUILTIN_COMMANDS.items():
            print(f"  {green(cmd):<15} {desc}")
        print()
        return True
        
    elif command == "history":
        items = get_history_items()
        print(cyan("\n=== Command History ==="))
        for item in items:
            parts = item.split(None, 1)
            if len(parts) == 2:
                print(f"  {yellow(parts[0])}  {parts[1]}")
            else:
                print(item)
        print()
        return True
        
    return True
