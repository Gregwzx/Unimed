"""
Testes unitários para o módulo de triagem de pacientes.
Execute com: pytest test_triagem.py -v
"""

import pytest
from triagem import Paciente, Prioridade, calcular_prioridade, ordenar_fila


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def paciente(
    nome="Teste",
    idade=30,
    nivel_dor=0,
    pressao_sistolica=120,
    temperatura=36.5,
    chegada=1,
) -> Paciente:
    """Factory com valores padrão saudáveis (BAIXA prioridade)."""
    return Paciente(
        nome=nome,
        idade=idade,
        nivel_dor=nivel_dor,
        pressao_sistolica=pressao_sistolica,
        temperatura=temperatura,
        chegada=chegada,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Testes de calcular_prioridade
# ─────────────────────────────────────────────────────────────────────────────

class TestCalcularPrioridade:

    # --- EMERGENCIA ---

    def test_emergencia_por_pressao_muito_baixa(self):
        p = paciente(pressao_sistolica=79)
        assert p.prioridade == Prioridade.EMERGENCIA

    def test_emergencia_por_temperatura_critica(self):
        p = paciente(temperatura=39.5)
        assert p.prioridade == Prioridade.EMERGENCIA

    def test_emergencia_temperatura_exatamente_no_limite(self):
        p = paciente(temperatura=39.5)
        assert p.prioridade == Prioridade.EMERGENCIA

    def test_emergencia_pressao_exatamente_no_limite(self):
        # PA = 79 dispara; PA = 80 não dispara regra 1
        assert paciente(pressao_sistolica=79).prioridade == Prioridade.EMERGENCIA
        assert paciente(pressao_sistolica=80).prioridade != Prioridade.EMERGENCIA

    # --- URGENTE ---

    def test_urgente_por_dor_alta(self):
        p = paciente(nivel_dor=8)
        assert p.prioridade == Prioridade.URGENTE

    def test_urgente_por_pressao_baixa(self):
        p = paciente(pressao_sistolica=95)
        assert p.prioridade == Prioridade.URGENTE

    def test_urgente_dor_9(self):
        p = paciente(nivel_dor=9)
        assert p.prioridade == Prioridade.URGENTE

    # --- ALTA ---

    def test_alta_por_dor_6(self):
        p = paciente(nivel_dor=6)
        assert p.prioridade == Prioridade.ALTA

    def test_alta_por_temperatura_febre(self):
        p = paciente(temperatura=38.0)
        assert p.prioridade == Prioridade.ALTA

    def test_alta_dor_7_sem_outras_condicoes(self):
        p = paciente(nivel_dor=7)
        assert p.prioridade == Prioridade.ALTA

    # --- NORMAL ---

    def test_normal_por_dor_3(self):
        p = paciente(nivel_dor=3)
        assert p.prioridade == Prioridade.NORMAL

    def test_normal_por_idade_60(self):
        p = paciente(idade=60)
        assert p.prioridade == Prioridade.NORMAL

    def test_normal_idoso_com_dor_baixa(self):
        p = paciente(idade=75, nivel_dor=1)
        assert p.prioridade == Prioridade.NORMAL

    # --- BAIXA ---

    def test_baixa_paciente_saudavel(self):
        p = paciente(idade=25, nivel_dor=0, pressao_sistolica=120, temperatura=36.5)
        assert p.prioridade == Prioridade.BAIXA

    def test_baixa_dor_2_jovem(self):
        p = paciente(idade=20, nivel_dor=2)
        assert p.prioridade == Prioridade.BAIXA

    # --- Interação de regras ---

    def test_emergencia_sobrepoe_dor_alta(self):
        """PA crítica deve classificar como EMERGENCIA mesmo com dor=9."""
        p = paciente(nivel_dor=9, pressao_sistolica=70)
        assert p.prioridade == Prioridade.EMERGENCIA

    def test_temperatura_critica_sobrepoe_dor_alta(self):
        """Temperatura >= 39.5 é EMERGENCIA, independente da dor."""
        p = paciente(nivel_dor=10, temperatura=40.0)
        assert p.prioridade == Prioridade.EMERGENCIA


# ─────────────────────────────────────────────────────────────────────────────
# Testes de ordenar_fila
# ─────────────────────────────────────────────────────────────────────────────

class TestOrdenarFila:

    def test_fila_vazia(self):
        assert ordenar_fila([]) == []

    def test_unico_paciente(self):
        p = paciente()
        assert ordenar_fila([p]) == [p]

    def test_emergencia_antes_de_urgente(self):
        urgente    = paciente(nome="U", nivel_dor=8, chegada=1)
        emergencia = paciente(nome="E", pressao_sistolica=70, chegada=2)
        fila = ordenar_fila([urgente, emergencia])
        assert fila[0].nome == "E"

    def test_ordem_completa_de_prioridades(self):
        baixa      = paciente(nome="B", chegada=5)
        normal     = paciente(nome="N", nivel_dor=3, chegada=4)
        alta       = paciente(nome="A", nivel_dor=6, chegada=3)
        urgente    = paciente(nome="U", nivel_dor=8, chegada=2)
        emergencia = paciente(nome="E", pressao_sistolica=70, chegada=1)

        fila = ordenar_fila([baixa, normal, alta, urgente, emergencia])
        assert [p.nome for p in fila] == ["E", "U", "A", "N", "B"]

    def test_desempate_por_idade_decrescente(self):
        """Mesmo nível de prioridade: idoso deve ser atendido primeiro."""
        jovem = paciente(nome="Jovem", idade=25, nivel_dor=3, chegada=1)
        idoso = paciente(nome="Idoso", idade=70, nivel_dor=3, chegada=2)
        fila = ordenar_fila([jovem, idoso])
        assert fila[0].nome == "Idoso"

    def test_desempate_por_chegada_quando_mesma_idade(self):
        p1 = paciente(nome="Primeiro", idade=40, nivel_dor=3, chegada=1)
        p2 = paciente(nome="Segundo",  idade=40, nivel_dor=3, chegada=2)
        fila = ordenar_fila([p2, p1])
        assert fila[0].nome == "Primeiro"

    def test_ordenacao_nao_modifica_lista_original(self):
        p1 = paciente(nome="X", nivel_dor=8, chegada=2)
        p2 = paciente(nome="Y", pressao_sistolica=70, chegada=1)
        original = [p1, p2]
        ordenar_fila(original)
        assert original[0].nome == "X"  # lista original intacta

    def test_multiplos_emergencia_desempata_por_idade_e_chegada(self):
        e1 = paciente(nome="E1", pressao_sistolica=60, idade=50, chegada=1)
        e2 = paciente(nome="E2", pressao_sistolica=60, idade=70, chegada=2)
        e3 = paciente(nome="E3", pressao_sistolica=60, idade=70, chegada=3)
        fila = ordenar_fila([e3, e1, e2])
        nomes = [p.nome for p in fila]
        # E2 e E3 têm 70 anos; E2 chegou antes → E2, E3, E1
        assert nomes == ["E2", "E3", "E1"]

    def test_cenario_realista_completo(self):
        pacientes = [
            Paciente("Ana",   72, nivel_dor=3, pressao_sistolica=120, temperatura=37.2, chegada=1),
            Paciente("Bruno", 35, nivel_dor=9, pressao_sistolica=110, temperatura=37.0, chegada=2),
            Paciente("Carla", 45, nivel_dor=5, pressao_sistolica=75,  temperatura=37.5, chegada=3),
            Paciente("Diego", 28, nivel_dor=1, pressao_sistolica=130, temperatura=36.8, chegada=4),
            Paciente("Eva",   65, nivel_dor=4, pressao_sistolica=115, temperatura=38.5, chegada=5),
            Paciente("Fabio", 50, nivel_dor=7, pressao_sistolica=105, temperatura=39.6, chegada=6),
            Paciente("Gabi",  20, nivel_dor=2, pressao_sistolica=122, temperatura=36.5, chegada=7),
        ]
        fila = ordenar_fila(pacientes)
        # Carla (PA=75) e Fabio (T=39.6) são EMERGENCIA
        assert fila[0].prioridade == Prioridade.EMERGENCIA
        assert fila[1].prioridade == Prioridade.EMERGENCIA
        # Bruno (dor=9) é URGENTE
        assert fila[2].nome == "Bruno"
        assert fila[2].prioridade == Prioridade.URGENTE
        # Diego e Gabi são BAIXA — devem ser os últimos
        assert set(p.nome for p in fila[-2:]) == {"Diego", "Gabi"}