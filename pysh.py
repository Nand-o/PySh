from core.prompt import get_prompt, read_input
from core.tokenizer import tokenize_input
from core.parser import parse_pipeline
from core.pipes import execute_pipeline
from core.builtins import EXIT_COMMAND

def run_shell():
    """Fungsi utama yang menjalankan REPL (Read-Eval-Print Loop)."""
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

if __name__ == "__main__":
    run_shell()