#!/usr/bin/env python3
"""Valida os desafios de autoria/desafios/ e gera data/desafios.db.

Uso: build.py [--so N]   (--so valida só o desafio N, sem gravar o banco)

As soluções de referência rodam no mesmo sandbox do app. Para os casos ocultos,
o banco guarda só a entrada e o hash da saída esperada. O gabarito não sai daqui.
"""
import importlib.util
import json
import os
import random
import re
import sqlite3
import sys
import tomllib

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from kata import criterios, runner  # noqa: E402

DESAFIOS = os.path.join(RAIZ, "autoria", "desafios")
BANCO = os.path.join(RAIZ, "data", "desafios.db")
OBRIGATORIOS = {"id", "slug", "titulo", "arco", "nivel", "assinatura", "enunciado", "exemplos", "dicas", "conceito"}
SCHEMA = """
CREATE TABLE meta (chave TEXT PRIMARY KEY, valor TEXT);
CREATE TABLE desafios (
    id INTEGER PRIMARY KEY, slug TEXT UNIQUE, titulo TEXT, arco INTEGER, nivel INTEGER,
    tags TEXT, usa TEXT, assinatura TEXT, esqueleto TEXT, enunciado TEXT,
    dicas TEXT, referencias TEXT, conceito TEXT, criterios TEXT
);
CREATE TABLE casos (
    desafio_id INTEGER, ordem INTEGER, visivel INTEGER,
    entrada TEXT, esperado TEXT, hash TEXT,
    PRIMARY KEY (desafio_id, ordem)
);
"""


class Erro(Exception):
    pass


def carregar(pasta):
    with open(os.path.join(pasta, "desafio.toml"), "rb") as f:
        d = tomllib.load(f)
    faltam = OBRIGATORIOS - d.keys()
    if faltam:
        raise Erro(f"campos faltando: {', '.join(sorted(faltam))}")
    nome = os.path.basename(pasta)
    if nome != f"{d['id']:03d}-{d['slug']}":
        raise Erro(f"a pasta devia se chamar {d['id']:03d}-{d['slug']}")
    if not re.fullmatch(r"def resolver\(.*\)( -> .+)?", d["assinatura"]):
        raise Erro("assinatura deve ser 'def resolver(...)' sem ':' no fim")
    if not 1 <= d["nivel"] <= 10 or not 1 <= d["arco"] <= 10:
        raise Erro("nivel e arco vão de 1 a 10")
    if len(d["dicas"]) != 3:
        raise Erro("são exatamente 3 dicas, da mais leve à mais direta")
    if any(u >= d["id"] for u in d.get("usa", [])):
        raise Erro("'usa' só pode apontar para desafios anteriores")
    with open(os.path.join(pasta, "solucao.py")) as f:
        d["_solucao"] = f.read()
    entradas = [e["entrada"] for e in d["exemplos"]]
    ocultos = list(d.get("testes", []))
    gerador = os.path.join(pasta, "gerador.py")
    if os.path.exists(gerador):
        spec = importlib.util.spec_from_file_location(f"gerador_{d['id']}", gerador)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        ocultos += mod.gerar(random.Random(d["id"]))
    if len(ocultos) < 5:
        raise Erro("pelo menos 5 casos ocultos (testes ou gerador.py)")
    if any(not isinstance(e, list) for e in entradas + ocultos):
        raise Erro("cada entrada é a lista de argumentos de resolver, ex.: [3] ou [[1, 2], 5]")
    d["_entradas"] = entradas
    d["_ocultos"] = ocultos
    return d


