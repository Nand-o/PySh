"""
colors.py — Utilitas Pewarnaan Teks Terminal
=============================================
Modul ini menyediakan fungsi-fungsi pembantu untuk menambahkan warna
pada teks yang ditampilkan di terminal menggunakan ANSI escape codes.

PySh menggunakan library 'colorama' sebagai backend pewarnaan karena
library ini secara otomatis menangani kompatibilitas ANSI escape codes
di Windows (yang secara default tidak mendukungnya).

Fitur Keamanan:
    Pewarnaan hanya diaktifkan jika output shell terhubung ke terminal
    interaktif (dicek menggunakan os.isatty(1)). Jika output dialihkan
    ke file atau pipe, warna akan dinonaktifkan secara otomatis agar
    tidak mengotori output dengan karakter escape yang tidak terbaca.

Warna yang Tersedia:
    - cyan()   : Warna cyan — digunakan untuk prompt dan header.
    - green()  : Warna hijau — digunakan untuk path, file executable.
    - blue()   : Warna biru — digunakan untuk nama direktori.
    - red()    : Warna merah — digunakan untuk pesan error.
    - yellow() : Warna kuning — digunakan untuk nomor urut dan label.
"""

import os
import colorama

# Inisialisasi colorama agar ANSI escape codes berfungsi di Windows
colorama.init()


def is_colors_supported() -> bool:
    """
    Memeriksa apakah terminal mendukung pewarnaan.

    Pewarnaan hanya diaktifkan jika stdout (FD 1) terhubung ke terminal
    sesungguhnya (TTY). Jika output di-redirect ke file atau pipe,
    fungsi ini mengembalikan False sehingga teks ditampilkan tanpa
    kode warna yang akan mengotori output.

    Returns:
        True jika terminal mendukung warna, False jika tidak.
    """
    try:
        return os.isatty(1)
    except Exception:
        return False


def cyan(text: str) -> str:
    """Membungkus teks dengan warna cyan. Digunakan untuk prompt dan header."""
    return f"{colorama.Fore.CYAN}{text}{colorama.Style.RESET_ALL}" if is_colors_supported() else text


def green(text: str) -> str:
    """Membungkus teks dengan warna hijau. Digunakan untuk path dan file executable."""
    return f"{colorama.Fore.GREEN}{text}{colorama.Style.RESET_ALL}" if is_colors_supported() else text


def blue(text: str) -> str:
    """Membungkus teks dengan warna biru. Digunakan untuk nama direktori."""
    return f"{colorama.Fore.BLUE}{text}{colorama.Style.RESET_ALL}" if is_colors_supported() else text


def red(text: str) -> str:
    """Membungkus teks dengan warna merah. Digunakan untuk pesan error."""
    return f"{colorama.Fore.RED}{text}{colorama.Style.RESET_ALL}" if is_colors_supported() else text


def yellow(text: str) -> str:
    """Membungkus teks dengan warna kuning. Digunakan untuk nomor urut dan label."""
    return f"{colorama.Fore.YELLOW}{text}{colorama.Style.RESET_ALL}" if is_colors_supported() else text
