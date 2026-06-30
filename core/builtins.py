import os
from typing import List

EXIT_COMMAND = "exit"

def is_builtin(command: str) -> bool:
    return command in ["cd", "pwd", EXIT_COMMAND]

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
            print(f"cd: {e}")
        return True
        
    elif command == "pwd":
        try:
            print(os.getcwd())
        except Exception as e:
            print(f"pwd: {e}")
        return True
        
    return True
