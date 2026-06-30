from typing import List
from dataclasses import dataclass
from .token import Token, TokenType

@dataclass
class Redirect:
    type: TokenType
    target: str

@dataclass
class CommandSegment:
    args: List[str]
    redirects: List[Redirect]

def parse_pipeline(tokens: List[Token]) -> List[CommandSegment]:
    segments = []
    current_args = []
    current_redirects = []
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        if token.type == TokenType.PIPE:
            segments.append(CommandSegment(current_args, current_redirects))
            current_args = []
            current_redirects = []
            i += 1
        elif token.type in (TokenType.REDIRECT_OUT, TokenType.REDIRECT_APPEND, TokenType.REDIRECT_IN,
                            TokenType.REDIRECT_ERR, TokenType.REDIRECT_ERR_APPEND):
            if i + 1 >= len(tokens):
                print("pysh: syntax error near unexpected token 'newline'")
                return []
            current_redirects.append(Redirect(type=token.type, target=tokens[i+1].value))
            i += 2
        elif token.type == TokenType.REDIRECT_ERR_TO_OUT:
            current_redirects.append(Redirect(type=token.type, target=""))
            i += 1
        else:
            current_args.append(token.value)
            i += 1
            
    segments.append(CommandSegment(current_args, current_redirects))
    return segments
