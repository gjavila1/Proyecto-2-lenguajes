# app.py
from flask import Flask, render_template, request, send_file, abort
import os
from datetime import datetime

import lexer
import grammar
import ll1
import parser_ll1
from tree import Node  # usamos parse_tree.to_dot()

app = Flask(__name__)

DEMO = """class Demo {
  int x;
  int y;

  int suma(int a, int b) {
    return a + b;
  }

  void main() {
    x = 2 + 3 * (4 + 5);
    y = suma(x, 10);
    return;
  }
}"""

# ---------------- utilidades ----------------
def safe_str(x, fallback=""):
    try:
        return str(x) if x is not None else fallback
    except Exception:
        return fallback

def ensure_out_dir():
    os.makedirs("out", exist_ok=True)

def write_text(path, content):
    ensure_out_dir()
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def write_lines(path, lines):
    ensure_out_dir()
    with open(path, "w", encoding="utf-8") as f:
        for line in (lines or []):
            f.write(safe_str(line) + "\n")

def load_programa_txt(default_text):
    try:
        with open("programa.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return default_text

# -------- wrapper de lexer: produce PTok(kind,lex,line,col) + errores --------
class PTok:
    __slots__ = ("kind","lex","line","col")
    def __init__(self, kind, lex, line, col):
        self.kind = kind
        self.lex = lex
        self.line = line
        self.col = col

def lex_tokenize(source_text):
    from grammar import TOK_TO_TERM
    L = lexer.Lexer(source_text)
    raw = L.tokenize_all()     # lista de Token(typ, lexeme, line, col)
    errs = list(L.errors)
    out = []
    for t in raw:
        name = t.typ.name      # 'CLASS','ID','NUM','EOF','ERROR',...
        if name == "EOF":
            out.append(PTok("$", "", t.line, t.col))
            break
        if name == "ERROR":
            # ya agregaste el mensaje en errs desde el lexer; seguimos
            continue
        term = TOK_TO_TERM.get(name)
        if term is None:
            errs.append(f"Token '{name}' no mapeado en la gramática (L{t.line}, C{t.col})")
            continue
        out.append(PTok(term, t.lexeme, t.line, t.col))
    if not out or out[-1].kind != "$":
        last = raw[-1] if raw else type("X", (), {"line":1,"col":1})()
        out.append(PTok("$","", last.line, last.col))
    return out, errs

# ---------------- análisis ----------------
def analyze(source: str):
    result = {
        "console": "",
        "errores": [],
        "conflictos": [],
        "arbol_dot": "",
        "ast_dot": "",
        "tabla_transicion": []
    }

    if not isinstance(source, str):
        source = safe_str(source)

    log = []
    try:
        # Gramática
        start = grammar.START
        G = grammar.G
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Gramática cargada. Símbolo inicial: {start}")

        # Lexer (wrapper)
        tokens, lex_errors = lex_tokenize(source)
        log.append(f"Tokens generados: {len(tokens)}")
        if lex_errors:
            log.append(f"Errores léxicos: {len(lex_errors)}")

        # FIRST/FOLLOW + Tabla LL(1)
        FIRST, FOLLOW = ll1.build_first_follow()
        table, conflicts = ll1.build_table(FIRST, FOLLOW)
        result["conflictos"] = conflicts or []
        log.append("Tabla LL(1) sin conflictos." if not conflicts else f"⚠️ Conflictos LL(1): {len(conflicts)}")

        # Serializar tabla
        rows = []
        for A in table:
            for a in table[A]:
                prod = table[A][a]
                rows.append(f"{A:12} | {a:10} -> {' '.join(prod) if prod else 'ε'}")
        result["tabla_transicion"] = sorted(rows)

        # Parser
        parse_tree, syn_errors = parser_ll1.parse(tokens, G, table)

        # Árbol DOT
        try:
            result["arbol_dot"] = parse_tree.to_dot() if parse_tree else "digraph G { node [shape=box]; Empty; }"
        except Exception as e:
            result["arbol_dot"] = f"digraph G {{ node [shape=box]; Error[label=\"DOT error: {safe_str(e)}\"]; }}"

        # (AST opcional no implementado)
        result["ast_dot"] = ""

        # Errores
        result["errores"].extend(lex_errors or [])
        result["errores"].extend(syn_errors or [])

        log.append(f"Líneas procesadas: {source.count('\\n')+1}")

        if conflicts:
            for (A,a,p1,p2) in conflicts:
                log.append(f"[Conflicto] ({A}, {a}) entre {p1} y {p2}")

    except Exception as e:
        result["errores"].append(f"Excepción interna: {type(e).__name__}: {e}")
        result["arbol_dot"] = "digraph G { node [shape=box]; Error; }"

    result["console"] = "\n".join(log)
    return result

# ---------------- rutas ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        codigo = load_programa_txt(DEMO)
        print("GET request - usando código demo")
    else:
        codigo = request.form.get("code", "")
        print("POST request - código recibido:", codigo[:100], "...")  # Primeros 100 chars

    # Debug de análisis
    print("Iniciando análisis...")
    res = analyze(codigo)
    
    # Debug del resultado
    print("Tokens:", len(res.get("tokens", [])))
    print("Errores:", len(res.get("errores", [])))
    print("Árbol generado:", bool(res.get("arbol_dot")))
    print("Tabla de transición:", len(res.get("tabla_transicion", [])))

    if request.method == "POST":
        write_lines("out/errores.txt", res.get("errores") or [])
        write_lines("out/tabla_transicion.txt", res.get("tabla_transicion") or [])
        write_text("out/arbol.dot", res.get("arbol_dot") or "")

    return render_template(
        "index.html",
        codigo=codigo,
        conflictos=res.get("conflictos") or [],
        errores=res.get("errores") or [],
        console=res.get("console") or "",
        arbol=res.get("arbol_dot") or "",
        ast=res.get("ast_dot") or "",
        tabla=res.get("tabla_transicion") or []
    )
@app.route("/download/errores")
def download_errores():
    path = "out/errores.txt"
    return send_file(path, as_attachment=True, download_name="errores.txt") if os.path.exists(path) else abort(404)

@app.route("/download/tabla")
def download_tabla():
    path = "out/tabla_transicion.txt"
    return send_file(path, as_attachment=True, download_name="tabla_transicion.txt") if os.path.exists(path) else abort(404)

@app.route("/download/arbol")
def download_arbol():
    path = "out/arbol.dot"
    return send_file(path, as_attachment=True, download_name="arbol.dot") if os.path.exists(path) else abort(404)

if __name__ == "__main__":
    app.run(debug=True)
