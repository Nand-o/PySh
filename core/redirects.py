import os
from .token import TokenType
from .parser import Redirect
from typing import List

def apply_redirects(redirects: List[Redirect]) -> bool:
    """Applies all redirections. Returns True if successful, False if failed."""
    for red in redirects:
        try:
            if red.type == TokenType.REDIRECT_OUT:
                fd = os.open(red.target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
                os.dup2(fd, 1)
                os.close(fd)
            elif red.type == TokenType.REDIRECT_APPEND:
                fd = os.open(red.target, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
                os.dup2(fd, 1)
                os.close(fd)
            elif red.type == TokenType.REDIRECT_IN:
                fd = os.open(red.target, os.O_RDONLY)
                os.dup2(fd, 0)
                os.close(fd)
        except OSError as e:
            print(f"pysh: {red.target}: {e.strerror}")
            return False
    return True
