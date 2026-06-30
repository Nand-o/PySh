"""
history.py — Modul Manajemen Riwayat Perintah (Command History)
================================================================
Modul ini mengelola fitur riwayat perintah yang memungkinkan pengguna
untuk mengakses kembali perintah-perintah yang pernah diketik sebelumnya.

Fitur ini memanfaatkan modul 'readline' (atau 'pyreadline3' di Windows)
yang menyediakan kemampuan:
    - Navigasi riwayat menggunakan tombol panah atas/bawah.
    - Pencarian riwayat (Ctrl+R pada terminal yang mendukung).
    - Penyimpanan riwayat secara persisten ke file.

File Riwayat:
    Riwayat perintah disimpan di file ~/.pysh_history di direktori home
    pengguna. File ini dibaca saat shell dimulai dan ditulis saat shell
    ditutup, sehingga riwayat tetap ada antar sesi penggunaan.

Batas Riwayat:
    Maksimal 1000 entri perintah disimpan untuk menghindari file
    riwayat yang terlalu besar.
"""

import os

# Impor modul readline dengan fallback yang aman.
# Di Linux, modul ini tersedia secara bawaan.
# Di Windows, memerlukan instalasi package 'pyreadline3'.
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

# Lokasi file penyimpanan riwayat perintah
HISTORY_FILE = os.path.expanduser("~/.pysh_history")

# Jumlah maksimal entri riwayat yang disimpan
MAX_HISTORY_LENGTH = 1000


def init_history():
    """
    Menginisialisasi sistem riwayat perintah saat shell dimulai.

    Fungsi ini:
    1. Memuat riwayat dari file ~/.pysh_history (jika ada).
    2. Mengatur batas maksimal jumlah entri riwayat.

    Jika modul readline tidak tersedia, fungsi ini tidak melakukan apa-apa.
    """
    if not READLINE_AVAILABLE:
        return

    if os.path.exists(HISTORY_FILE):
        try:
            readline.read_history_file(HISTORY_FILE)
        except Exception:
            pass
    readline.set_history_length(MAX_HISTORY_LENGTH)


def save_history():
    """
    Menyimpan riwayat perintah ke file saat shell ditutup.

    Dipanggil sebelum shell keluar (setelah pengguna mengetik 'exit')
    untuk memastikan semua perintah yang diketik pada sesi ini
    tersimpan secara persisten.
    """
    if not READLINE_AVAILABLE:
        return

    try:
        readline.write_history_file(HISTORY_FILE)
    except Exception:
        pass


def get_history_items():
    """
    Mengambil seluruh entri riwayat perintah dalam format yang siap ditampilkan.

    Setiap entri diformat sebagai string "nomor  perintah", misalnya:
        "   1  ls -l"
        "   2  cd /home"

    Returns:
        List[str]: Daftar string riwayat yang sudah diformat.
                   Jika readline tidak tersedia, mengembalikan pesan informatif.
    """
    if not READLINE_AVAILABLE:
        return ["History feature is not available (readline module not found)."]

    length = readline.get_current_history_length()
    items = []
    # Indeks readline dimulai dari 1 (bukan 0)
    for i in range(1, length + 1):
        item = readline.get_history_item(i)
        if item:
            items.append(f"{i:4d}  {item}")
    return items
