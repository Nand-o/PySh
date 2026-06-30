import pytest
from core.builtins import is_builtin

@pytest.mark.parametrize("command, expected", [
    ("cd", True),
    ("pwd", True),
    ("ls", True),
    ("dir", True),
    ("history", True),
    ("help", True),
    ("exit", True),
    ("echo", False),
    ("grep", False),
    ("cat", False),
])
def test_is_builtin(command, expected):
    assert is_builtin(command) == expected
