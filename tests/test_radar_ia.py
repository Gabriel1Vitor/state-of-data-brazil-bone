"""Regressão das categorias exclusivas de IA nas três edições do Radar.

Execute com: python -m unittest discover -s tests -v
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "reports"))
import radar


class TesteRadarIA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resultado = radar.compute()

    def test_codigo_tem_prioridade_sobre_ferramentas_gratuitas(self):
        # Inclui quem marcou simultaneamente IA de código e ferramentas gratuitas,
        # sem nenhuma opção paga: 132, 222 e 116 respostas, respectivamente.
        esperado = {
            "2023": (8.5, 58.8),
            "2024/25": (14.8, 45.0),
            "2025/26": (11.3, 21.8),
        }
        for ano, (codigo, gratuitas) in esperado.items():
            with self.subTest(ano=ano):
                categorias = self.resultado["ai"][ano]
                self.assertEqual(categorias["Só IA de código"], codigo)
                self.assertEqual(categorias["Só gratuitas"], gratuitas)

    def test_preserva_demais_categorias_e_denominadores(self):
        esperado = {
            "2023": (6.3, 6.7, 19.7, 3772),
            "2024/25": (19.2, 14.4, 6.5, 3619),
            "2025/26": (42.4, 22.4, 2.1, 2106),
        }
        for ano, valores in esperado.items():
            with self.subTest(ano=ano):
                categorias = self.resultado["ai"][ano]
                self.assertEqual(
                    tuple(categorias[chave] for chave in
                          ("Empresa paga", "Paga do próprio bolso", "Não usa", "_n")),
                    valores,
                )

    def test_preserva_uso_total_de_ia_de_codigo(self):
        # O gráfico de uso total inclui também quem paga por outras ferramentas.
        self.assertEqual(self.resultado["ai_code"], [11.8, 23.7, 29.8])


if __name__ == "__main__":
    unittest.main()
