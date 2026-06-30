"""
core/ — Package Inti PySh (Python Shell)
=========================================
Package ini berisi seluruh modul inti yang membentuk arsitektur internal dari
PySh. Setiap modul dirancang dengan prinsip Single Responsibility, di mana
masing-masing hanya menangani satu aspek spesifik dari operasi shell.

Daftar Modul:
    - token.py      : Definisi struktur data Token dan enumerasi TokenType.
    - tokenizer.py  : Proses pemecahan input string menjadi daftar Token (lexical analysis).
    - parser.py     : Proses pengelompokan Token menjadi CommandSegment (syntactic analysis).
    - executor.py   : Pendelegasian eksekusi perintah ke sistem operasi (via execvp/subprocess).
    - pipes.py      : Manajemen pipeline antar-proses menggunakan os.pipe() dan os.fork().
    - redirects.py  : Manipulasi file descriptor untuk I/O redirection (stdin, stdout, stderr).
    - builtins.py   : Implementasi perintah internal shell (cd, pwd, ls, help, history, exit).
    - prompt.py     : Pembuatan string prompt dan pembacaan input pengguna.
    - colors.py     : Utilitas pewarnaan teks terminal menggunakan ANSI escape codes.
    - history.py    : Manajemen riwayat perintah (persistent history via readline).
    - completion.py : Fitur auto-complete (Tab completion) untuk perintah dan path file.

Arsitektur Aliran Data:
    Input Pengguna → tokenizer → parser → pipes/executor → Output
    
    1. Pengguna mengetik perintah di prompt (prompt.py).
    2. Input dipecah menjadi token-token (tokenizer.py).
    3. Token dikelompokkan menjadi segmen perintah beserta redirect-nya (parser.py).
    4. Segmen dieksekusi, baik secara langsung maupun melalui pipeline (pipes.py, executor.py).
    5. Jika ada redirect, file descriptor dimanipulasi sebelum eksekusi (redirects.py).
"""
