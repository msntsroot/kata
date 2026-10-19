"""Regras do jogo, como funções puras de datas: desafio do dia, ofensiva, XP, títulos e conquistas."""
import os
from datetime import date, timedelta

MAX_CONGELAMENTOS = 2
DIAS_POR_CONGELAMENTO = 7
TITULOS = ["Aprendiz", "Curioso", "Explorador", "Artesão", "Construtor",
           "Engenheiro", "Estrategista", "Arquiteto", "Sábio", "Mestre"]


def hoje():
    """KATA_HOJE=2026-10-19 simula outra data (testes e conferência manual)."""
    return date.fromisoformat(os.environ["KATA_HOJE"]) if os.environ.get("KATA_HOJE") else date.today()


def desafio_do_dia(resolvidos, total, dia):
    """(id, status): status é 'pendente', 'feito' (já resolveu hoje) ou 'fim' (acabaram os desafios).

    Um dia perdido não pula conteúdo: o desafio do dia é sempre o próximo não resolvido.
    """
    for id_, d in resolvidos.items():
        if d == dia:
            return id_, "feito"
    for id_ in range(1, total + 1):
        if id_ not in resolvidos:
            return id_, "pendente"
    return None, "fim"


def ofensiva(dias, dia):
    """Simula os dias, do primeiro resolvido até hoje.

    Devolve {atual, recorde, congelamentos, congelados}: a cada 7 dias seguidos ganha
    1 congelamento (máx. 2), gasto sozinho num dia perdido. Hoje ainda pendente não quebra nada.
    """
    dias = set(dias)
    estado = {"atual": 0, "recorde": 0, "congelamentos": 0, "congelados": set()}
    if not dias:
        return estado
    d = min(dias)
    seguidos = 0  # dias resolvidos desde o último congelamento ganho
    while d <= dia:
        if d in dias:
            estado["atual"] += 1
            seguidos += 1
            if seguidos == DIAS_POR_CONGELAMENTO:
                seguidos = 0
                estado["congelamentos"] = min(estado["congelamentos"] + 1, MAX_CONGELAMENTOS)
        elif d < dia:
            if estado["congelamentos"] > 0:
                estado["congelamentos"] -= 1
                estado["congelados"].add(d)
            else:
                estado["atual"] = 0
                seguidos = 0
        estado["recorde"] = max(estado["recorde"], estado["atual"])
        d += timedelta(days=1)
    return estado


def xp(nivel, falhas, dicas):
    """Base 10 por nível, +5/nível passando de primeira, +5/nível sem dica, −3/nível por dica."""
    total = 10 * nivel
    if falhas == 0:
        total += 5 * nivel
    if dicas == 0:
        total += 5 * nivel
    total -= 3 * nivel * dicas
    return max(total, nivel)


def titulo(resolvidos):
    return TITULOS[min(resolvidos // 10, len(TITULOS) - 1)]


def nivel_jogador(xp_total):
    """Nível n exige 50·n·(n−1) de XP: 0, 100, 300, 600, 1000…"""
    n = 1
    while 50 * (n + 1) * n <= xp_total:
        n += 1
    return n


def conquistas(historico, recorde):
    """historico: [(id, data, tentativas, dicas)]. Devolve [(emoji, nome, conseguiu)]."""
    sem_dica = sum(1 for *_, k in historico if k == 0)
    de_primeira = sum(1 for _, _, t, _ in historico if t == 1)
    chefes = sum(1 for i, _, _, k in historico if i % 10 == 0 and k == 0)
    return [
        ("🌱", "primeiro passo", len(historico) >= 1),
        ("🔥", "7 dias seguidos", recorde >= 7),
        ("☄️", "30 dias seguidos", recorde >= 30),
        ("🌋", "100 dias seguidos", recorde >= 100),
        ("🧠", "10 sem dica", sem_dica >= 10),
        ("🎯", "10 de primeira", de_primeira >= 10),
        ("👑", "chefão sem dica", chefes >= 1),
        ("🏔️", "os 100", len(historico) >= 100),
    ]
