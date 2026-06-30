import os

PROMPT = "pysh> "

def get_prompt() -> str:
    try:
        cwd = os.getcwd()
    except OSError:
        cwd = "(unreachable)"
        
    parts = cwd.split(os.sep)
    if len(parts) > 3:
        return f"[{parts[0]}{os.sep}...{os.sep}{parts[-1]}] {PROMPT}"
    else:
        return f"[{cwd}] {PROMPT}"

def read_input(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return "exit"
    except UnicodeDecodeError:
        print("\npysh: input mengandung karakter invalid")
        return ""
