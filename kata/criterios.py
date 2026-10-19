"""Critérios checados no código-fonte (AST), antes de rodar: nomes proibidos e recursão exigida."""
import ast


def checar(codigo, criterios):
    """Devolve uma lista de mensagens; vazia quando o código respeita os critérios."""
    try:
        arvore = ast.parse(codigo)
    except SyntaxError:
        return []  # o lint/execução já reportam o erro de sintaxe
    erros = []
    proibidos = set(criterios.get("proibido", []))
    if proibidos:
        usados = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.Name) and no.id in proibidos:
                usados.add(no.id)
            elif isinstance(no, ast.Attribute) and no.attr in proibidos:
                usados.add(no.attr)
            elif isinstance(no, (ast.Import, ast.ImportFrom)):
                for a in no.names:
                    if a.name.split(".")[0] in proibidos:
                        usados.add(a.name)
                if isinstance(no, ast.ImportFrom) and no.module and no.module.split(".")[0] in proibidos:
                    usados.add(no.module)
        for nome in sorted(usados):
            erros.append(f"hoje não vale usar {nome}")
    if criterios.get("recursivo"):
        if not _tem_recursao(arvore):
            erros.append("resolva com recursão: uma função que chama a si mesma")
    return erros


def _tem_recursao(arvore):
    for fn in ast.walk(arvore):
        if isinstance(fn, ast.FunctionDef):
            for no in ast.walk(fn):
                if isinstance(no, ast.Call) and isinstance(no.func, ast.Name) and no.func.id == fn.name:
                    return True
    return False
