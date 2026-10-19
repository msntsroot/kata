"""Os dois bancos: desafios.db (gerado pelo build, só leitura) e progresso.db (do usuário)."""
import json
import os
import sqlite3
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESAFIOS = os.environ.get("KATA_DESAFIOS", os.path.join(RAIZ, "data", "desafios.db"))
DADOS = os.environ.get("KATA_DADOS", os.path.join(
    os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")), "kata"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS resolucoes (
    desafio_id INTEGER PRIMARY KEY, data TEXT, xp INTEGER, tentativas INTEGER,
    dicas INTEGER, codigo TEXT, nota TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS estado (
    desafio_id INTEGER PRIMARY KEY, tentativas INTEGER DEFAULT 0,
    dicas INTEGER DEFAULT 0, rascunho TEXT
);
CREATE TABLE IF NOT EXISTS config (chave TEXT PRIMARY KEY, valor TEXT);
"""


class Desafios:
    def __init__(self, caminho=DESAFIOS):
        self.con = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
        self.con.row_factory = sqlite3.Row

    def total(self):
        return self.con.execute("SELECT COUNT(*) FROM desafios").fetchone()[0]

    def get(self, id_):
        r = self.con.execute("SELECT * FROM desafios WHERE id = ?", (id_,)).fetchone()
        if r is None:
            return None
        d = dict(r)
        for k in ("tags", "usa", "dicas", "referencias", "criterios"):
            d[k] = json.loads(d[k])
        return d

    def casos(self, id_):
        rs = self.con.execute(
            "SELECT visivel, entrada, esperado, hash FROM casos WHERE desafio_id = ? ORDER BY ordem", (id_,))
        return [{"visivel": bool(v), "entrada": json.loads(e), "esperado": esp, "hash": h} for v, e, esp, h in rs]

    def niveis(self):
        return dict(self.con.execute("SELECT id, nivel FROM desafios"))


class Progresso:
    def __init__(self, pasta=DADOS):
        os.makedirs(pasta, exist_ok=True)
        self.con = sqlite3.connect(os.path.join(pasta, "progresso.db"))
        self.con.executescript(SCHEMA)

    # resoluções do modo diário: {desafio_id: date}
    def resolvidos(self):
        return {i: date.fromisoformat(d) for i, d in self.con.execute("SELECT desafio_id, data FROM resolucoes")}

    def resolucao(self, id_):
        r = self.con.execute(
            "SELECT data, xp, tentativas, dicas, codigo, nota FROM resolucoes WHERE desafio_id = ?", (id_,)).fetchone()
        return None if r is None else dict(zip(("data", "xp", "tentativas", "dicas", "codigo", "nota"), r))

    def resolver(self, id_, dia, xp, tentativas, dicas, codigo):
        with self.con:
            self.con.execute("INSERT OR IGNORE INTO resolucoes VALUES (?,?,?,?,?,?,'')",
                             (id_, dia.isoformat(), xp, tentativas, dicas, codigo))

    def anotar(self, id_, nota):
        with self.con:
            self.con.execute("UPDATE resolucoes SET nota = ? WHERE desafio_id = ?", (nota, id_))

    def xp_total(self):
        return self.con.execute("SELECT COALESCE(SUM(xp), 0) FROM resolucoes").fetchone()[0]

    def historico(self):
        """[(desafio_id, data, tentativas, dicas)] em ordem."""
        return [(i, date.fromisoformat(d), t, k) for i, d, t, k in self.con.execute(
            "SELECT desafio_id, data, tentativas, dicas FROM resolucoes ORDER BY desafio_id")]

    def estado(self, id_):
        r = self.con.execute("SELECT tentativas, dicas, rascunho FROM estado WHERE desafio_id = ?", (id_,)).fetchone()
        return {"tentativas": 0, "dicas": 0, "rascunho": None} if r is None else \
            {"tentativas": r[0], "dicas": r[1], "rascunho": r[2]}

    def _upsert(self, id_, campo, valor_sql, params=()):
        with self.con:
            self.con.execute("INSERT OR IGNORE INTO estado (desafio_id) VALUES (?)", (id_,))
            self.con.execute(f"UPDATE estado SET {campo} = {valor_sql} WHERE desafio_id = ?", (*params, id_))

    def tentou(self, id_):
        self._upsert(id_, "tentativas", "tentativas + 1")

    def pediu_dica(self, id_):
        self._upsert(id_, "dicas", "MIN(dicas + 1, 3)")

    def salvar_rascunho(self, id_, codigo):
        self._upsert(id_, "rascunho", "?", (codigo,))

    def config(self, chave, padrao=None):
        r = self.con.execute("SELECT valor FROM config WHERE chave = ?", (chave,)).fetchone()
        return padrao if r is None else json.loads(r[0])

    def set_config(self, chave, valor):
        with self.con:
            self.con.execute("INSERT OR REPLACE INTO config VALUES (?, ?)", (chave, json.dumps(valor)))
