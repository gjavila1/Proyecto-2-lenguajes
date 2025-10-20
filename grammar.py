# Gramática LL(1) factorizada (símbolos como strings)
# No-terminales en MAYÚSCULAS con camel (por conveniencia)
NONTERMS = [
    'Prog','ClassDecl','MemberList','Member','VarDecl','MethodDecl',
    'ParamList','ParamRest','Param','Block','StmtList','Stmt','Assign',
    'Return','Call','ArgList','ArgRest','Expr','ExprP','Term','TermP','Factor','Type'
]

TERMS = [
    'class','id','number','{','}','(',')',',',';','=','return',
    '+','-','*','/','int','void','<','>','=='
]

START = 'Prog'

# Producciones (lado izquierdo -> lista de alternativas; ε como [])
G = {
    'Prog'      : [['ClassDecl']],
    'ClassDecl' : [['class','id','{','MemberList','}']],
    'MemberList': [['Member','MemberList'], []],
    'Member'    : [['MethodDecl'], ['VarDecl']],
    'VarDecl'   : [['Type','id',';']],
    'MethodDecl': [['Type','id','(','ParamList',')','Block']],
    'ParamList' : [['Param','ParamRest'], []],
    'ParamRest' : [[',','Param','ParamRest'], []],
    'Param'     : [['Type','id']],
    'Block'     : [['{','StmtList','}']],
    'StmtList'  : [['Stmt','StmtList'], []],
    'Stmt'      : [['VarDecl'], ['Assign'], ['Return'], ['Call',';']],
    'Assign'    : [['id','=','Expr',';']],
    'Return'    : [['return','Expr',';']],
    'Call'      : [['id','(','ArgList',')']],
    'ArgList'   : [['Expr','ArgRest'], []],
    'ArgRest'   : [[',','Expr','ArgRest'], []],
    'Expr'      : [['Term','ExprP']],
    'ExprP'     : [['+','Term','ExprP'], ['-','Term','ExprP'], []],
    'Term'      : [['Factor','TermP']],
    'TermP'     : [['*','Factor','TermP'], ['/','Factor','TermP'], []],
    'Factor'    : [['id'], ['number'], ['(','Expr',')']],
    'Type'      : [['int'], ['void']],
}

# Mapeo tokens->terminales
TOK_TO_TERM = {
    'CLASS':'class','ID':'id','NUM':'number','LBRACE':'{','RBRACE':'}','LPAR':'(','RPAR':')',
    'COMMA':',','SEMI':';','ASSIGN':'=','RETURN':'return','PLUS':'+','MINUS':'-','MUL':'*',
    'DIV':'/','INT':'int','VOID':'void','LT':'<','GT':'>','EQEQ':'=='
}
