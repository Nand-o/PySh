from typing import List
from .token import Token, TokenType

def determine_type(value: str, is_quoted: bool) -> TokenType:
    if is_quoted:
        return TokenType.WORD
    if value == "|":
        return TokenType.PIPE
    if value == ">":
        return TokenType.REDIRECT_OUT
    if value == ">>":
        return TokenType.REDIRECT_APPEND
    if value == "<":
        return TokenType.REDIRECT_IN
    return TokenType.WORD

def tokenize_input(command_line: str) -> List[Token]:
    tokens = []
    current_token = []
    in_quote = None
    has_quote = False
    escape_next = False

    for char in command_line.strip():
        if escape_next:
            current_token.append(char)
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char in ('"', "'"):
            if in_quote == char:
                in_quote = None
            elif in_quote is None:
                in_quote = char
                has_quote = True
            else:
                current_token.append(char)
        elif char in (' ', '\t') and not in_quote:
            if current_token or has_quote:
                val = "".join(current_token)
                tokens.append(Token(val, determine_type(val, has_quote), has_quote))
                current_token = []
                has_quote = False
        else:
            current_token.append(char)
            
    if in_quote:
        print(f"pysh: warning: unclosed quote {in_quote}")
            
    if current_token or has_quote:
        val = "".join(current_token)
        tokens.append(Token(val, determine_type(val, has_quote), has_quote))
        
    return tokens
