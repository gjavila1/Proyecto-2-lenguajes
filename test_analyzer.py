from lexer import Lexer

code = """class Demo {
  int x;
  int suma(int a, int b) {
    return a + b;
  }
}"""

L = Lexer(code)
tokens = L.tokenize_all()
for t in tokens:
    print(f"{t.typ.name:10}  {t.lexeme!r}  (L{t.line}, C{t.col})")

print("Errores:", L.errors)