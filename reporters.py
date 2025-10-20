import os

OUT = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(OUT, exist_ok=True)

def write_errors(errors):
    path = os.path.join(OUT, 'errores.txt')
    with open(path,'w',encoding='utf-8') as f:
        for e in errors:
            f.write(e+'\n')

def write_table(table, conflicts):
    path = os.path.join(OUT, 'tabla_transicion.txt')
    with open(path,'w',encoding='utf-8') as f:
        for A, row in table.items():
            for a, prod in row.items():
                f.write(f"M[{A}, {a}] = {' '.join(prod) if prod else 'ε'}\n")
        if conflicts:
            f.write("\n# Conflictos:\n")
            for c in conflicts:
                A,a,p1,p2 = c
                f.write(f"Conflicto en ({A},{a}) entre {p1} y {p2}\n")
    return path

def write_dot(filename, content):
    path = os.path.join(OUT, filename)
    with open(path,'w',encoding='utf-8') as f: f.write(content)
    return path
