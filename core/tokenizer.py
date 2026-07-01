"""
tokenizer.py — Modul Tokenisasi Input (Lexical Analysis)
=========================================================
Modul ini bertanggung jawab untuk memecah string input mentah dari pengguna
menjadi daftar objek Token yang terstruktur. Proses ini sering disebut
sebagai "lexical analysis" atau "lexing" dalam teori kompilasi.

Tokenizer bekerja menggunakan pendekatan state machine (mesin keadaan) yang
membaca input karakter per karakter dan memutuskan bagaimana setiap karakter
harus diperlakukan berdasarkan konteks saat ini (apakah sedang di dalam
tanda kutip, apakah ada karakter escape, dll).

Fitur Utama:
    - Mendukung tanda kutip tunggal ('...') dan ganda ("...") untuk melindungi
      karakter spesial agar tidak diinterpretasikan sebagai operator shell.
    - Mendukung escape character (backslash '\\') untuk meng-escape karakter
      individual, misalnya: echo hello\\ world → "hello world" sebagai satu token.
    - Mengenali operator shell: | (pipe), > >> < (redirect stdout/stdin),
      2> 2>> 2>&1 (redirect stderr).
    - Menangani spasi berlebih dan whitespace (tab) secara otomatis.
    - Memberikan peringatan jika ditemukan tanda kutip yang tidak ditutup.

Contoh:
    tokenize_input('echo "hello world" > out.txt')
    → [Token("echo", WORD), Token("hello world", WORD, quoted=True),
       Token(">", REDIRECT_OUT), Token("out.txt", WORD)]
"""

from typing import List
from .token import Token, TokenType


def determine_type(value: str, is_quoted: bool) -> TokenType:
    """
    Menentukan tipe token berdasarkan nilai string dan status kutipnya.
    
    Fungsi ini adalah inti dari klasifikasi token. Logika utamanya:
    - Jika token berasal dari dalam kutip (is_quoted=True), maka apapun nilainya
      akan selalu dikembalikan sebagai WORD (teks biasa). Ini memastikan bahwa
      string seperti echo "|" tidak akan memicu operasi pipe.
    - Jika tidak dikutip, nilai string dicocokkan dengan daftar operator shell
      yang dikenali (|, >, >>, <, 2>, 2>>, 2>&1).
    
    Args:
        value (str)       : Nilai string token yang akan diklasifikasikan.
        is_quoted (bool)  : Apakah token ini berasal dari dalam tanda kutip.
    
    Returns:
        TokenType: Tipe token yang sesuai dengan nilai dan konteksnya.
    """
    # Token yang dikutip selalu dianggap sebagai teks biasa (WORD),
    # meskipun isinya adalah karakter operator shell seperti | atau >
    if is_quoted:
        return TokenType.WORD

    # Pencocokan operator shell berdasarkan nilai string
    if value == "|":
        return TokenType.PIPE
    if value == ">":
        return TokenType.REDIRECT_OUT
    if value == ">>":
        return TokenType.REDIRECT_APPEND
    if value == "<":
        return TokenType.REDIRECT_IN
    if value == "2>":
        return TokenType.REDIRECT_ERR
    if value == "2>>":
        return TokenType.REDIRECT_ERR_APPEND
    if value == "2>&1":
        return TokenType.REDIRECT_ERR_TO_OUT

    # Jika tidak cocok dengan operator manapun, maka itu adalah kata biasa
    return TokenType.WORD


def tokenize_input(command_line: str) -> List[Token]:
    """
    Memecah string input perintah menjadi daftar Token menggunakan state machine.
    
    Proses tokenisasi bekerja dengan membaca setiap karakter satu per satu
    dan menggunakan beberapa variabel keadaan (state) untuk melacak konteks:
    
    State Variables:
        - current_token (list) : Buffer karakter untuk token yang sedang dibangun.
        - in_quote (str|None)  : Menyimpan jenis kutip yang sedang aktif (' atau ").
                                 None berarti tidak sedang di dalam kutip.
        - has_quote (bool)     : Penanda apakah token saat ini mengandung kutip,
                                 digunakan untuk menentukan is_quoted pada Token.
        - escape_next (bool)   : True jika karakter berikutnya harus di-escape
                                 (diperlakukan sebagai teks biasa tanpa makna khusus).
    
    Alur Kerja:
        1. Untuk setiap karakter, cek apakah sedang dalam mode escape → tambahkan langsung.
        2. Jika karakter adalah backslash '\\' → aktifkan mode escape untuk karakter berikutnya.
        3. Jika karakter adalah tanda kutip → buka/tutup mode kutip sesuai konteks.
        4. Jika karakter adalah spasi/tab dan TIDAK di dalam kutip → selesaikan token saat ini.
        5. Selain itu → tambahkan karakter ke buffer token saat ini.
    
    Args:
        command_line (str): String input mentah dari pengguna (misalnya "ls -l | grep py").
    
    Returns:
        List[Token]: Daftar token yang terstruktur dan siap untuk diproses oleh parser.
    """
    tokens = []
    current_token = []
    in_quote = None
    has_quote = False
    escape_next = False

    for char in command_line.strip():
        # Jika karakter sebelumnya adalah backslash, karakter ini di-escape
        # (artinya diperlakukan sebagai teks biasa apapun karakternya)
        if escape_next:
            current_token.append(char)
            escape_next = False
            continue

        # Backslash mengaktifkan mode escape untuk karakter berikutnya
        if char == '\\':
            escape_next = True
            continue

        # Penanganan tanda kutip (membuka, menutup, atau kutip bersarang)
        if char in ('"', "'"):
            if in_quote == char:
                # Menutup kutip yang sama jenisnya (misalnya " menutup ")
                in_quote = None
            elif in_quote is None:
                # Membuka kutip baru (belum ada kutip yang aktif)
                in_quote = char
                has_quote = True
            else:
                # Kutip berbeda jenis di dalam kutip aktif
                # (misalnya ' di dalam "..."), diperlakukan sebagai teks biasa
                current_token.append(char)

        # Spasi atau tab di luar kutip → pemisah antar token
        elif char in (' ', '\t') and not in_quote:
            if current_token or has_quote:
                val = "".join(current_token)
                tokens.append(Token(val, determine_type(val, has_quote), has_quote))
                current_token = []
                has_quote = False
        else:
            # Karakter biasa → tambahkan ke buffer token
            current_token.append(char)

    # Peringatan jika ada kutip yang tidak ditutup
    if in_quote:
        print(f"pysh: warning: unclosed quote {in_quote}")

    # Simpan sisa buffer terakhir sebagai token (jika ada)
    if current_token or has_quote:
        val = "".join(current_token)
        tokens.append(Token(val, determine_type(val, has_quote), has_quote))
        
    return tokens
