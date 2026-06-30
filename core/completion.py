"""
completion.py — Modul Tab Completion (Auto-Complete)
=====================================================
Modul ini mengimplementasikan fitur auto-complete yang diaktifkan
dengan menekan tombol Tab saat mengetik perintah di shell PySh.

Tab completion mempercepat pengetikan dan mengurangi kesalahan ketik
dengan menyarankan kemungkinan pelengkapan berdasarkan konteks:

Konteks Pelengkapan:
    1. Posisi Perintah (awal baris):
       Menyarankan nama-nama perintah built-in PySh dan program
       executable yang ditemukan di direktori-direktori PATH.
       Contoh: mengetik "he" lalu Tab → "help"

    2. Posisi Argumen (setelah spasi):
       Menyarankan nama file dan direktori di folder saat ini.
       Direktori secara otomatis ditambahkan separator (/ atau \\)
       untuk mempermudah navigasi lebih dalam.
       Contoh: mengetik "cd co" lalu Tab → "cd core/"

Caching:
    Daftar executable di PATH di-cache setelah pembacaan pertama
    untuk menghindari pemindaian berulang yang lambat.
"""

import os
import glob

# Impor readline dengan fallback aman
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

from .builtins import BUILTIN_COMMANDS


def get_executables_in_path():
    """
    Mengumpulkan daftar semua file executable yang ada di direktori PATH.

    Fungsi ini memindai setiap direktori yang terdaftar dalam variabel
    lingkungan PATH dan mengumpulkan nama-nama file di dalamnya.

    Returns:
        List[str]: Daftar nama file executable yang ditemukan.
    """
    executables = []
    path_env = os.environ.get("PATH", "")
    for p in path_env.split(os.pathsep):
        if os.path.isdir(p):
            try:
                for f in os.listdir(p):
                    executables.append(f)
            except Exception:
                # Abaikan direktori yang tidak bisa dibaca (permission denied, dll)
                pass
    return executables


class Completer:
    """
    Kelas yang menangani logika auto-complete untuk readline.

    Readline memanggil method complete() berulang kali dengan nilai
    state yang bertambah (0, 1, 2, ...) sampai mendapat None, yang
    menandakan tidak ada lagi opsi pelengkapan.

    Attributes:
        options (list)     : Daftar opsi pelengkapan yang cocok untuk input saat ini.
        executables (list) : Cache daftar executable di PATH (di-load sekali saja).
    """

    def __init__(self):
        self.options = []
        self.executables = None

    def complete(self, text, state):
        """
        Fungsi callback yang dipanggil oleh readline saat pengguna menekan Tab.

        Args:
            text (str) : Teks yang sedang diketik oleh pengguna (bagian terakhir).
            state (int): Indeks opsi yang diminta (0 = pertama, 1 = kedua, dst).

        Returns:
            str atau None: Opsi pelengkapan ke-state, atau None jika habis.
        """
        line = readline.get_line_buffer()

        if state == 0:
            # State 0: Bangun daftar opsi pelengkapan
            if not line.strip() or line.rfind(" ") == -1 or line.rfind(" ") == len(line) - 1:
                # Konteks: mengetik nama perintah (posisi pertama)
                if self.executables is None:
                    self.executables = get_executables_in_path()
                opts = list(BUILTIN_COMMANDS.keys()) + self.executables
                self.options = [cmd for cmd in opts if cmd.startswith(text)]
            else:
                # Konteks: mengetik argumen (posisi setelah spasi)
                # Gunakan glob untuk mencocokkan nama file
                matches = glob.glob(text + "*")

                # Tambahkan separator untuk direktori agar mudah dinavigasi
                self.options = []
                for m in matches:
                    if os.path.isdir(m):
                        self.options.append(m + os.sep)
                    else:
                        self.options.append(m)

        try:
            return self.options[state]
        except IndexError:
            return None


def init_completion():
    """
    Menginisialisasi sistem tab completion pada saat shell dimulai.

    Fungsi ini:
    1. Membuat instance Completer dan mendaftarkannya ke readline.
    2. Mengaktifkan binding tombol Tab untuk trigger auto-complete.
    3. Menangani perbedaan konfigurasi antara GNU readline dan BSD libedit
       (yang digunakan di macOS).
    """
    if not READLINE_AVAILABLE:
        return

    completer = Completer()
    readline.set_completer(completer.complete)

    # Binding Tab berbeda antara GNU readline dan BSD libedit (macOS)
    doc = getattr(readline, '__doc__', '')
    if doc and 'libedit' in doc:
        readline.parse_and_bind('bind ^I rl_complete')
    else:
        readline.parse_and_bind('tab: complete')
