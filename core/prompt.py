import os
from .colors import green, blue, cyan

PROMPT = "pysh> "

def get_prompt() -> str:
    try:
        cwd = os.getcwd()
    except OSError:
        cwd = "(unreachable)"
        
    parts = cwd.split(os.sep)
    if len(parts) > 3:
        path_str = f"{parts[0]}{os.sep}...{os.sep}{parts[-1]}"
    else:
        path_str = cwd
        
    return f"[{blue(path_str)}] {cyan(PROMPT)}"

def read_input(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return "exit"
    except UnicodeDecodeError:
        print("\npysh: input mengandung karakter invalid")
        return ""
