import os
import sys
from typing import List
from .parser import CommandSegment
from .redirects import apply_redirects
from .builtins import execute_builtin, is_builtin

def execute_external_command(args: List[str]):
    """Pendelegasian eksekusi murni via POSIX execvp."""
    if not args:
        sys.exit(0)
    try:
        os.execvp(args[0], args)
    except FileNotFoundError:
        print(f"pysh: {args[0]}: command not found")
        sys.exit(1)
    except Exception as e:
        print(f"pysh: {args[0]}: eksekusi gagal ({e})")
        sys.exit(1)

def execute_segment(segment: CommandSegment):
    """Mengeksekusi satu command segment (external atau builtin yang berjalan di child)."""
    if not segment.args:
        sys.exit(0)
        
    if not apply_redirects(segment.redirects):
        sys.exit(1)
        
    if is_builtin(segment.args[0]):
        # Di dalam child, eksekusi builtin lalu exit
        execute_builtin(segment.args)
        sys.exit(0)
    else:
        execute_external_command(segment.args)

def execute_single_command_windows(segment: CommandSegment) -> bool:
    # Windows fallback
    if is_builtin(segment.args[0]):
        return execute_builtin(segment.args)
        
    import subprocess
    try:
        subprocess.run(segment.args, shell=False)
    except FileNotFoundError:
        print(f"pysh: {segment.args[0]}: command not found")
    except Exception as e:
        print(f"pysh: eksekusi gagal: {e}")
    return True
