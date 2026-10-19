"""Lint do editor: ruff quando instalado, senão só a checagem de sintaxe do próprio Python."""
import json
import shutil
import subprocess

TRADUCOES = {
    "F821": "nome não definido",
    "F841": "variável criada e nunca usada",
    "F401": "import não usado",
    "E711": "compare com None usando `is`",
    "E712": "não compare com True/False, use a condição direto",
    "E721": "use isinstance() para checar tipo",
    "E741": "nome ambíguo (l, O, I)",
    "F811": "redefinição de nome já usado",
    "F632": "use == para comparar valores, não `is`",
}
SINTAXE = [
    ("expected ':'", "faltou o ':' no fim da linha"),
    ("expected an indented block", "faltou indentar o bloco"),
    ("unexpected indent", "indentação inesperada"),
    ("unindent does not match", "indentação desalinhada"),
    ("was never closed", "parêntese/colchete aberto e nunca fechado"),
    ("unterminated string", "string sem aspas de fechamento"),
    ("invalid syntax", "sintaxe inválida"),
    ("unmatched", "fechou algo que não foi aberto"),
]


def traduz_sintaxe(msg):
    for en, pt in SINTAXE:
        if en in msg:
            return pt
    return msg


def lint(codigo):
    """[(linha, coluna, codigo, mensagem)] ordenado por linha."""
    try:
        compile(codigo, "solucao.py", "exec")
    except SyntaxError as e:
        return [(e.lineno or 1, e.offset or 1, "sintaxe", traduz_sintaxe(e.msg))]
    if not shutil.which("ruff"):
        return []
    try:
        p = subprocess.run(
            ["ruff", "check", "--no-cache", "--isolated", "--select", "E4,E7,E9,F", "--output-format", "json",
             "--stdin-filename", "solucao.py", "-"],
            input=codigo, capture_output=True, text=True, timeout=5,
        )
        itens = json.loads(p.stdout or "[]")
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return []
    return sorted(
        (i["location"]["row"], i["location"]["column"], i["code"] or "",
         TRADUCOES.get(i["code"], i["message"]))
        for i in itens
    )
