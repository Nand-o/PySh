"""
pipes.py — Modul Manajemen Pipeline Antar-Proses
==================================================
Modul ini mengimplementasikan mekanisme piping yang memungkinkan pengguna
menghubungkan output dari satu perintah ke input perintah berikutnya
menggunakan operator pipe '|'.

Konsep Dasar Pipeline:
    Pipeline adalah fitur fundamental shell UNIX yang memungkinkan
    komposisi perintah. Misalnya: 'ls -l | grep py | wc -l'
    akan menghitung jumlah file Python di direktori saat ini.

    Secara teknis, pipeline bekerja dengan:
    1. Membuat pipe (saluran komunikasi) menggunakan os.pipe().
       Setiap pipe memiliki dua ujung: read-end (r) dan write-end (w).
    2. Membuat child process untuk setiap perintah menggunakan os.fork().
    3. Menghubungkan stdout perintah ke write-end pipe, dan stdin
       perintah berikutnya ke read-end pipe yang sama.
    4. Parent process menunggu semua child process selesai.

Tipe Eksekusi:
    - Single Command (tanpa pipe):
      Built-in dijalankan langsung di parent process.
      Perintah eksternal dijalankan di satu child process.
    
    - Multi-pipe (ada operator |):
      Setiap segmen perintah dijalankan di child process terpisah,
      dengan pipe menghubungkan stdout → stdin antar segmen.
"""

import os
from typing import List
from .parser import CommandSegment
from .executor import execute_segment, execute_builtin, is_builtin, execute_single_command_windows


def execute_pipeline(segments: List[CommandSegment]) -> bool:
    """
    Mengeksekusi daftar CommandSegment, baik sebagai perintah tunggal
    maupun sebagai pipeline multi-proses.

    Alur Kerja:
        1. Validasi: Pastikan tidak ada segmen kosong (syntax error pipe).
        2. Single command: Jika hanya ada 1 segmen, jalankan langsung
           tanpa membuat pipe (lebih efisien).
        3. Multi-pipe: Jika ada lebih dari 1 segmen, buat pipe untuk
           setiap koneksi antar-segmen dan fork child process.

    Args:
        segments: Daftar CommandSegment hasil dari parser.

    Returns:
        True untuk melanjutkan loop REPL (shell tetap berjalan).
    """
    if not segments:
        return True

    # Validasi: cek apakah ada segmen kosong (misalnya "| ls" atau "ls |")
    if any(not seg.args and not seg.redirects for seg in segments):
        print("pysh: syntax error near unexpected token '|'")
        return True

    # ===== EKSEKUSI PERINTAH TUNGGAL (tanpa pipe) =====
    if len(segments) == 1:
        seg = segments[0]
        if not seg.args:
            return True

        # Built-in command dijalankan langsung di parent process
        # agar perubahan state (seperti cd) berdampak pada shell utama
        if is_builtin(seg.args[0]):
            return execute_builtin(seg.args)

        # Fallback Windows (tidak ada os.fork)
        if not hasattr(os, 'fork'):
            return execute_single_command_windows(seg)

        # POSIX: Fork child process untuk perintah eksternal
        try:
            pid = os.fork()
        except OSError as e:
            print(f"pysh: fork failed: {e}")
            return True

        if pid == 0:
            # Child process: eksekusi perintah
            execute_segment(seg)
        else:
            # Parent process: tunggu child selesai
            os.waitpid(pid, 0)
        return True

    # ===== EKSEKUSI MULTI-PIPE =====
    # Contoh: "ls | grep py | wc -l" menghasilkan 3 segmen dan 2 pipe
    if not hasattr(os, 'fork'):
        print("pysh: piping not yet fully supported on Windows")
        return True

    num_pipes = len(segments) - 1
    # Buat semua pipe yang diperlukan
    # Setiap pipe adalah tuple (read_fd, write_fd)
    pipes = [os.pipe() for _ in range(num_pipes)]
    pids = []

    for i in range(len(segments)):
        try:
            pid = os.fork()
        except OSError as e:
            print(f"pysh: fork failed: {e}")
            break

        if pid == 0:
            # === CHILD PROCESS ===
            # Hubungkan stdin ke read-end dari pipe sebelumnya
            if i > 0:
                os.dup2(pipes[i-1][0], 0)
            # Hubungkan stdout ke write-end dari pipe saat ini
            if i < num_pipes:
                os.dup2(pipes[i][1], 1)

            # Tutup SEMUA file descriptor pipe yang tidak digunakan
            # (penting untuk menghindari deadlock dan resource leak)
            for p in pipes:
                os.close(p[0])
                os.close(p[1])

            # Eksekusi perintah di segmen ini
            execute_segment(segments[i])
        else:
            # === PARENT PROCESS ===
            pids.append(pid)

    # Parent: tutup semua pipe (child sudah mengambil alih)
    for p in pipes:
        os.close(p[0])
        os.close(p[1])

    # Parent: tunggu semua child process selesai
    for pid in pids:
        os.waitpid(pid, 0)

    return True
