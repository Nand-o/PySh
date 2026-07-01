"""
redirects.py — Modul Manipulasi File Descriptor untuk I/O Redirection
======================================================================
Modul ini mengimplementasikan mekanisme I/O redirection pada shell PySh.

Konsep Dasar File Descriptor (FD):
    - FD 0 (stdin)  : Sumber data masukan (biasanya keyboard).
    - FD 1 (stdout) : Tujuan output normal (biasanya terminal).
    - FD 2 (stderr) : Tujuan pesan error (biasanya terminal).

    Redirection bekerja dengan mengalihkan FD menggunakan system call os.dup2().

Operator yang Didukung:
    >    : Redirect stdout ke file (overwrite).
    >>   : Redirect stdout ke file (append).
    <    : Redirect stdin dari file.
    2>   : Redirect stderr ke file (overwrite).
    2>>  : Redirect stderr ke file (append).
    2>&1 : Redirect stderr ke stdout (gabungkan keduanya).
"""

import os
from .token import TokenType
from .parser import Redirect
from typing import List


def apply_redirects(redirects: List[Redirect]) -> bool:
    """
    Menerapkan semua instruksi redirection pada proses saat ini.

    Dipanggil di dalam child process sebelum perintah dieksekusi.
    Memproses setiap Redirect secara berurutan menggunakan os.dup2().

    Args:
        redirects: Daftar instruksi redirection dari CommandSegment.

    Returns:
        True jika semua berhasil, False jika ada kegagalan.
    """
    for red in redirects:
        try:
            if red.type == TokenType.REDIRECT_OUT:
                # '>' → stdout ke file (overwrite)
                fd = os.open(red.target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
                os.dup2(fd, 1)
                os.close(fd)
            elif red.type == TokenType.REDIRECT_APPEND:
                # '>>' → stdout ke file (append)
                fd = os.open(red.target, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
                os.dup2(fd, 1)
                os.close(fd)
            elif red.type == TokenType.REDIRECT_IN:
                # '<' → stdin dari file
                fd = os.open(red.target, os.O_RDONLY)
                os.dup2(fd, 0)
                os.close(fd)
            elif red.type == TokenType.REDIRECT_ERR:
                # '2>' → stderr ke file (overwrite)
                fd = os.open(red.target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
                os.dup2(fd, 2)
                os.close(fd)
            elif red.type == TokenType.REDIRECT_ERR_APPEND:
                # '2>>' → stderr ke file (append)
                fd = os.open(red.target, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
                os.dup2(fd, 2)
                os.close(fd)
            elif red.type == TokenType.REDIRECT_ERR_TO_OUT:
                # '2>&1' → gabungkan stderr ke stdout
                os.dup2(1, 2)
        except OSError as e:
            print(f"pysh: {red.target}: {e.strerror}")
            return False
    return True
