"""
pysh.py — Entry Point Utama PySh (Python Shell)
=================================================
File ini adalah titik masuk (entry point) utama dari shell PySh.
Ia bertanggung jawab untuk menginisialisasi seluruh subsistem shell
dan menjalankan REPL (Read-Eval-Print Loop), yaitu siklus utama
yang terus membaca input, memprosesnya, dan menampilkan hasilnya.

Alur Kerja Utama:
    1. Inisialisasi: Memuat riwayat perintah, mengaktifkan tab completion,
       dan mengeksekusi file konfigurasi ~/.pyshrc (jika ada).
    2. Loop REPL:
       a. Tampilkan prompt → Baca input pengguna.
       b. Tokenisasi input → Parsing menjadi CommandSegment.
       c. Eksekusi pipeline/perintah.
       d. Ulangi sampai pengguna mengetik 'exit'.
    3. Cleanup: Simpan riwayat perintah ke file sebelum keluar.

Penanganan Error:
    - KeyboardInterrupt (Ctrl+C) : Membatalkan input saat ini tanpa
      menghentikan shell. Prompt baru akan ditampilkan.
    - Exception umum : Ditangkap dan ditampilkan sebagai pesan error,
      menjaga shell tetap berjalan meskipun terjadi kesalahan.

Cara Menjalankan:
    $ python pysh.py
"""

from core.prompt import get_prompt, read_input
from core.tokenizer import tokenize_input
from core.parser import parse_pipeline
from core.pipes import execute_pipeline
from core.builtins import EXIT_COMMAND
from core.history import init_history, save_history
from core.completion import init_completion
import os


def load_pyshrc():
    """
    Memuat dan mengeksekusi file konfigurasi startup ~/.pyshrc.

    File .pyshrc berfungsi seperti .bashrc pada Bash — berisi perintah-
    perintah yang akan dieksekusi secara otomatis setiap kali shell
    dibuka. Berguna untuk mengatur alias, variabel lingkungan, atau
    perintah inisialisasi lainnya.

    Format file:
        - Baris kosong dan baris yang diawali '#' (komentar) diabaikan.
        - Setiap baris lainnya diperlakukan sebagai perintah shell biasa.

    Contoh isi ~/.pyshrc:
        # Konfigurasi PySh
        cd ~/projects
    """
    pyshrc_path = os.path.expanduser("~/.pyshrc")
    if os.path.exists(pyshrc_path):
        try:
            with open(pyshrc_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Lewati baris kosong dan komentar
                    if not line or line.startswith('#'):
                        continue
                    tokens = tokenize_input(line)
                    segments = parse_pipeline(tokens)
                    if segments:
                        execute_pipeline(segments)
        except Exception as e:
            print(f"pysh: error loading .pyshrc: {e}")


def run_shell():
    """
    Fungsi utama yang menjalankan REPL (Read-Eval-Print Loop).

    REPL adalah pola desain standar untuk program interaktif:
        - Read  : Membaca input dari pengguna melalui prompt.
        - Eval  : Memproses input (tokenisasi → parsing → eksekusi).
        - Print : Menampilkan hasil eksekusi (dilakukan oleh perintah itu sendiri).
        - Loop  : Mengulangi proses di atas sampai pengguna mengetik 'exit'.

    Inisialisasi yang dilakukan sebelum loop dimulai:
        1. init_history()   : Memuat riwayat perintah dari sesi sebelumnya.
        2. init_completion() : Mengaktifkan fitur Tab completion.
        3. load_pyshrc()    : Mengeksekusi file konfigurasi startup.

    Cleanup yang dilakukan setelah loop berakhir:
        1. save_history()   : Menyimpan riwayat perintah ke file.
    """
    # === FASE INISIALISASI ===
    init_history()
    init_completion()
    load_pyshrc()

    # === FASE LOOP UTAMA (REPL) ===
    while True:
        try:
            # READ: Tampilkan prompt dan baca input pengguna
            user_input = read_input(get_prompt())

            # Abaikan input kosong (pengguna hanya menekan Enter)
            if not user_input.strip():
                continue

            # EVAL: Tokenisasi → Parsing
            tokens = tokenize_input(user_input)
            segments = parse_pipeline(tokens)

            # Jika parsing gagal (syntax error), lanjut ke prompt berikutnya
            if not segments:
                continue

            # Cek perintah exit secara khusus di parent process.
            # Perintah exit harus ditangani di sini (bukan di builtins)
            # karena hanya parent process yang bisa menghentikan loop REPL.
            if len(segments) == 1 and segments[0].args and segments[0].args[0] == EXIT_COMMAND:
                print("Cihuyyy!\n")
                break

            # EVAL + PRINT: Eksekusi pipeline (output ditangani oleh perintah)
            execute_pipeline(segments)

        except KeyboardInterrupt:
            # Ctrl+C: Batalkan input saat ini, tampilkan prompt baru
            print()
            continue
        except Exception as e:
            # Safety net: tangkap semua error tak terduga
            # agar shell tidak crash dan terus berjalan
            print(f"pysh: unexpected error: {e}")
            continue

    # === FASE CLEANUP ===
    save_history()


# Entry point: jalankan shell jika file ini dieksekusi langsung
if __name__ == "__main__":
    run_shell()