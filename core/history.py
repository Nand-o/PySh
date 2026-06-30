import os

try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

HISTORY_FILE = os.path.expanduser("~/.pysh_history")
MAX_HISTORY_LENGTH = 1000

def init_history():
    if not READLINE_AVAILABLE:
        return
    
    if os.path.exists(HISTORY_FILE):
        try:
            readline.read_history_file(HISTORY_FILE)
        except Exception:
            pass
    readline.set_history_length(MAX_HISTORY_LENGTH)

def save_history():
    if not READLINE_AVAILABLE:
        return
    
    try:
        readline.write_history_file(HISTORY_FILE)
    except Exception:
        pass
        
def get_history_items():
    if not READLINE_AVAILABLE:
        return ["History feature is not available (readline module not found)."]
        
    length = readline.get_current_history_length()
    items = []
    # readline history is 1-indexed
    for i in range(1, length + 1):
        item = readline.get_history_item(i)
        if item:
            items.append(f"{i:4d}  {item}")
    return items
