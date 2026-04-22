"""
Kata 1 — Triagem de Pacientes
Sistema de organização de fila por regras de prioridade clínica.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import List


# ─────────────────────────────────────────────
# Domínio
# ─────────────────────────────────────────────

class Prioridade(IntEnum):
    """
    Níveis de prioridade inspirados no Protocolo de Manchester.
    Valores menores = maior urgência (facilita sorted() ascendente).
    """
    EMERGENCIA = 1  # risco imediato de vida
    URGENTE    = 2  # pode deteriorar rapidamente
    ALTA       = 3  # dor intensa mas estável
    NORMAL     = 4  # consulta de rotina
    BAIXA      = 5  # queixa leve


@dataclass
class Paciente:
    nome: str
    idade: int
    nivel_dor: int           # 0–10
    pressao_sistolica: int   # mmHg
    temperatura: float       # °C
    chegada: int             # ordem de chegada (desempate)
    prioridade: Prioridade = field(init=False)

    def __post_init__(self):
        self.prioridade = calcular_prioridade(self)

    def __repr__(self):
        return (
            f"Paciente({self.nome!r}, prioridade={self.prioridade.name}, "
            f"idade={self.idade}, dor={self.nivel_dor}, "
            f"PA={self.pressao_sistolica}, T={self.temperatura})"
        )


# ─────────────────────────────────────────────
# Regras de prioridade
# ─────────────────────────────────────────────

def calcular_prioridade(p: Paciente) -> Prioridade:
    """
    Regras aplicadas em cascata — primeira que bate define a prioridade:

    EMERGENCIA : PA sistólica < 80  OU  temperatura >= 39.5
    URGENTE    : dor >= 8           OU  PA sistólica < 100
    ALTA       : dor >= 6           OU  temperatura >= 38.0
    NORMAL     : dor >= 3           OU  idade >= 60
    BAIXA      : demais casos
    """
    if p.pressao_sistolica < 80 or p.temperatura >= 39.5:
        return Prioridade.EMERGENCIA

    if p.nivel_dor >= 8 or p.pressao_sistolica < 100:
        return Prioridade.URGENTE

    if p.nivel_dor >= 6 or p.temperatura >= 38.0:
        return Prioridade.ALTA

    if p.nivel_dor >= 3 or p.idade >= 60:
        return Prioridade.NORMAL

    return Prioridade.BAIXA


# ─────────────────────────────────────────────
# Ordenação da fila
# ─────────────────────────────────────────────

def ordenar_fila(pacientes: List[Paciente]) -> List[Paciente]:
    """
    Critérios de ordenação (em ordem de prioridade):
      1. Prioridade clínica (EMERGENCIA < URGENTE < ... < BAIXA)
      2. Idade decrescente (idosos à frente dentro do mesmo nível)
      3. Ordem de chegada — FIFO como desempate final

    Complexidade: O(n log n) — usa Timsort do Python.
    """
    return sorted(
        pacientes,
        key=lambda p: (p.prioridade, -p.idade, p.chegada)
    )


# ─────────────────────────────────────────────
# Exibição
# ─────────────────────────────────────────────

def exibir_fila(fila: List[Paciente]) -> None:
    sep = "-" * 68
    print(sep)
    print(f"{'#':<4} {'Nome':<22} {'Prioridade':<14} {'Idade':>5} {'Chegada':>8}")
    print(sep)
    for pos, p in enumerate(fila, start=1):
        print(
            f"{pos:<4} {p.nome:<22} {p.prioridade.name:<14} "
            f"{p.idade:>5} {p.chegada:>8}"
        )
    print(sep)


# ─────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────

if __name__ == "__main__":
    pacientes = [
        Paciente("Ana Lima",       72, nivel_dor=3, pressao_sistolica=120, temperatura=37.2, chegada=1),
        Paciente("Bruno Souza",    35, nivel_dor=9, pressao_sistolica=110, temperatura=37.0, chegada=2),
        Paciente("Carla Mendes",   45, nivel_dor=5, pressao_sistolica=75,  temperatura=37.5, chegada=3),
        Paciente("Diego Ferreira", 28, nivel_dor=1, pressao_sistolica=130, temperatura=36.8, chegada=4),
        Paciente("Eva Santos",     65, nivel_dor=4, pressao_sistolica=115, temperatura=38.5, chegada=5),
        Paciente("Fabio Costa",    50, nivel_dor=7, pressao_sistolica=105, temperatura=39.6, chegada=6),
        Paciente("Gabi Rocha",     20, nivel_dor=2, pressao_sistolica=122, temperatura=36.5, chegada=7),
    ]

    print("\n=== ORDEM DE CHEGADA ===")
    exibir_fila(pacientes)

    fila = ordenar_fila(pacientes)

    print("\n=== FILA APOS TRIAGEM ===")
    exibir_fila(fila)