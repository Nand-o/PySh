import os
import sys
from typing import List

PROMPT = "pysh> "
EXIT_COMMAND = "exit"

class Token(str):
    """
    Subclass string untuk menyimpan metadata tokenisasi,
    sehingga karakter spesial yang diapit tanda kutip (misal "|")
    tidak akan disamakan dengan operator shell sesungguhnya.
    """
    def __new__(cls, content, is_quoted=False):
        obj = super().__new__(cls, content)
        obj.is_quoted = is_quoted
        return obj

    def __eq__(self, other):
        # Jika membandingkan dengan raw string ("|", ">", dll)
        if type(other) is str and self.is_quoted:
            return False
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()

def get_prompt() -> str:
    """Mengembalikan teks prompt yang ditampilkan kepada pengguna."""
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
    """
    Membaca satu baris input.
    Menangani Ctrl+D (EOFError) agar tidak force close.
    """
    try:
        return input(prompt)
    except EOFError:
        return EXIT_COMMAND
    except UnicodeDecodeError:
        print("\npysh: input mengandung karakter invalid")
        return ""

def tokenize_input(command_line: str) -> List[str]:
    """
    Memecah string input menjadi token menggunakan character iteration.
    Mengakomodasi spasi di dalam tanda kutip tunggal/ganda.
    """
    tokens = []
    current_token = []
    in_quote = None
    has_quote = False
    escape_next = False

    for char in command_line.strip():
        if escape_next:
            current_token.append(char)
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char in ('"', "'"):
            if in_quote == char:
                in_quote = None
            elif in_quote is None:
                in_quote = char
                has_quote = True
            else:
                current_token.append(char)
        elif char in (' ', '\t') and not in_quote:
            if current_token or has_quote:
                tokens.append(Token("".join(current_token), is_quoted=has_quote))
                current_token = []
                has_quote = False
        else:
            current_token.append(char)
            
    if in_quote:
        print(f"pysh: warning: unclosed quote {in_quote}")
            
    if current_token or has_quote:
        tokens.append(Token("".join(current_token), is_quoted=has_quote))
        
    return tokens

def is_exit_command(tokens: List[str]) -> bool:
    """Mengecek perintah keluar."""
    return len(tokens) > 0 and tokens[0] == EXIT_COMMAND

def execute_external_command(tokens: List[str]):
    """Pendelegasian eksekusi murni via POSIX execvp."""
    if not tokens:
        sys.exit(0)
    try:
        os.execvp(tokens[0], tokens)
    except FileNotFoundError:
        print(f"pysh: {tokens[0]}: command not found")
        sys.exit(1)
    except Exception as e:
        print(f"pysh: {tokens[0]}: eksekusi gagal ({e})")
        sys.exit(1)

def process_redirects_and_execute(tokens: List[str]):
    """Memproses semua redirect operators dan menjalankan command."""
    clean_tokens = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in (">", ">>", "<"):
            if i + 1 >= len(tokens):
                print(f"pysh: syntax error near unexpected token 'newline'")
                return 1
            
            file_name = tokens[i+1]
            try:
                if token == ">":
                    fd = os.open(file_name, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
                    os.dup2(fd, 1)
                    os.close(fd)
                elif token == ">>":
                    fd = os.open(file_name, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
                    os.dup2(fd, 1)
                    os.close(fd)
                elif token == "<":
                    fd = os.open(file_name, os.O_RDONLY)
                    os.dup2(fd, 0)
                    os.close(fd)
            except OSError as e:
                print(f"pysh: {file_name}: {e.strerror}")
                return 1
            i += 2
        else:
            clean_tokens.append(token)
            i += 1
            
    if clean_tokens:
        execute_external_command(clean_tokens)
    return 0

def handle_command(tokens: List[str]) -> bool:
    """Memproses command, Built-in, Piping (|), dan Redirection (>, >>, <)."""
    if not tokens:
        return True

    if is_exit_command(tokens):
        return False

    command = tokens[0]

    # === TAHAP 3: Built-in Commands ===
    if command == "cd":
        try:
            target_dir = os.path.expanduser(tokens[1]) if len(tokens) > 1 else os.path.expanduser("~")
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

    # === KOMPATIBILITAS OS ===
    if not hasattr(os, 'fork'):
        import subprocess
        try:
            subprocess.run(tokens, shell=False)
        except FileNotFoundError:
            print(f"pysh: {tokens[0]}: command not found")
        except Exception as e:
            print(f"pysh: eksekusi gagal: {e}")
        return True

    # === TAHAP 5: Piping (|) ===
    if "|" in tokens:
        pipe_commands = []
        current_cmd = []
        for t in tokens:
            if t == "|":
                pipe_commands.append(current_cmd)
                current_cmd = []
            else:
                current_cmd.append(t)
        pipe_commands.append(current_cmd)
        
        if any(not cmd for cmd in pipe_commands):
            print("pysh: syntax error near unexpected token '|'")
            return True

        num_pipes = len(pipe_commands) - 1
        pipes = [os.pipe() for _ in range(num_pipes)]
        pids = []

        for i in range(len(pipe_commands)):
            try:
                pid = os.fork()
            except OSError as e:
                print(f"pysh: fork failed: {e}")
                break

            if pid == 0:
                if i > 0:
                    os.dup2(pipes[i-1][0], 0)
                if i < num_pipes:
                    os.dup2(pipes[i][1], 1)
                
                for p in pipes:
                    os.close(p[0])
                    os.close(p[1])
                
                sys.exit(process_redirects_and_execute(pipe_commands[i]))
            else:
                pids.append(pid)

        for p in pipes:
            os.close(p[0])
            os.close(p[1])

        for pid in pids:
            os.waitpid(pid, 0)
        
        return True

    # === TAHAP 5: I/O Redirection & TAHAP 4: External Command Biasa ===
    try:
        pid = os.fork()
    except OSError as e:
        print(f"pysh: fork failed: {e}")
        return True
        
    if pid == 0:
        sys.exit(process_redirects_and_execute(tokens))
    elif pid > 0:
        os.waitpid(pid, 0)

    return True

def run_shell():
    """Fungsi utama yang menjalankan REPL (Read-Eval-Print Loop)."""
    while True:
        try:
            user_input = read_input(get_prompt())
            
            if not user_input.strip():
                continue

            tokens = tokenize_input(user_input)
            status = handle_command(tokens)
            
            if not status:
                print("Cihuyyy!\n")
                break
                
        except KeyboardInterrupt:
            print()
            continue
        except Exception as e:
            print(f"pysh: unexpected error: {e}")
            continue

if __name__ == "__main__":
    run_shell()