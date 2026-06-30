import os
import glob
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

from .builtins import BUILTIN_COMMANDS

def get_executables_in_path():
    executables = []
    path_env = os.environ.get("PATH", "")
    for p in path_env.split(os.pathsep):
        if os.path.isdir(p):
            try:
                for f in os.listdir(p):
                    # Fast check, though not 100% perfect on Windows
                    executables.append(f)
            except Exception:
                pass
    return executables

class Completer:
    def __init__(self):
        self.options = []
        self.executables = None
        
    def complete(self, text, state):
        line = readline.get_line_buffer()
        
        if state == 0:
            if not line.strip() or line.rfind(" ") == -1 or line.rfind(" ") == len(line) - 1:
                # We are at the start or typing the first command
                if self.executables is None:
                    self.executables = get_executables_in_path()
                opts = list(BUILTIN_COMMANDS.keys()) + self.executables
                self.options = [cmd for cmd in opts if cmd.startswith(text)]
            else:
                # We are typing arguments, complete files and directories
                # Use glob for file matching
                matches = glob.glob(text + "*")
                
                # Append slash to directories for easier navigation
                self.options = []
                for m in matches:
                    if os.path.isdir(m):
                        self.options.append(m + os.sep)
                    else:
                        self.options.append(m)
        
        try:
            return self.options[state]
        except IndexError:
            return None

def init_completion():
    if not READLINE_AVAILABLE:
        return
    
    completer = Completer()
    readline.set_completer(completer.complete)
    
    # Enable tab completion
    doc = getattr(readline, '__doc__', '')
    if doc and 'libedit' in doc:
        readline.parse_and_bind('bind ^I rl_complete')
    else:
        readline.parse_and_bind('tab: complete')
