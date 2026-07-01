"""
token.py — Definisi Struktur Data Token
========================================
Modul ini mendefinisikan dua komponen fundamental yang menjadi dasar dari
seluruh proses parsing di PySh:

1. TokenType (Enum):
   Enumerasi yang mengklasifikasikan jenis-jenis token yang dikenali oleh shell.
   Setiap karakter atau kelompok karakter yang memiliki makna khusus dalam shell
   (seperti pipe '|' atau redirect '>') memiliki tipe tersendiri.

2. Token (Dataclass):
   Struktur data immutable yang merepresentasikan satu unit terkecil dari input
   pengguna setelah proses tokenisasi. Setiap token menyimpan tiga informasi:
   - value     : Nilai string asli dari token tersebut.
   - type      : Klasifikasi tipe token (WORD, PIPE, REDIRECT_OUT, dll).
   - is_quoted : Penanda apakah token ini berasal dari dalam tanda kutip,
                 yang berarti karakter spesial di dalamnya harus diperlakukan
                 sebagai teks biasa (bukan operator).

Contoh Penggunaan:
    Token("hello", TokenType.WORD, False)       → kata biasa
    Token("|", TokenType.PIPE, False)            → operator pipe
    Token("|", TokenType.WORD, True)             → teks literal "|" (di dalam kutip)
"""

from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    """
    Enumerasi tipe-tipe token yang dikenali oleh tokenizer PySh.
    
    Kategori:
        - WORD              : Teks biasa (nama perintah, argumen, nama file).
        - PIPE              : Operator pipe '|' untuk menghubungkan stdout ke stdin.
        - REDIRECT_OUT      : Operator '>' untuk menulis stdout ke file (overwrite).
        - REDIRECT_APPEND   : Operator '>>' untuk menulis stdout ke file (append/tambah).
        - REDIRECT_IN       : Operator '<' untuk membaca stdin dari file.
        - REDIRECT_ERR      : Operator '2>' untuk menulis stderr ke file (overwrite).
        - REDIRECT_ERR_APPEND   : Operator '2>>' untuk menulis stderr ke file (append).
        - REDIRECT_ERR_TO_OUT   : Operator '2>&1' untuk menggabungkan stderr ke stdout.
    """
    WORD = auto()
    PIPE = auto()
    REDIRECT_OUT = auto()
    REDIRECT_APPEND = auto()
    REDIRECT_IN = auto()
    REDIRECT_ERR = auto()
    REDIRECT_ERR_APPEND = auto()
    REDIRECT_ERR_TO_OUT = auto()


@dataclass(frozen=True)
class Token:
    """
    Representasi satu unit token hasil pemecahan input pengguna.
    
    Menggunakan frozen=True agar token bersifat immutable (tidak bisa diubah
    setelah dibuat), yang menjamin keamanan data selama proses parsing.
    
    Attributes:
        value (str)         : Nilai string dari token (misalnya "echo", ">", "file.txt").
        type (TokenType)    : Tipe token yang menentukan bagaimana token akan diproses.
        is_quoted (bool)    : True jika token berasal dari dalam tanda kutip.
                              Jika True, token selalu dianggap WORD meskipun nilainya
                              adalah karakter spesial seperti '|' atau '>'.
    """
    value: str
    type: TokenType
    is_quoted: bool

    def __str__(self):
        """Mengembalikan nilai string dari token untuk kemudahan debugging dan tampilan."""
        return self.value
