from enum import Enum, auto
import re

class TokType(Enum):
    # Palabras clave / tipos
    CLASS = auto(); INT = auto(); VOID = auto(); RETURN = auto()
    # Identificadores y literales
    ID = auto(); NUM = auto()
    # Operadores
    PLUS = auto(); MINUS = auto(); MUL = auto(); DIV = auto()
    LT = auto(); GT = auto(); EQEQ = auto(); ASSIGN = auto()
    # Símbolos
    LPAR = auto(); RPAR = auto(); LBRACE = auto(); RBRACE = auto()
    COMMA = auto(); SEMI = auto()
    # Meta
    EOF = auto(); ERROR = auto()

KEYWORDS = {
    'class': TokType.CLASS,
    'int': TokType.INT,
    'void': TokType.VOID,
    'return': TokType.RETURN,
}

SIMPLE = {
    '+': TokType.PLUS, '-': TokType.MINUS, '*': TokType.MUL, '/': TokType.DIV,
    '<': TokType.LT, '>': TokType.GT, '=': TokType.ASSIGN,
    '(': TokType.LPAR, ')': TokType.RPAR, '{': TokType.LBRACE, '}': TokType.RBRACE,
    ',': TokType.COMMA, ';': TokType.SEMI
}

TOKEN_NAMES = {t: t.name for t in TokType}

_id_re = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')
_num_re = re.compile(r'\d+')
_space_re = re.compile(r'[ \t\r\n]+')
