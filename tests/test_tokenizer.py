"""
test_tokenizer.py — Unit Test untuk Modul Tokenizer
=====================================================
File ini berisi pengujian otomatis untuk memverifikasi kebenaran
fungsi tokenize_input() di modul core/tokenizer.py.

Menggunakan fitur @pytest.mark.parametrize untuk menjalankan satu
fungsi test dengan berbagai variasi input secara otomatis, sehingga
setiap skenario menjadi test case independen.

Kategori Pengujian:
    1. Perintah Sederhana    : Memastikan tokenisasi dasar berfungsi (ls, echo hello).
    2. Penanganan Kutip      : Memastikan teks di dalam tanda kutip tidak dipecah
                               dan karakter spesial di dalamnya tidak diinterpretasikan.
    3. Operator Pipe/Redirect : Memastikan |, >, >>, < dikenali sebagai operator.
    4. Redirect Stderr       : Memastikan 2>, 2>>, 2>&1 dikenali dengan benar (Fase 3).
    5. Spasi Berlebih        : Memastikan spasi ganda/triple tidak menghasilkan token kosong.
    6. Escape Character      : Memastikan backslash meng-escape karakter berikutnya.
"""

import pytest
from core.tokenizer import tokenize_input, TokenType

@pytest.mark.parametrize("command_line, expected_tokens", [
    # 1. Perintah sederhana — satu kata, dua kata, tiga kata
    ("ls", [("ls", TokenType.WORD, False)]),
    ("ls -l", [("ls", TokenType.WORD, False), ("-l", TokenType.WORD, False)]),
    ("echo hello world", [("echo", TokenType.WORD, False), ("hello", TokenType.WORD, False), ("world", TokenType.WORD, False)]),

    # 2. Penanganan kutip — teks di dalam kutip menjadi satu token utuh
    ('echo "hello world"', [("echo", TokenType.WORD, False), ("hello world", TokenType.WORD, True)]),
    ("echo 'single quotes'", [("echo", TokenType.WORD, False), ("single quotes", TokenType.WORD, True)]),
    # Karakter spesial di dalam kutip TIDAK boleh diinterpretasikan sebagai operator
    ('echo "quote with | pipe"', [("echo", TokenType.WORD, False), ("quote with | pipe", TokenType.WORD, True)]),
    ('echo "quote with > redirect"', [("echo", TokenType.WORD, False), ("quote with > redirect", TokenType.WORD, True)]),

    # 3. Operator pipe dan redirect stdout/stdin
    ("ls | grep py", [("ls", TokenType.WORD, False), ("|", TokenType.PIPE, False), ("grep", TokenType.WORD, False), ("py", TokenType.WORD, False)]),
    ("echo hi > out.txt", [("echo", TokenType.WORD, False), ("hi", TokenType.WORD, False), (">", TokenType.REDIRECT_OUT, False), ("out.txt", TokenType.WORD, False)]),
    ("echo hi >> out.txt", [("echo", TokenType.WORD, False), ("hi", TokenType.WORD, False), (">>", TokenType.REDIRECT_APPEND, False), ("out.txt", TokenType.WORD, False)]),
    ("cat < in.txt", [("cat", TokenType.WORD, False), ("<", TokenType.REDIRECT_IN, False), ("in.txt", TokenType.WORD, False)]),

    # 4. Operator redirect stderr (fitur Fase 3)
    ("ls 2> err.txt", [("ls", TokenType.WORD, False), ("2>", TokenType.REDIRECT_ERR, False), ("err.txt", TokenType.WORD, False)]),
    ("ls 2>> err.txt", [("ls", TokenType.WORD, False), ("2>>", TokenType.REDIRECT_ERR_APPEND, False), ("err.txt", TokenType.WORD, False)]),
    ("ls 2>&1", [("ls", TokenType.WORD, False), ("2>&1", TokenType.REDIRECT_ERR_TO_OUT, False)]),

    # 5. Spasi berlebih — harus ditangani tanpa menghasilkan token kosong
    ("   ls    -l   ", [("ls", TokenType.WORD, False), ("-l", TokenType.WORD, False)]),

    # 6. Escape character — backslash meng-escape spasi sehingga menjadi satu token
    ("echo escaped\\ space", [("echo", TokenType.WORD, False), ("escaped space", TokenType.WORD, False)]),
])
def test_tokenizer(command_line, expected_tokens):
    """
    Memverifikasi bahwa tokenize_input() menghasilkan daftar token yang benar
    untuk setiap variasi input yang diberikan.

    Untuk setiap token, diperiksa tiga atribut:
        - value     : Nilai string token harus sesuai.
        - type      : Tipe token (WORD, PIPE, REDIRECT_*, dll) harus sesuai.
        - is_quoted : Status kutip harus sesuai.
    """
    tokens = tokenize_input(command_line)
    assert len(tokens) == len(expected_tokens), f"Length mismatch for {command_line}"
    for i, (expected_val, expected_type, expected_quoted) in enumerate(expected_tokens):
        assert tokens[i].value == expected_val
        assert tokens[i].type == expected_type
        assert tokens[i].is_quoted == expected_quoted
