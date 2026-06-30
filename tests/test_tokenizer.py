import pytest
from core.tokenizer import tokenize_input, TokenType

@pytest.mark.parametrize("command_line, expected_tokens", [
    # 1. Simple commands
    ("ls", [("ls", TokenType.WORD, False)]),
    ("ls -l", [("ls", TokenType.WORD, False), ("-l", TokenType.WORD, False)]),
    ("echo hello world", [("echo", TokenType.WORD, False), ("hello", TokenType.WORD, False), ("world", TokenType.WORD, False)]),
    # 2. Quotes handling
    ('echo "hello world"', [("echo", TokenType.WORD, False), ("hello world", TokenType.WORD, True)]),
    ("echo 'single quotes'", [("echo", TokenType.WORD, False), ("single quotes", TokenType.WORD, True)]),
    ('echo "quote with | pipe"', [("echo", TokenType.WORD, False), ("quote with | pipe", TokenType.WORD, True)]),
    ('echo "quote with > redirect"', [("echo", TokenType.WORD, False), ("quote with > redirect", TokenType.WORD, True)]),
    # 3. Pipes and redirects
    ("ls | grep py", [("ls", TokenType.WORD, False), ("|", TokenType.PIPE, False), ("grep", TokenType.WORD, False), ("py", TokenType.WORD, False)]),
    ("echo hi > out.txt", [("echo", TokenType.WORD, False), ("hi", TokenType.WORD, False), (">", TokenType.REDIRECT_OUT, False), ("out.txt", TokenType.WORD, False)]),
    ("echo hi >> out.txt", [("echo", TokenType.WORD, False), ("hi", TokenType.WORD, False), (">>", TokenType.REDIRECT_APPEND, False), ("out.txt", TokenType.WORD, False)]),
    ("cat < in.txt", [("cat", TokenType.WORD, False), ("<", TokenType.REDIRECT_IN, False), ("in.txt", TokenType.WORD, False)]),
    # 4. Stderr redirects (Fase 3)
    ("ls 2> err.txt", [("ls", TokenType.WORD, False), ("2>", TokenType.REDIRECT_ERR, False), ("err.txt", TokenType.WORD, False)]),
    ("ls 2>> err.txt", [("ls", TokenType.WORD, False), ("2>>", TokenType.REDIRECT_ERR_APPEND, False), ("err.txt", TokenType.WORD, False)]),
    ("ls 2>&1", [("ls", TokenType.WORD, False), ("2>&1", TokenType.REDIRECT_ERR_TO_OUT, False)]),
    # 5. Multiple spaces
    ("   ls    -l   ", [("ls", TokenType.WORD, False), ("-l", TokenType.WORD, False)]),
    # 6. Escape characters
    ("echo escaped\\ space", [("echo", TokenType.WORD, False), ("escaped space", TokenType.WORD, False)]),
])
def test_tokenizer(command_line, expected_tokens):
    tokens = tokenize_input(command_line)
    assert len(tokens) == len(expected_tokens), f"Length mismatch for {command_line}"
    for i, (expected_val, expected_type, expected_quoted) in enumerate(expected_tokens):
        assert tokens[i].value == expected_val
        assert tokens[i].type == expected_type
        assert tokens[i].is_quoted == expected_quoted
