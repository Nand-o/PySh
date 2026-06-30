import pytest
from core.tokenizer import Token, TokenType
from core.parser import parse_pipeline

@pytest.mark.parametrize("tokens, expected_segments", [
    # Simple command
    (
        [Token("ls", TokenType.WORD, False), Token("-l", TokenType.WORD, False)],
        [ {"args": ["ls", "-l"], "redirects": []} ]
    ),
    # Command with one pipe
    (
        [Token("ls", TokenType.WORD, False), Token("|", TokenType.PIPE, False), Token("grep", TokenType.WORD, False), Token("py", TokenType.WORD, False)],
        [
            {"args": ["ls"], "redirects": []},
            {"args": ["grep", "py"], "redirects": []}
        ]
    ),
    # Command with redirect out
    (
        [Token("echo", TokenType.WORD, False), Token("hi", TokenType.WORD, False), Token(">", TokenType.REDIRECT_OUT, False), Token("out.txt", TokenType.WORD, False)],
        [
            {"args": ["echo", "hi"], "redirects": [ (TokenType.REDIRECT_OUT, "out.txt") ]}
        ]
    ),
    # Command with redirect stderr to stdout (2>&1 has no target)
    (
        [Token("ls", TokenType.WORD, False), Token("2>&1", TokenType.REDIRECT_ERR_TO_OUT, False)],
        [
            {"args": ["ls"], "redirects": [ (TokenType.REDIRECT_ERR_TO_OUT, "") ]}
        ]
    ),
    # Complex chain: echo hi > out.txt | grep h 2> err.txt
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
    # Syntax error missing target
    (
        [Token("echo", TokenType.WORD, False), Token(">", TokenType.REDIRECT_OUT, False)],
        [] # parse_pipeline returns [] on syntax error
    )
])
def test_parser(tokens, expected_segments):
    segments = parse_pipeline(tokens)
    
    assert len(segments) == len(expected_segments)
    
    for i, expected in enumerate(expected_segments):
        assert segments[i].args == expected["args"]
        assert len(segments[i].redirects) == len(expected["redirects"])
        for j, (expected_type, expected_target) in enumerate(expected["redirects"]):
            assert segments[i].redirects[j].type == expected_type
            assert segments[i].redirects[j].target == expected_target
