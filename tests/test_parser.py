"""
test_parser.py — Unit Test untuk Modul Parser
===============================================
File ini berisi pengujian otomatis untuk memverifikasi kebenaran
fungsi parse_pipeline() di modul core/parser.py.

Pengujian dilakukan dengan menyediakan daftar Token secara langsung
(bukan string input mentah) untuk mengisolasi pengujian parser dari
tokenizer. Dengan demikian, jika test ini gagal, kita tahu pasti
bahwa masalahnya ada di parser, bukan di tokenizer.

Kategori Pengujian:
    1. Perintah Sederhana    : Satu perintah tanpa pipe atau redirect.
    2. Pipeline dengan Pipe  : Dua perintah yang dihubungkan dengan pipe.
    3. Redirect Stdout       : Perintah dengan operator > dan file target.
    4. Redirect Stderr       : Perintah dengan operator 2>&1 (tanpa file target).
    5. Pipeline Kompleks     : Kombinasi pipe, redirect stdout, dan redirect stderr.
    6. Syntax Error          : Operator redirect tanpa file target (harus mengembalikan []).
"""

import pytest
from core.tokenizer import Token, TokenType
from core.parser import parse_pipeline

@pytest.mark.parametrize("tokens, expected_segments", [
    # 1. Perintah sederhana: "ls -l" → 1 segmen dengan 2 argumen
    (
        [Token("ls", TokenType.WORD, False), Token("-l", TokenType.WORD, False)],
        [ {"args": ["ls", "-l"], "redirects": []} ]
    ),

    # 2. Pipeline: "ls | grep py" → 2 segmen terpisah oleh pipe
    (
        [Token("ls", TokenType.WORD, False), Token("|", TokenType.PIPE, False), Token("grep", TokenType.WORD, False), Token("py", TokenType.WORD, False)],
        [
            {"args": ["ls"], "redirects": []},
            {"args": ["grep", "py"], "redirects": []}
        ]
    ),

    # 3. Redirect stdout: "echo hi > out.txt" → 1 segmen dengan 1 redirect
    (
        [Token("echo", TokenType.WORD, False), Token("hi", TokenType.WORD, False), Token(">", TokenType.REDIRECT_OUT, False), Token("out.txt", TokenType.WORD, False)],
        [
            {"args": ["echo", "hi"], "redirects": [ (TokenType.REDIRECT_OUT, "out.txt") ]}
        ]
    ),

    # 4. Redirect stderr ke stdout: "ls 2>&1" → target kosong (tidak butuh file)
    (
        [Token("ls", TokenType.WORD, False), Token("2>&1", TokenType.REDIRECT_ERR_TO_OUT, False)],
        [
            {"args": ["ls"], "redirects": [ (TokenType.REDIRECT_ERR_TO_OUT, "") ]}
        ]
    ),

    # 5. Pipeline kompleks: "echo hi > out.txt | grep h 2> err.txt"
    (
        [
            Token("echo", TokenType.WORD, False), Token("hi", TokenType.WORD, False), Token(">", TokenType.REDIRECT_OUT, False), Token("out.txt", TokenType.WORD, False),
            Token("|", TokenType.PIPE, False),
            Token("grep", TokenType.WORD, False), Token("h", TokenType.WORD, False), Token("2>", TokenType.REDIRECT_ERR, False), Token("err.txt", TokenType.WORD, False)
        ],
        [
            {"args": ["echo", "hi"], "redirects": [ (TokenType.REDIRECT_OUT, "out.txt") ]},
            {"args": ["grep", "h"], "redirects": [ (TokenType.REDIRECT_ERR, "err.txt") ]}
        ]
    ),

    # 6. Syntax error: "echo >" tanpa file target → parser mengembalikan []
    (
        [Token("echo", TokenType.WORD, False), Token(">", TokenType.REDIRECT_OUT, False)],
        []
    )
])
def test_parser(tokens, expected_segments):
    """
    Memverifikasi bahwa parse_pipeline() menghasilkan daftar CommandSegment
    yang benar untuk setiap variasi input token.

    Untuk setiap segmen, diperiksa:
        - args      : Daftar argumen harus sesuai.
        - redirects : Jumlah, tipe, dan target redirect harus sesuai.
    """
    segments = parse_pipeline(tokens)

    assert len(segments) == len(expected_segments)

    for i, expected in enumerate(expected_segments):
        assert segments[i].args == expected["args"]
        assert len(segments[i].redirects) == len(expected["redirects"])
        for j, (expected_type, expected_target) in enumerate(expected["redirects"]):
            assert segments[i].redirects[j].type == expected_type
            assert segments[i].redirects[j].target == expected_target
