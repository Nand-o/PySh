import os
import colorama

colorama.init()

def is_colors_supported() -> bool:
    # Only use colors if connected to a terminal
    try:
        return os.isatty(1)
    except Exception:
        return False

def cyan(text: str) -> str:
    return f"{colorama.Fore.CYAN}{text}{colorama.Style.RESET_ALL}" if is_colors_supported() else text

def green(text: str) -> str:
    return f"{colorama.Fore.GREEN}{text}{colorama.Style.RESET_ALL}" if is_colors_supported() else text

def blue(text: str) -> str:
    return f"{colorama.Fore.BLUE}{text}{colorama.Style.RESET_ALL}" if is_colors_supported() else text

def red(text: str) -> str:
    return f"{colorama.Fore.RED}{text}{colorama.Style.RESET_ALL}" if is_colors_supported() else text

def yellow(text: str) -> str:
    return f"{colorama.Fore.YELLOW}{text}{colorama.Style.RESET_ALL}" if is_colors_supported() else text
