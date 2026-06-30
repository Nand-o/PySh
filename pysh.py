from core.prompt import get_prompt, read_input
from core.tokenizer import tokenize_input
from core.parser import parse_pipeline
from core.pipes import execute_pipeline
from core.builtins import EXIT_COMMAND
from core.history import init_history, save_history
from core.completion import init_completion
import os

def load_pyshrc():
    pyshrc_path = os.path.expanduser("~/.pyshrc")
    if os.path.exists(pyshrc_path):
        try:
            with open(pyshrc_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    tokens = tokenize_input(line)
                    segments = parse_pipeline(tokens)
                    if segments:
                        execute_pipeline(segments)
        except Exception as e:
            print(f"pysh: error loading .pyshrc: {e}")

def run_shell():
    """Fungsi utama yang menjalankan REPL (Read-Eval-Print Loop)."""
    init_history()
    init_completion()
    load_pyshrc()
    
    while True:
        try:
            user_input = read_input(get_prompt())
            
            if not user_input.strip():
                continue

            tokens = tokenize_input(user_input)
            segments = parse_pipeline(tokens)
            
            if not segments:
                continue
                
            # Cek exit command (harus keluar dari shell)
            # Jika ada pipeline "exit | ls", exit akan jalan di child dan parent gak ikut keluar
            # Jadi kita cek command pertama saja (bash style).
            if len(segments) == 1 and segments[0].args and segments[0].args[0] == EXIT_COMMAND:
                print("Cihuyyy!\n")
                break
                
            execute_pipeline(segments)
                
        except KeyboardInterrupt:
            print()
            continue
        except Exception as e:
            print(f"pysh: unexpected error: {e}")
            continue

    save_history()

if __name__ == "__main__":
    run_shell()