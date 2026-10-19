"""Roda dentro do sandbox: importa solucao.py e chama resolver(*entrada) para cada caso.

Lê do stdin uma lista JSON de entradas (cada uma é a lista de argumentos) e
escreve no stdout um único JSON com o resultado de cada caso. Os print() do
usuário são capturados por caso e devolvidos à parte, para não sujar a saída.
"""
import contextlib
import copy
import io
import json
import math
import os
import sys
import traceback

LIMITE_PRINT = 2000


def normalizar(v):
    """Leva o retorno a uma forma JSON única: tupla vira lista, 2.0 vira 2, floats com 6 casas."""
    if isinstance(v, bool) or v is None or isinstance(v, (int, str)):
        return v
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            raise TypeError("retorno com nan/inf")
        v = round(v, 6)
        return int(v) if v.is_integer() else v
    if isinstance(v, (list, tuple)):
        return [normalizar(x) for x in v]
    if isinstance(v, dict):
        return {str(k): normalizar(x) for k, x in v.items()}
    raise TypeError(f"tipo de retorno não suportado: {type(v).__name__} (use int, float, str, bool, list, dict ou None)")


def canonico(v):
    return json.dumps(normalizar(v), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def traceback_curto():
    """Só os frames do código do usuário, sem o harness."""
    tipo, valor, tb = sys.exc_info()
    frames = [f for f in traceback.extract_tb(tb) if f.filename.endswith("solucao.py")]
    linhas = [f"linha {f.lineno}: {f.line}" for f in frames[-3:]]
    linhas.append(f"{tipo.__name__}: {valor}")
    return "\n".join(linhas)


def main():
    # -I não põe a pasta do script no path; o solucao.py está ao lado
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    entradas = json.loads(sys.stdin.read())
    saida = {"carga": None, "casos": []}
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            import solucao
        resolver = solucao.resolver
    except AttributeError:
        saida["carga"] = "defina uma função chamada resolver"
        print(json.dumps(saida))
        return
    except BaseException:
        saida["carga"] = traceback_curto()
        print(json.dumps(saida))
        return

    for args in entradas:
        buf = io.StringIO()
        caso = {"saida": None, "erro": None, "print": ""}
        try:
            with contextlib.redirect_stdout(buf):
                ret = resolver(*copy.deepcopy(args))
            caso["saida"] = canonico(ret)
        except RecursionError:
            caso["erro"] = "RecursionError: recursão sem fim (faltou o caso base?)"
        except BaseException:
            caso["erro"] = traceback_curto()
        caso["print"] = buf.getvalue()[:LIMITE_PRINT]
        saida["casos"].append(caso)
        # flush parcial: se estourar o tempo, o runner ainda vê os casos já rodados
        sys.stderr.write(json.dumps(caso) + "\n")
        sys.stderr.flush()

    print(json.dumps(saida))


if __name__ == "__main__":
    main()