def validar(d):
    crit = d.get("criterios", {})
    todas = d["_entradas"] + d["_ocultos"]
    if (msgs := criterios.checar(d["_solucao"], crit)):
        raise Erro(f"a solução de referência quebra os próprios critérios: {msgs}")
    tempo = crit.get("tempo", runner.TEMPO)
    res = [runner.executar(d["_solucao"], todas, tempo) for _ in range(2)]
    for r in res:
        if r["carga"] or r["tempo_esgotado"]:
            raise Erro(f"a solução de referência não rodou: {r['carga'] or 'tempo esgotado'}")
        for i, c in enumerate(r["casos"]):
            if c["erro"]:
                raise Erro(f"a solução de referência quebrou na entrada {todas[i]}: {c['erro']}")
    saidas = [c["saida"] for c in res[0]["casos"]]
    if saidas != [c["saida"] for c in res[1]["casos"]]:
        raise Erro("saída não determinística")
    for ex, s in zip(d["exemplos"], saidas):
        if "saida" in ex and json.loads(s) != runner_normal(ex["saida"]):
            raise Erro(f"exemplo {ex['entrada']}: o toml diz {ex['saida']!r}, a solução dá {s}")
    esqueleto = esqueleto_de(d)
    r = runner.executar(esqueleto, todas, tempo)
    if all(not c["erro"] and c["saida"] == s for c, s in zip(r["casos"], saidas)) and len(r["casos"]) == len(todas):
        raise Erro("o esqueleto vazio já passa em todos os casos")
    if len(set(saidas[len(d["_entradas"]):])) < 2:
        raise Erro("os casos ocultos têm todos a mesma resposta: dá pra chutar")
    return saidas


def runner_normal(v):
    spec = importlib.util.spec_from_file_location("h", runner.HARNESS)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    return json.loads(h.canonico(v))


def esqueleto_de(d):
    return f"{d['assinatura']}:\n    pass\n"


def pastas():
    return sorted(os.path.join(DESAFIOS, p) for p in os.listdir(DESAFIOS)
                  if os.path.isfile(os.path.join(DESAFIOS, p, "desafio.toml")))


def main():
    so = int(sys.argv[sys.argv.index("--so") + 1]) if "--so" in sys.argv else None
    validados, falhas = [], 0
    for pasta in pastas():
        nome = os.path.basename(pasta)
        if so is not None and not nome.startswith(f"{so:03d}-"):
            continue
        try:
            d = carregar(pasta)
            saidas = validar(d)
            validados.append((d, saidas))
            print(f"  ok  {nome}  ({len(d['_ocultos'])} ocultos)")
        except Erro as e:
            falhas += 1
            print(f"FALHA {nome}: {e}")
    ids = [d["id"] for d, _ in validados]
    if so is None:
        if ids != list(range(1, len(ids) + 1)):
            falhas += 1
            print(f"FALHA: ids precisam ser 1..N sem buracos (tenho {ids})")
    if falhas:
        sys.exit(f"\n{falhas} falha(s): banco não gravado")
    if so is not None:
        return
    gravar(validados)
    print(f"\n{len(validados)} desafios → {BANCO}")


def gravar(validados):
    tmp = BANCO + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    con = sqlite3.connect(tmp)
    con.executescript(SCHEMA)
    con.execute("INSERT INTO meta VALUES ('versao', '1')")
    for d, saidas in validados:
        con.execute(
            "INSERT INTO desafios VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (d["id"], d["slug"], d["titulo"], d["arco"], d["nivel"],
             json.dumps(d.get("tags", [])), json.dumps(d.get("usa", [])),
             d["assinatura"], esqueleto_de(d), d["enunciado"].strip(),
             json.dumps(d["dicas"], ensure_ascii=False),
             json.dumps(d.get("referencias", []), ensure_ascii=False),
             re.sub(r"(?<!\n)\n(?!\n)", " ", d["conceito"].strip()), json.dumps(d.get("criterios", {}))),
        )
        n_vis = len(d["_entradas"])
        for i, (entrada, s) in enumerate(zip(d["_entradas"] + d["_ocultos"], saidas)):
            vis = i < n_vis
            con.execute("INSERT INTO casos VALUES (?,?,?,?,?,?)",
                        (d["id"], i, int(vis), json.dumps(entrada), s if vis else None,
                         runner.hash_saida(d["slug"], s)))
    con.commit()
    con.close()
    os.replace(tmp, BANCO)


if __name__ == "__main__":
    main()
