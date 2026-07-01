"""
parser.py — Modul Parsing Token menjadi Segmen Perintah (Syntactic Analysis)
==============================================================================
Modul ini bertanggung jawab untuk mengubah daftar Token (hasil dari tokenizer)
menjadi struktur data yang lebih tinggi tingkatannya, yaitu CommandSegment.

Dalam arsitektur shell, parser berada di antara tokenizer dan executor:
    Input String → [Tokenizer] → List[Token] → [Parser] → List[CommandSegment] → [Executor]

Setiap CommandSegment merepresentasikan satu perintah lengkap yang siap
dieksekusi, termasuk argumen-argumennya dan instruksi redirection yang menyertainya.

Jika input pengguna mengandung operator pipe '|', parser akan menghasilkan
lebih dari satu CommandSegment. Misalnya:
    "ls -l | grep py > out.txt"
    → Segment 1: args=["ls", "-l"], redirects=[]
    → Segment 2: args=["grep", "py"], redirects=[Redirect(REDIRECT_OUT, "out.txt")]

Struktur Data:
    - Redirect       : Menyimpan satu instruksi redirection (tipe + file target).
    - CommandSegment  : Menyimpan satu perintah lengkap (argumen + daftar redirect).
"""

from typing import List
from dataclasses import dataclass
from .token import Token, TokenType


@dataclass
class Redirect:
    """
    Representasi satu instruksi I/O redirection.
    
    Setiap kali parser menemukan operator redirect (>, >>, <, 2>, 2>>, 2>&1),
    ia akan membuat objek Redirect untuk menyimpan informasi tersebut.
    
    Attributes:
        type (TokenType)  : Jenis redirection yang diminta (contoh: REDIRECT_OUT untuk '>').
        target (str)      : Nama file target untuk redirection.
                            Untuk operator 2>&1, target berisi string kosong ("")
                            karena tidak memerlukan file eksternal (hanya duplikasi
                            file descriptor internal).
    
    Contoh:
        Redirect(TokenType.REDIRECT_OUT, "output.txt")   → stdout ke file output.txt
        Redirect(TokenType.REDIRECT_ERR_TO_OUT, "")       → stderr digabung ke stdout
    """
    type: TokenType
    target: str


@dataclass
class CommandSegment:
    """
    Representasi satu segmen perintah yang siap dieksekusi.
    
    Satu CommandSegment berisi semua informasi yang diperlukan untuk menjalankan
    satu perintah, yaitu daftar argumen (di mana argumen pertama adalah nama
    perintah itu sendiri) dan daftar instruksi redirection.
    
    Dalam konteks pipeline (perintah yang dihubungkan dengan pipe '|'),
    setiap segmen akan dieksekusi dalam child process terpisah, dengan
    stdout dari segmen sebelumnya dihubungkan ke stdin segmen berikutnya.
    
    Attributes:
        args (List[str])         : Daftar argumen perintah.
                                   args[0] adalah nama perintah, sisanya adalah argumen.
                                   Contoh: ["grep", "-i", "hello"] → perintah "grep -i hello"
        redirects (List[Redirect]) : Daftar instruksi redirection yang harus diterapkan
                                     sebelum perintah dieksekusi.
    """
    args: List[str]
    redirects: List[Redirect]


def parse_pipeline(tokens: List[Token]) -> List[CommandSegment]:
    """
    Menguraikan daftar token menjadi daftar CommandSegment berdasarkan operator pipe.
    
    Fungsi ini melakukan iterasi linear pada daftar token dan membangun
    CommandSegment secara inkremental. Setiap kali ditemukan token PIPE,
    segmen saat ini diselesaikan dan segmen baru dimulai.
    
    Penanganan Khusus:
        - Operator redirect yang memerlukan file target (>, >>, <, 2>, 2>>):
          Parser akan mengambil token berikutnya sebagai nama file target.
          Jika tidak ada token berikutnya, muncul pesan syntax error.
        - Operator 2>&1: Tidak memerlukan file target, sehingga parser
          hanya mencatat instruksi redirect tanpa mengonsumsi token tambahan.
    
    Args:
        tokens (List[Token]): Daftar token hasil dari tokenizer.
    
    Returns:
        List[CommandSegment]: Daftar segmen perintah yang siap dieksekusi.
                              Mengembalikan list kosong [] jika terjadi syntax error.
    """
    segments = []
    current_args = []
    current_redirects = []
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        if token.type == TokenType.PIPE:
            # Operator pipe ditemukan → selesaikan segmen saat ini
            # dan mulai segmen baru untuk perintah setelah pipe
            segments.append(CommandSegment(current_args, current_redirects))
            current_args = []
            current_redirects = []
            i += 1

        elif token.type in (TokenType.REDIRECT_OUT, TokenType.REDIRECT_APPEND, TokenType.REDIRECT_IN,
                            TokenType.REDIRECT_ERR, TokenType.REDIRECT_ERR_APPEND):
            # Operator redirect yang memerlukan file target
            # Pastikan ada token berikutnya sebagai nama file
            if i + 1 >= len(tokens):
                print("pysh: syntax error near unexpected token 'newline'")
                return []
            current_redirects.append(Redirect(type=token.type, target=tokens[i+1].value))
            i += 2  # Lompati operator redirect DAN nama file target

        elif token.type == TokenType.REDIRECT_ERR_TO_OUT:
            # Operator 2>&1 → tidak memerlukan file target
            # Cukup instruksikan agar stderr dialihkan ke stdout
            current_redirects.append(Redirect(type=token.type, target=""))
            i += 1

        else:
            # Token biasa (WORD) → tambahkan ke daftar argumen
            current_args.append(token.value)
            i += 1
            
    # Jangan lupa menyimpan segmen terakhir
    segments.append(CommandSegment(current_args, current_redirects))
    return segments
