# parser_ll1.py (reemplazo completo)
from tree import Node
import ll1
import grammar

def parse(tokens, G=None, table=None):
    """
    tokens: lista de PTok(kind, lex, line, col) (ver app.py)
    G: gramática dict (por defecto grammar.G)
    table: tabla LL(1) opcional (si no, se calcula aquí)
    return: (parse_tree_root, syn_errors)
    """
    G = G or grammar.G
    # Construir FIRST/FOLLOW y tabla si no la mandan
    FIRST, FOLLOW = ll1.build_first_follow()
    M, _conflicts = ll1.build_table(FIRST, FOLLOW)

    stack = [("$", None), (grammar.START, Node(grammar.START))]
    root = stack[-1][1]
    i = 0
    errors = []

    def curr():
        nonlocal i
        return tokens[i] if i < len(tokens) else tokens[-1]  # '$' garantizado

    while stack:
        X, node = stack.pop()
        a = curr()

        if X == "$":
            if a.kind == "$":
                break
            else:
                errors.append(f"Sintáctico L{a.line} C{a.col}: tokens extra al final '{a.lex}'")
                i += 1
                continue

        # Terminal
        if X not in G:
            if X == a.kind:
                node.label = X
                node.children = [Node(f"«{a.lex}»")] if a.lex else [Node(X)]
                i += 1
            else:
                msg = f"Sintáctico L{a.line} C{a.col}: se esperaba '{X}' antes de '{a.lex}'"
                if X == ";":
                    msg += " — sugerencia: inserta ';'"
                errors.append(msg)
            continue

        # No-terminal
        entry = M.get(X, {}).get(a.kind)
        if entry is None:
            errors.append(f"Sintáctico L{a.line} C{a.col}: no se puede derivar {X} con '{a.lex}'. Saltando hasta sincronizar.")
            sync = ll1.build_first_follow()[1].get(X, set())  # FOLLOW[X]
            while a.kind not in sync and a.kind != "$":
                i += 1
                a = curr()
            continue

        if entry and entry != ["ε"]:
            children = [Node(sym) for sym in entry]
            node.children = children
            for sym, child in reversed(list(zip(entry, children))):
                stack.append((sym, child))
        else:
            node.children = [Node("ε")]

    return root, errors
