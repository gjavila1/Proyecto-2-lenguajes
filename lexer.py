# === lexer.py ===
# Módulo compatible con app.py
# Expone: class Lexer(text) con .tokenize_all() y .errors[]

import re
from collections import namedtuple

Token = namedtuple("Token", ["typ", "lexeme", "line", "col"])

class TokenType:
    def __init__(self, name): 
        self.name = name


# --------------------------------------------
# Clase principal Lexer
# --------------------------------------------
class Lexer:
    def __init__(self, source_text):
        self.source = source_text
        self.errors = []

        # Palabras reservadas típicas de Java
        self.reserved = {
            "class": "CLASS",
            "int": "INT",
            "float": "FLOAT",
            "char": "CHAR",
            "void": "VOID",
            "return": "RETURN",
            "if": "IF",
            "else": "ELSE",
            "while": "WHILE",
            "for": "FOR",
            "true": "TRUE",
            "false": "FALSE",
            "System": "SYSTEM",
            "out": "OUT",
            "println": "PRINTLN",
        }

        # Expresiones regulares para tokens
        self.token_exprs = [
            ("WS",        r"[ \t]+"),                        # espacios
            ("NEWLINE",   r"\n"),                            # salto de línea
            ("COMMENT1",  r"//[^\n]*"),                      # comentario //
            ("COMMENT2",  r"/\*[\s\S]*?\*/"),                # comentario /* ... */
            ("STRING",    r"\"(\\.|[^\"\\])*\""),            # literal de cadena
            ("NUM",       r"\d+"),                           # números
            ("ID",        r"[A-Za-z_][A-Za-z_0-9]*"),        # identificadores
            ("OP",        r"==|!=|<=|>=|\+\+|--|&&|\|\||[+\-*/=<>&|!]"),  # operadores
            ("SYMBOL",    r"[(){};,\.]"),                    # símbolos (incluye punto)
            ("ERROR",     r"."),                             # cualquier otro (error)
        ]

        # Expresión regular maestra con flags para evitar falsos espacios
        self.master = re.compile(
            "|".join(f"(?P<{name}>{expr})" for name, expr in self.token_exprs),
            re.MULTILINE | re.DOTALL
        )

    # ----------------------------------------
    # Mapeo de tipos de tokens a los nombres esperados por grammar.py
    # ----------------------------------------
    def map_token_name(self, kind, lex):
        """Convierte los tipos del lexer a los usados en grammar.TOK_TO_TERM."""
        if kind == "SYMBOL":
            return {
                "{": "LBRACE", 
                "}": "RBRACE", 
                "(": "LPAR", 
                ")": "RPAR",
                ",": "COMMA", 
                ";": "SEMI"
            }.get(lex, "SYMBOL")

        if kind == "OP":
            return {
                "=": "ASSIGN", 
                "+": "PLUS", 
                "-": "MINUS", 
                "*": "MUL", 
                "/": "DIV",
                "<": "LT", 
                ">": "GT", 
                "==": "EQEQ"
            }.get(lex, "OP")

        return kind

    # ----------------------------------------
    # Tokenización completa
    # ----------------------------------------
    def tokenize_all(self):
        tokens = []
        line, col = 1, 1
        for match in self.master.finditer(self.source):
            kind = match.lastgroup
            lex = match.group()

            # Ignorar espacios y comentarios
            if kind in ("WS", "COMMENT1", "COMMENT2"):
                col += len(lex)
                continue

            if kind == "NEWLINE":
                line += 1
                col = 1
                continue

            if kind == "ID":
                kind = self.reserved.get(lex, "ID")

            if kind == "ERROR":
                self.errors.append(f"Símbolo no reconocido '{lex}' (L{line}, C{col})")

            # Mapear nombres a los que espera grammar.py
            mapped_kind = self.map_token_name(kind, lex)
            tokens.append(Token(TokenType(mapped_kind), lex, line, col))
            col += len(lex)

        # Token EOF final
        tokens.append(Token(TokenType("EOF"), "", line, col))
        return tokens


# --------------------------------------------
# Helper público compatible con app.py
# --------------------------------------------
class PTok:
    __slots__ = ("kind", "lex", "line", "col")

    def __init__(self, kind, lex, line, col):
        self.kind = kind
        self.lex = lex
        self.line = line
        self.col = col


def tokenize(source_text):
    """Función auxiliar para compatibilidad con app.py"""
    from grammar import TOK_TO_TERM  # mapeo EnumName -> terminal (string)
    L = Lexer(source_text)
    raw = L.tokenize_all()
    out = []
    errs = list(L.errors)

    for t in raw:
        name = t.typ.name
        if name == "EOF":
            out.append(PTok("$", "", t.line, t.col))
            break
        if name == "ERROR":
            continue
        term = TOK_TO_TERM.get(name)
        if term is None:
            errs.append(f"Token '{name}' no mapeado en la gramática (L{t.line}, C{t.col})")
            continue
        out.append(PTok(term, t.lexeme, t.line, t.col))

    if not out or out[-1].kind != "$":
        out.append(PTok("$", "", raw[-1].line if raw else 1, raw[-1].col if raw else 1))

    return out, errs
