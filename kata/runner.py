"""Executa o código do usuário num sandbox bubblewrap: sem rede, sem $HOME, com tempo e memória limitados."""
import hashlib
import json
import os
import shutil
import signal
import subprocess
import tempfile

HARNESS = os.path.join(os.path.dirname(__file__), "harness", "python.py")
TEMPO = 5          # segundos de relógio para todos os casos
MEMORIA = 512 << 20  # bytes de espaço de endereçamento


def hash_saida(slug, canon):
    return hashlib.sha256(f"{slug}:{canon}".encode()).hexdigest()


def _comando(pasta):
    return [
        "prlimit", f"--as={MEMORIA}", f"--cpu={TEMPO * 2}", "--fsize=1048576", "--",
        "bwrap",
        "--unshare-all", "--die-with-parent", "--new-session",
        "--ro-bind", "/usr", "/usr",
        "--symlink", "usr/lib", "/lib",
        "--symlink", "usr/lib", "/lib64",
        "--symlink", "usr/bin", "/bin",
        "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
        "--ro-bind", pasta, "/work", "--chdir", "/work",
        "--clearenv", "--setenv", "PATH", "/usr/bin", "--setenv", "PYTHONDONTWRITEBYTECODE", "1",
        "/usr/bin/python3", "-I", "/work/harness.py",
    ]


def executar(codigo, entradas, tempo=TEMPO):
    """Roda resolver() em cada entrada. Devolve {carga, casos, tempo_esgotado}.

    Cada caso: {saida: json canônico | None, erro: str | None, print: str}.
    """
    with tempfile.TemporaryDirectory(prefix="kata-") as pasta:
        with open(os.path.join(pasta, "solucao.py"), "w") as f:
            f.write(codigo)
        shutil.copy(HARNESS, os.path.join(pasta, "harness.py"))
        os.chmod(pasta, 0o755)
        proc = subprocess.Popen(
            _comando(pasta), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, start_new_session=True,
        )
        try:
            out, err = proc.communicate(json.dumps(entradas), timeout=tempo)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            out, err = proc.communicate()
            return {"carga": None, "casos": _parciais(err), "tempo_esgotado": True}

    try:
        res = json.loads(out.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        # morreu sem responder: memória, CPU ou algo pior
        motivo = "o programa foi encerrado"
        if "MemoryError" in err or proc.returncode in (-signal.SIGKILL, -signal.SIGSEGV):
            motivo = "memória esgotada"
        elif proc.returncode == -signal.SIGXCPU:
            motivo = "tempo de CPU esgotado"
        return {"carga": motivo, "casos": _parciais(err), "tempo_esgotado": False}
    res["tempo_esgotado"] = False
    return res


def _parciais(err):
    casos = []
    for linha in err.splitlines():
        try:
            casos.append(json.loads(linha))
        except json.JSONDecodeError:
            pass
    return casos
