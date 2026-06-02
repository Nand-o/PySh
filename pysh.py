"""
Custom shell prototype (Minggu 1)
- REPL loop
- Tokenisasi sederhana 
- Exit command handling
"""

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
    """Membaca satu baris input dan menangani EOF (Ctrl+D) sebagai perintah exit."""
    try:
        return input(prompt)
    except EOFError:
        return EXIT_COMMAND

def tokenize_input(command_line: str) -> List[str]:
    """
    Memecah string input menjadi token (Perintah Utama dan Argumen) secara manual.
    Mendukung pengelompokan argumen dengan spasi jika diapit tanda kutip tunggal atau ganda.
    """
    tokens = []
    current_token = []
    in_quote = None  # Menyimpan jenis tanda kutip yang sedang terbuka (' atau ")

    for char in command_line.strip():
        if char in ('"', "'"):
            if in_quote == char:
                # Jika karakter kutip yang sama ditemukan, tutup kutip tersebut
                in_quote = None
            elif in_quote is None:
                # Jika belum ada kutip yang terbuka, mulai blok kutip
                in_quote = char
            else:
                # Tanda kutip lain di dalam kutip yang sedang aktif
                current_token.append(char)
        elif char == ' ' and not in_quote:
            # Spasi di luar kutip menandakan akhir dari sebuah token
            if current_token:
                tokens.append("".join(current_token))
                current_token = []
        else:
            # Karakter lainnya masuk ke token saat ini
            current_token.append(char)
            
    # Masukkan sisa karakter sebagai token terakhir
    if current_token:
        tokens.append("".join(current_token))
        
    return tokens

def is_exit_command(tokens: List[str]) -> bool:
    """Mengecek apakah pengguna meminta shell untuk berhenti."""
    return len(tokens) > 0 and tokens[0].lower() == EXIT_COMMAND

def handle_command(tokens: List[str]) -> bool:
    """Memproses command yang sudah ditokenisasi. Return False untuk berhenti."""
    if not tokens:
        return True

    if is_exit_command(tokens):
        return False

    command = tokens[0]
    arguments = tokens[1:]

    if command == "cd":
        if arguments:
            try:
                os.chdir(arguments[0])
            except FileNotFoundError:
                print(f"cd: {arguments[0]}: No such file or directory")
            except NotADirectoryError:
                print(f"cd: {arguments[0]}: Not a directory")
            except PermissionError:
                print(f"cd: {arguments[0]}: Permission denied")
        else:
            # Jika cd dipanggil tanpa argumen, ubah ke direktori home
            try:
                os.chdir(os.path.expanduser("~"))
            except Exception as e:
                print(f"cd: {e}")
        return True
        
    elif command == "pwd":
        try:
            print(os.getcwd())
        except Exception as e:
            print(f"pwd: {e}")
        return True

    # Output Mingguan: Membuktikan CLI mengenali kata per kata
    print(f"[DEBUG] Command Utama : '{command}'")
    if arguments:
        print(f"[DEBUG] Argumen       : {arguments}")
    else:
        print("[DEBUG] Argumen       : (Tidak ada)")

    return True

def run_shell():
    """Fungsi utama yang menjalankan REPL (Read-Eval-Print Loop)."""
    while True:
        try:
            # 1. READ: Tampilkan prompt dan baca input
            user_input = read_input(get_prompt())
            
            # Jika user hanya menekan Enter tanpa mengetik apa-apa
            if not user_input.strip():
                continue

            # 2. EVAL (Parsing): Pecah input jadi token
            tokens = tokenize_input(user_input)
            
            # 3. PRINT/EXECUTE: Jalankan perintah
            status = handle_command(tokens)
            
            # Jika handle_command mengembalikan False (karena perintah exit)
            if not status:
                print("Cihuyyy!\n")
                break
                
        except KeyboardInterrupt:
            # Menangkap Ctrl+C agar shell tidak force close
            print()
            continue

if __name__ == "__main__":
    run_shell()