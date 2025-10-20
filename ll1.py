from grammar import G, NONTERMS, TERMS, START
from collections import defaultdict

EPS = 'ε'
END = '$'

def first_of_seq(seq, FIRST):
    s = set()
    if not seq:
        s.add(EPS); return s
    for X in seq:
        s |= (FIRST[X] - {EPS})
        if EPS not in FIRST[X]:
            break
    else:
        s.add(EPS)
    return s

def build_first_follow():
    FIRST = {A:set() for A in (NONTERMS+TERMS+[EPS])}
    FOLLOW = {A:set() for A in NONTERMS}
    # FIRST terminal = t
    for t in TERMS: FIRST[t].add(t)
    FIRST[EPS].add(EPS)
    changed = True
    while changed:
        changed = False
        for A, prods in G.items():
            for alpha in prods:
                if not alpha:
                    if EPS not in FIRST[A]:
                        FIRST[A].add(EPS); changed=True
                    continue
                f = first_of_seq(alpha, FIRST)
                n = len(FIRST[A])
                FIRST[A] |= f
                if len(FIRST[A]) != n: changed = True
    FOLLOW[START].add(END)
    changed = True
    while changed:
        changed=False
        for A, prods in G.items():
            for alpha in prods:
                trailer = set(FOLLOW[A])
                for X in reversed(alpha):
                    if X in NONTERMS:
                        n = len(FOLLOW[X])
                        FOLLOW[X] |= trailer
                        if 'ε' in FIRST[X]:  # no se usa, pero mantener por simetría
                            pass
                        if EPS in FIRST[X]:
                            trailer |= (FIRST[X]-{EPS})
                        else:
                            trailer = (FIRST[X]-{EPS})
                        if len(FOLLOW[X])!=n: changed=True
                    else:
                        trailer = (FIRST[X]-{EPS})
    return FIRST, FOLLOW

def build_table(FIRST, FOLLOW):
    M = defaultdict(dict)
    conflicts = []
    for A, prods in G.items():
        for i, alpha in enumerate(prods):
            f = first_of_seq(alpha, FIRST)
            for a in (f - {EPS}):
                if a in M[A] and M[A][a] != alpha:
                    conflicts.append((A, a, M[A][a], alpha))
                M[A][a] = alpha
            if EPS in f:
                for b in FOLLOW[A]:
                    if b in M[A] and M[A][b] != alpha:
                        conflicts.append((A, b, M[A][b], alpha))
                    M[A][b] = alpha
    return M, conflicts
