import os
import sys
from typing import List

PROMPT = "pysh> "
EXIT_COMMAND = "exit"

def get_prompt() -> str:
    """Mengembalikan teks prompt yang ditampilkan kepada pengguna."""
    cwd = os.getcwd()
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

def tokenize_input(command_line: str) -> List[str]:
    """
    Memecah string input menjadi token menggunakan character iteration.
    Mengakomodasi spasi di dalam tanda kutip tunggal/ganda.
    """
    tokens = []
    current_token = []
    in_quote = None

    for char in command_line.strip():
        if char in ('"', "'"):
            if in_quote == char:
                in_quote = None
            elif in_quote is None:
                in_quote = char
            else:
                current_token.append(char)
        elif char == ' ' and not in_quote:
            if current_token:
                tokens.append("".join(current_token))
                current_token = []
        else:
            current_token.append(char)
            
    if current_token:
        tokens.append("".join(current_token))
        
    return tokens

def is_exit_command(tokens: List[str]) -> bool:
    """Mengecek perintah keluar."""
    return len(tokens) > 0 and tokens[0].lower() == EXIT_COMMAND

def execute_external_command(tokens: List[str]):
    """Pendelegasian eksekusi murni via POSIX execvp."""
    try:
        os.execvp(tokens[0], tokens)
    except FileNotFoundError:
        print(f"pysh: {tokens[0]}: command not found")
        sys.exit(1)
    except Exception as e:
        print(f"pysh: {tokens[0]}: eksekusi gagal ({e})")
        sys.exit(1)

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
        
    # CATATAN PENYESUAIAN: Perintah internal 'echo' sengaja dihapus dari sini.
    # Jika dipertahankan, shell Pysh akan mencegat eksekusinya dan menggagalkan
    # operasi redirection seperti `echo "teks" > file.txt`. 
    # Dengan menghapusnya, Pysh akan meneruskan perintah echo ke binary asli OS.

    # === KOMPATIBILITAS OS ===
    # Kompatibilitas Lingkungan Windows via exception OS
    if not hasattr(os, 'fork'):
        import subprocess
        # Parameter shell=True menyelesaikan masalah batch script & metakarakter Windows
        subprocess.run(" ".join(tokens), shell=True)
        return True

    # === TAHAP 5: Piping (|) ===
    # Menghubungkan output dari proses pertama (kiri) menjadi input bagi proses kedua (kanan)
    if "|" in tokens:
        pipe_index = tokens.index("|")
        left_cmd = tokens[:pipe_index]
        right_cmd = tokens[pipe_index+1:]

        # Membuka saluran komunikasi IPC
        read_fd, write_fd = os.pipe()

        pid1 = os.fork()
        if pid1 == 0:
            # Child 1 (Proses Kiri): Menulis ke pipe
            os.close(read_fd)         
            os.dup2(write_fd, 1)      # Alihkan STDOUT ke pipe write end
            os.close(write_fd)        
            execute_external_command(left_cmd)

        pid2 = os.fork()
        if pid2 == 0:
            # Child 2 (Proses Kanan): Membaca dari pipe
            os.close(write_fd)        
            os.dup2(read_fd, 0)       # Alihkan STDIN ke pipe read end
            os.close(read_fd)         
            execute_external_command(right_cmd)

        # Parent Process: Wajib menutup kedua ujung pipe untuk mencegah deadlock (hang)
        os.close(read_fd)
        os.close(write_fd)
        
        # Parent menunggu kedua child selesai
        os.waitpid(pid1, 0)
        os.waitpid(pid2, 0)
        
        return True

    # === TAHAP 5: I/O Redirection (>, >>, <) ===
    # Mengarahkan output standar ke file teks atau membaca input dari file teks
    redirect_out = ">" in tokens
    redirect_append = ">>" in tokens
    redirect_in = "<" in tokens

    if redirect_out or redirect_append or redirect_in:
        pid = os.fork()
        
        if pid == 0:
            # Di dalam Child Process, lakukan manipulasi File Descriptor sebelum execvp
            if redirect_append:
                idx = tokens.index(">>")
                cmd_tokens = tokens[:idx]
                file_name = tokens[idx+1]
                
                # O_APPEND: Tambahkan output ke bawah baris tanpa menghapus file asli
                fd = os.open(file_name, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
                os.dup2(fd, 1)
                os.close(fd)
                execute_external_command(cmd_tokens)
                
            elif redirect_out:
                idx = tokens.index(">")
                cmd_tokens = tokens[:idx]
                file_name = tokens[idx+1]
                
                # O_TRUNC: Hapus isi file lama, ganti dengan output yang baru
                fd = os.open(file_name, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
                os.dup2(fd, 1)        
                os.close(fd)
                execute_external_command(cmd_tokens)

            elif redirect_in:
                idx = tokens.index("<")
                cmd_tokens = tokens[:idx]
                file_name = tokens[idx+1]
                
                try:
                    # O_RDONLY: Buka file hanya untuk dibaca
                    fd = os.open(file_name, os.O_RDONLY)
                    os.dup2(fd, 0)    # Alihkan STDIN (0) agar membaca dari file
                    os.close(fd)
                    execute_external_command(cmd_tokens)
                except FileNotFoundError:
                    print(f"pysh: {file_name}: No such file or directory")
                    sys.exit(1)
                    
        elif pid > 0:
            # Parent menunggu proses redirection selesai
            os.waitpid(pid, 0)
            
        return True

    # === TAHAP 4: External Command Biasa ===
    pid = os.fork()
    if pid == 0:
        execute_external_command(tokens)
    elif pid > 0:
        # Menyinkronkan siklus hidup proses (mencegah prompt mendahului output)
        os.waitpid(pid, 0)
    else:
        print("pysh: fork failed")

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
            # Mencegah eksekusi berhenti mendadak saat Ctrl+C ditekan
            print()
            continue

if __name__ == "__main__":
    run_shell()