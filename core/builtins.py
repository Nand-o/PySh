"""
builtins.py — Implementasi Perintah Internal (Built-in Commands)
=================================================================
Modul ini berisi implementasi perintah-perintah yang dijalankan secara
internal oleh shell, tanpa perlu memanggil program eksternal.

Mengapa Built-in Diperlukan?
    Beberapa perintah HARUS dijalankan di dalam proses shell itu sendiri
    (bukan di child process) agar efeknya berdampak pada shell. Contoh
    paling jelas adalah 'cd' (change directory): jika cd dijalankan di
    child process, maka hanya child yang berpindah direktori, sedangkan
    shell utama tetap di direktori semula.

Daftar Perintah Built-in:
    - cd [dir]   : Berpindah ke direktori yang ditentukan (atau ~ jika kosong).
    - pwd        : Menampilkan direktori kerja saat ini.
    - ls [dir]   : Menampilkan isi direktori dalam format tabel detail.
    - dir [dir]  : Alias untuk ls.
    - help       : Menampilkan daftar semua perintah built-in beserta deskripsinya.
    - history    : Menampilkan riwayat perintah yang pernah diketik.
    - exit       : Keluar dari shell PySh.
"""

import os
import stat
import datetime
from typing import List
from .history import get_history_items
from .colors import cyan, green, blue, yellow, red

# Konstanta untuk perintah exit agar konsisten di seluruh codebase
EXIT_COMMAND = "exit"

# Registry semua perintah built-in beserta deskripsi singkatnya.
# Dictionary ini juga digunakan oleh modul completion.py untuk
# menyediakan auto-complete pada nama perintah.
BUILTIN_COMMANDS = {
    "cd": "Change the shell working directory.",
    "pwd": "Print the name of the current working directory.",
    "ls": "List directory contents with details.",
    "dir": "List directory contents with details (alias for ls).",
    EXIT_COMMAND: "Exit the shell.",
    "help": "Display information about builtin commands.",
    "history": "Display the command history list."
}


def is_builtin(command: str) -> bool:
    """
    Memeriksa apakah suatu perintah termasuk built-in command.

    Args:
        command: Nama perintah yang akan diperiksa.

    Returns:
        True jika perintah terdaftar di BUILTIN_COMMANDS.
    """
    return command in BUILTIN_COMMANDS


def execute_builtin(args: List[str]) -> bool:
    """
    Mengeksekusi perintah built-in berdasarkan nama perintah di args[0].

    Args:
        args: Daftar argumen (args[0] = nama perintah, sisanya = parameter).

    Returns:
        True jika shell harus melanjutkan loop REPL.
        False jika perintah adalah 'exit' (sinyal untuk menghentikan shell).
    """
    command = args[0]

    if command == EXIT_COMMAND:
        # Perintah exit ditangani secara khusus di loop utama (pysh.py)
        return False

    if command == "cd":
        # Berpindah direktori. Jika tidak ada argumen, pindah ke home (~)
        try:
            target_dir = os.path.expanduser(args[1]) if len(args) > 1 else os.path.expanduser("~")
            os.chdir(target_dir)
        except Exception as e:
            print(red(f"cd: {e}"))
        return True

    elif command == "pwd":
        # Menampilkan direktori kerja saat ini dengan format berwarna
        try:
            print(f"Current Directory: {green(os.getcwd())}")
        except Exception as e:
            print(red(f"pwd: {e}"))
        return True

    elif command in ("ls", "dir"):
        # Menampilkan isi direktori dalam format tabel detail
        # mirip dengan output perintah 'dir' di PowerShell
        try:
            path = args[1] if len(args) > 1 else '.'
            if not os.path.exists(path):
                print(red(f"ls: cannot access '{path}': No such file or directory"))
                return True

            items = os.listdir(path) if os.path.isdir(path) else [path]

            # Header tabel dengan path absolut
            print(f"\n    Directory: {green(os.path.abspath(path))}\n")
            print(f"{'Mode':<18} {'LastWriteTime':<20} {'Length':>10} Name")
            print(f"{'----':<18} {'-------------':<20} {'------':>10} ----")

            for item in sorted(items):
                item_path = os.path.join(path, item) if os.path.isdir(path) else item
                try:
                    s = os.stat(item_path)
                    is_dir = stat.S_ISDIR(s.st_mode)

                    # Format mode: 'd----' untuk direktori, '-a---' untuk file biasa
                    win_mode = ('d' if is_dir else '-') + ('a' if not is_dir else '-') + '---'
                    # Format waktu modifikasi terakhir
                    mtime = datetime.datetime.fromtimestamp(s.st_mtime).strftime('%m/%d/%Y %I:%M %p')
                    # Ukuran file (kosong untuk direktori)
                    length = str(s.st_size) if not is_dir else ''
                    # Pewarnaan: biru untuk direktori, hijau untuk executable
                    colored_name = blue(item) if is_dir else (green(item) if os.access(item_path, os.X_OK) else item)

                    print(f"{win_mode:<18} {mtime:<20} {length:>10} {colored_name}")
                except OSError:
                    continue
            print()
        except Exception as e:
            print(red(f"{command}: {e}"))
        return True

    elif command == "help":
        # Menampilkan daftar perintah built-in dengan format rapi dan berwarna
        print(cyan("\n=== PySh - The Python Shell ==="))
        print(yellow("Built-in commands:"))
        for cmd, desc in BUILTIN_COMMANDS.items():
            print(f"  {green(cmd):<15} {desc}")
        print()
        return True

    elif command == "history":
        # Menampilkan riwayat perintah dengan nomor urut berwarna
        items = get_history_items()
        print(cyan("\n=== Command History ==="))
        for item in items:
            parts = item.split(None, 1)
            if len(parts) == 2:
                print(f"  {yellow(parts[0])}  {parts[1]}")
            else:
                print(item)
        print()
        return True

    return True
