"""
executor.py — Modul Eksekusi Perintah Eksternal
=================================================
Modul ini bertanggung jawab untuk mengeksekusi perintah eksternal (program
yang terinstal di sistem operasi, seperti grep, cat, python, dll) dari
dalam child process shell PySh.

Mekanisme Eksekusi (POSIX/Linux):
    Pada sistem POSIX, eksekusi perintah dilakukan melalui system call
    os.execvp(). Fungsi ini menggantikan image proses saat ini dengan
    program baru. Artinya, setelah execvp dipanggil, kode di bawahnya
    TIDAK AKAN PERNAH dieksekusi (kecuali jika execvp gagal).

    execvp melakukan pencarian otomatis di direktori-direktori yang
    terdaftar dalam variabel lingkungan PATH.

Mekanisme Fallback (Windows):
    Karena Windows tidak memiliki os.fork() dan os.execvp(), modul ini
    menyediakan fungsi fallback yang menggunakan subprocess.run() dengan
    parameter shell=False untuk keamanan (menghindari shell injection).
"""

import os
import sys
from typing import List
from .parser import CommandSegment
from .redirects import apply_redirects
from .builtins import execute_builtin, is_builtin


def execute_external_command(args: List[str]):
    """
    Menjalankan perintah eksternal menggunakan POSIX execvp.

    Fungsi ini HANYA boleh dipanggil dari dalam child process (setelah fork),
    karena os.execvp() akan menggantikan seluruh proses saat ini dengan
    program yang dituju. Proses pemanggil tidak akan kembali ke sini.

    Args:
        args: Daftar argumen perintah (args[0] = nama program).

    Catatan:
        - FileNotFoundError terjadi jika program tidak ditemukan di PATH.
        - Fungsi ini memanggil sys.exit() pada kasus error karena child
          process harus segera dihentikan agar tidak terus berjalan.
    """
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
    """
    Mengeksekusi satu CommandSegment di dalam child process.

    Fungsi ini menangani alur lengkap eksekusi satu segmen perintah:
    1. Validasi bahwa segmen memiliki argumen.
    2. Terapkan semua instruksi redirection (jika ada).
    3. Cek apakah perintah adalah built-in → jalankan built-in.
    4. Jika bukan built-in → delegasikan ke execute_external_command.

    Args:
        segment: Objek CommandSegment yang berisi args dan redirects.

    Catatan:
        Fungsi ini selalu diakhiri dengan sys.exit() karena dipanggil
        dari child process yang harus segera berhenti setelah selesai.
    """
    if not segment.args:
        sys.exit(0)

    # Terapkan redirection sebelum eksekusi
    if not apply_redirects(segment.redirects):
        sys.exit(1)

    if is_builtin(segment.args[0]):
        # Di dalam child, eksekusi builtin lalu exit
        execute_builtin(segment.args)
        sys.exit(0)
    else:
        execute_external_command(segment.args)


def execute_single_command_windows(segment: CommandSegment) -> bool:
    """
    Fallback eksekusi perintah untuk sistem Windows.

    Karena Windows tidak mendukung os.fork() dan os.execvp(), fungsi ini
    menggunakan modul subprocess sebagai alternatif. Parameter shell=False
    digunakan untuk mencegah kerentanan shell injection.

    Args:
        segment: Objek CommandSegment yang akan dieksekusi.

    Returns:
        True untuk melanjutkan loop REPL.
    """
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
