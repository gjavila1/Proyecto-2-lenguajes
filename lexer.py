# === Helper público compatible con app.py ===
# Devuelve (tokens_para_parser, errores)
# tokens_para_parser = objetos simples con: kind (terminal string o '$'), lex (lexema), line, col
class PTok:
    __slots__ = ("kind","lex","line","col")
    def __init__(self, kind, lex, line, col):
        self.kind = kind
        self.lex = lex
        self.line = line
        self.col = col

def tokenize(source_text):
    from grammar import TOK_TO_TERM  # mapeo EnumName -> terminal (string)
    L = Lexer(source_text)
    raw = L.tokenize_all()           # lista de Token(typ, lexeme, line, col)
    out = []
    errs = list(L.errors)            # errores acumulados en el lexer (comentario no cerrado, char ilegal, etc.)

    for t in raw:
        name = t.typ.name            # ej: 'CLASS', 'ID', 'NUM', 'EOF', 'ERROR'
        if name == "EOF":
            out.append(PTok("$", "", t.line, t.col))
            break
        if name == "ERROR":
            # Ya agregamos un mensaje en errs; seguimos para no cortar el flujo
            continue
        term = TOK_TO_TERM.get(name)
        if term is None:
            # Si aparece algo no mapeado, lo reportamos y seguimos
            errs.append(f"Token '{name}' no mapeado en la gramática (L{t.line}, C{t.col})")
            continue
        out.append(PTok(term, t.lexeme, t.line, t.col))

    if not out or out[-1].kind != "$":
        # Garantiza token de fin
        out.append(PTok("$","", raw[-1].line if raw else 1, raw[-1].col if raw else 1))

    return out, errs
