import unittest
from datetime import date, timedelta

from kata import progresso as p

D0 = date(2026, 10, 1)


def dias(*offsets):
    return {D0 + timedelta(days=o) for o in offsets}


class DesafioDoDia(unittest.TestCase):
    def test_primeiro_dia(self):
        self.assertEqual(p.desafio_do_dia({}, 100, D0), (1, "pendente"))

    def test_feito_hoje_trava(self):
        self.assertEqual(p.desafio_do_dia({1: D0}, 100, D0), (1, "feito"))

    def test_dia_seguinte_libera_o_proximo(self):
        self.assertEqual(p.desafio_do_dia({1: D0}, 100, D0 + timedelta(1)), (2, "pendente"))

    def test_dia_perdido_nao_pula_conteudo(self):
        self.assertEqual(p.desafio_do_dia({1: D0}, 100, D0 + timedelta(5)), (2, "pendente"))

    def test_fim(self):
        self.assertEqual(p.desafio_do_dia({1: D0, 2: D0 + timedelta(1)}, 2, D0 + timedelta(2)), (None, "fim"))


class Ofensiva(unittest.TestCase):
    def test_vazia(self):
        self.assertEqual(p.ofensiva(set(), D0)["atual"], 0)

    def test_seguidos(self):
        self.assertEqual(p.ofensiva(dias(0, 1, 2), D0 + timedelta(2))["atual"], 3)

    def test_hoje_pendente_nao_quebra(self):
        self.assertEqual(p.ofensiva(dias(0, 1, 2), D0 + timedelta(3))["atual"], 3)

    def test_dia_perdido_zera(self):
        e = p.ofensiva(dias(0, 1, 2, 4), D0 + timedelta(4))
        self.assertEqual((e["atual"], e["recorde"]), (1, 3))

    def test_ontem_perdido_zera_ate_resolver(self):
        self.assertEqual(p.ofensiva(dias(0, 1), D0 + timedelta(3))["atual"], 0)

    def test_congelamento_ganho_e_gasto(self):
        sete = dias(*range(7))
        self.assertEqual(p.ofensiva(sete, D0 + timedelta(6))["congelamentos"], 1)
        e = p.ofensiva(sete | dias(8), D0 + timedelta(8))
        self.assertEqual((e["atual"], e["congelamentos"]), (8, 0))
        self.assertEqual(e["congelados"], dias(7))

    def test_congelamento_maximo(self):
        e = p.ofensiva(dias(*range(30)), D0 + timedelta(29))
        self.assertEqual(e["congelamentos"], p.MAX_CONGELAMENTOS)

    def test_dois_buracos_com_um_congelamento(self):
        e = p.ofensiva(dias(*range(7), 9), D0 + timedelta(9))
        self.assertEqual(e["atual"], 1)


class Pontos(unittest.TestCase):
    def test_xp(self):
        self.assertEqual(p.xp(1, 0, 0), 20)
        self.assertEqual(p.xp(2, 3, 0), 30)
        self.assertEqual(p.xp(1, 1, 3), 1)  # nunca abaixo do nível

    def test_nivel_jogador(self):
        self.assertEqual([p.nivel_jogador(x) for x in (0, 99, 100, 299, 300, 600)], [1, 1, 2, 2, 3, 4])

    def test_titulo(self):
        self.assertEqual(p.titulo(0), "Aprendiz")
        self.assertEqual(p.titulo(150), "Mestre")


if __name__ == "__main__":
    unittest.main()
