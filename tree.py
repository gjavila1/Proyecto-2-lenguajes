from dataclasses import dataclass, field
from typing import List

@dataclass
class Node:
    label: str
    children: List['Node'] = field(default_factory=list)

    def add(self, *kids): 
        self.children.extend(kids); 
        return self

    def to_mermaid(self):
        lines = ["graph TD"]
        def walk(n, name_iter=['A']):
            my = name_iter[0]
            lines.append(f'{my}["{n.label}"]')
            for i, c in enumerate(n.children):
                nxt = my + chr(ord('A')+i)
                lines.append(f"{my}-->{nxt}")
                name_iter[0] = nxt
                walk(c, name_iter)
        walk(self, ['A'])
        return "\n".join(lines)

    def to_dot(self):
        out = ["digraph G { node [shape=box];"]
        counter = [0]
        def visit(n):
            i = counter[0]; counter[0]+=1
            out.append(f'n{i} [label="{n.label}"];')
            my = i
            for c in n.children:
                j = visit(c)
                out.append(f'n{my} -> n{j};')
            return my
        visit(self)
        out.append("}")
        return "\n".join(out)
