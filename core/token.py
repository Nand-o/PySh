from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
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
    value: str
    type: TokenType
    is_quoted: bool

    def __str__(self):
        return self.value
