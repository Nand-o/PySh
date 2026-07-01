# PySh — Python Shell

PySh (PythonShell) adalah custom shell yang dikembangkan menggunakan bahasa pemrograman Python sebagai proyek tugas akhir mata kuliah **Sistem Operasi**. Shell ini mengimplementasikan konsep-konsep fundamental sistem operasi seperti *process management*, *inter-process communication (IPC)*, dan *file descriptor manipulation*.

## Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| **REPL Interaktif** | Loop baca-evaluasi-cetak yang responsif dengan prompt berwarna |
| **Tokenizer & Parser** | Pemecahan input berbasis state machine dengan dukungan kutip dan escape |
| **Pipeline (Pipe)** | Dukungan multi-pipe berantai (`cmd1 \| cmd2 \| cmd3`) via `os.pipe()` dan `os.fork()` |
| **I/O Redirection** | Redirect stdout (`>`, `>>`), stdin (`<`), dan stderr (`2>`, `2>>`, `2>&1`) |
| **Built-in Commands** | `cd`, `pwd`, `ls`/`dir`, `help`, `history`, `exit` |
| **Tab Completion** | Auto-complete untuk perintah dan path file menggunakan readline |
| **Command History** | Riwayat perintah persisten dengan navigasi panah atas/bawah |
| **Startup Config** | Eksekusi otomatis file `~/.pyshrc` saat shell dimulai |
| **Cross-Platform** | Berjalan di Linux/macOS (POSIX native) dan Windows (fallback subprocess) |

## Struktur Proyek

```
PySh/
├── pysh.py              # Entry point utama (REPL loop)
├── run_tests.bat        # Script eksekusi test suite (1-klik)
├── README.md            # Dokumentasi proyek
├── core/                # Package inti shell
│   ├── __init__.py      # Dokumentasi arsitektur package
│   ├── token.py         # Definisi Token dan TokenType (struktur data)
│   ├── tokenizer.py     # Lexical analysis (pemecahan input → token)
│   ├── parser.py        # Syntactic analysis (token → CommandSegment)
│   ├── executor.py      # Eksekusi perintah (execvp / subprocess)
│   ├── pipes.py         # Manajemen pipeline antar-proses
│   ├── redirects.py     # Manipulasi file descriptor (dup2)
│   ├── builtins.py      # Perintah internal shell
│   ├── prompt.py        # Pembuatan prompt dan pembacaan input
│   ├── colors.py        # Utilitas pewarnaan terminal (ANSI)
│   ├── history.py       # Manajemen riwayat perintah
│   └── completion.py    # Tab completion (auto-complete)
└── tests/               # Unit test (pytest)
    ├── test_tokenizer.py   # 16 test case untuk tokenizer
    ├── test_parser.py      # 6 test case untuk parser
    └── test_builtins.py    # 10 test case untuk built-in commands
```

## Cara Menjalankan

### Prasyarat
- Python 3.10 atau lebih baru
- Library tambahan: `colorama`, `pyreadline3` (Windows), `pytest` (untuk testing)

### Instalasi Dependensi
```bash
pip install colorama pyreadline3 pytest
```

### Menjalankan Shell
```bash
python pysh.py
```

### Menjalankan Test Suite
```bash
# Windows (1-klik)
.\run_tests.bat

# Atau manual
set PYTHONPATH=. && pytest tests/ -v
```

## Arsitektur & Aliran Data

```
Input Pengguna
      │
      ▼
┌─────────────┐
│  Tokenizer  │  Memecah string input menjadi daftar Token
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Parser    │  Mengelompokkan Token menjadi CommandSegment
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌────────────┐
│   Pipes     │────▶│  Executor  │  Menjalankan perintah (fork + execvp)
└──────┬──────┘     └────────────┘
       │
       ▼
┌─────────────┐
│  Redirects  │  Mengalihkan file descriptor (stdin/stdout/stderr)
└─────────────┘
```

## Konsep Sistem Operasi yang Diimplementasikan

1. **Process Creation** — Menggunakan `os.fork()` untuk membuat child process.
2. **Program Execution** — Menggunakan `os.execvp()` untuk mengganti image proses.
3. **Inter-Process Communication** — Menggunakan `os.pipe()` untuk komunikasi antar-proses.
4. **File Descriptor Manipulation** — Menggunakan `os.dup2()` untuk I/O redirection.
5. **Process Synchronization** — Menggunakan `os.waitpid()` untuk sinkronisasi parent-child.

## Lisensi

Proyek ini dikembangkan untuk keperluan akademis pada mata kuliah Sistem Operasi, Universitas Negeri Jakarta.
