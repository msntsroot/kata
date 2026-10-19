"""Compara o que o usuário retornou com os casos: visíveis pelo valor, ocultos pelo hash."""
from . import criterios, runner


def avaliar(desafio, casos, codigo):
    """Devolve {aprovado, erros_criterio, carga, tempo_esgotado, casos: [...]}.

    Cada caso: {visivel, entrada, esperado (só visível), obtido, erro, print, ok}.
    O esperado de um caso oculto nunca sai daqui: só se sabe se bateu ou não.
    """
    crit = desafio["criterios"]
    erros = criterios.checar(codigo, crit)
    if erros:
        return {"aprovado": False, "erros_criterio": erros, "carga": None, "tempo_esgotado": False, "casos": []}
    res = runner.executar(codigo, [c["entrada"] for c in casos], crit.get("tempo", runner.TEMPO))
    saida = []
    for caso, r in zip(casos, res["casos"]):
        ok = r["erro"] is None and runner.hash_saida(desafio["slug"], r["saida"]) == caso["hash"]
        saida.append({
            "visivel": caso["visivel"], "entrada": caso["entrada"],
            "esperado": caso["esperado"] if caso["visivel"] else None,
            "obtido": r["saida"], "erro": r["erro"], "print": r["print"], "ok": ok,
        })
    aprovado = not res["carga"] and not res["tempo_esgotado"] and len(saida) == len(casos) and all(c["ok"] for c in saida)
    return {"aprovado": aprovado, "erros_criterio": [], "carga": res["carga"],
            "tempo_esgotado": res["tempo_esgotado"], "casos": saida}
