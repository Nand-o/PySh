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
    return PROMPT

def read_input(prompt: str) -> str:
    """Membaca satu baris input dan menangani EOF (Ctrl+D) sebagai perintah exit."""
    try:
        return input(prompt)
    except EOFError:
        return EXIT_COMMAND

def tokenize_input(command_line: str) -> List[str]:
    """
    Memecah string input menjadi token (Perintah Utama dan Argumen).
    """
    # .strip() menghapus spasi di awal/akhir, lalu .split() memecah kata
    return command_line.strip().split()

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