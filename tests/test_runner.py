import json
import os
import unittest

from kata import criterios, runner


class Sandbox(unittest.TestCase):
    def test_retorno_e_print(self):
        r = runner.executar("def resolver(a, b):\n    print('oi')\n    return a + b\n", [[1, 2], [2.5, 0.5]])
        self.assertEqual([c["saida"] for c in r["casos"]], ["3", "3"])
        self.assertEqual(r["casos"][0]["print"], "oi\n")

    def test_canonico(self):
        r = runner.executar("def resolver(x):\n    return x\n", [[(1, 2)], [{"b": 1, "a": 0.1 + 0.2}], [True]])
        self.assertEqual([c["saida"] for c in r["casos"]], ["[1,2]", '{"a":0.3,"b":1}', "true"])

    def test_erro_por_caso(self):
        r = runner.executar("def resolver(x):\n    return 10 // x\n", [[0], [5]])
        self.assertIn("ZeroDivisionError", r["casos"][0]["erro"])
        self.assertEqual(r["casos"][1]["saida"], "2")

    def test_sem_resolver(self):
        self.assertIn("resolver", runner.executar("x = 1\n", [[1]])["carga"])

    def test_sintaxe(self):
        self.assertIn("SyntaxError", runner.executar("def resolver(:\n", [[1]])["carga"])

    def test_tempo(self):
        r = runner.executar("def resolver(x):\n    while True:\n        pass\n", [[1]], tempo=1)
        self.assertTrue(r["tempo_esgotado"])

    def test_memoria(self):
        r = runner.executar("def resolver(x):\n    return len('a' * (2 << 30))\n", [[1]])
        self.assertTrue(r["carga"] or r["casos"][0]["erro"])

    def test_sem_home(self):
        cod = f"import os\ndef resolver(x):\n    return os.path.exists({os.path.expanduser('~')!r})\n"
        self.assertEqual(runner.executar(cod, [[1]])["casos"][0]["saida"], "false")

    def test_sem_rede(self):
        cod = ("import socket\ndef resolver(x):\n    s = socket.socket()\n    s.settimeout(1)\n"
               "    s.connect(('1.1.1.1', 53))\n    return 1\n")
        self.assertIsNotNone(runner.executar(cod, [[1]])["casos"][0]["erro"])

    def test_sem_escrita(self):
        cod = "def resolver(x):\n    open('/work/x', 'w').write('a')\n    return 1\n"
        self.assertIsNotNone(runner.executar(cod, [[1]])["casos"][0]["erro"])

    def test_hash(self):
        self.assertEqual(runner.hash_saida("a", "1"), runner.hash_saida("a", "1"))
        self.assertNotEqual(runner.hash_saida("a", "1"), runner.hash_saida("b", "1"))


class Criterios(unittest.TestCase):
    def test_proibido(self):
        self.assertTrue(criterios.checar("def resolver(l):\n    return sorted(l)\n", {"proibido": ["sorted"]}))
        self.assertTrue(criterios.checar("def resolver(l):\n    l.sort()\n", {"proibido": ["sort"]}))
        self.assertFalse(criterios.checar("def resolver(l):\n    return l\n", {"proibido": ["sorted"]}))

    def test_recursivo(self):
        self.assertTrue(criterios.checar("def resolver(n):\n    return n\n", {"recursivo": True}))
        self.assertFalse(criterios.checar("def resolver(n):\n    return 0 if n == 0 else resolver(n-1)\n",
                                          {"recursivo": True}))


if __name__ == "__main__":
    unittest.main()
