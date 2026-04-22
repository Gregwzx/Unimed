# ANALISE.md — Kata 1: Triagem de Pacientes

## 1. Estrutura de dados escolhida

### `Prioridade` — IntEnum
Usei `IntEnum` em vez de `Enum` simples porque o valor inteiro serve diretamente como chave de ordenação. Isso elimina a necessidade de dicionários de mapeamento e torna a key do `sorted()` limpa e legível.

### `Paciente` — dataclass
`@dataclass` gera automaticamente `__init__`, `__repr__` e comparações, reduzindo boilerplate. O campo `prioridade` é calculado em `__post_init__`, garantindo que um `Paciente` seja sempre criado já com sua prioridade correta — sem estado inconsistente.

### Lista Python (`List[Paciente]`)
A fila é representada como lista simples. A ordenação é feita por `sorted()` (Timsort), que devolve uma **nova** lista sem modificar a original — importante para imutabilidade e testabilidade.

---

## 2. Complexidade computacional

| Operação               | Complexidade | Justificativa                                    |
|------------------------|:------------:|--------------------------------------------------|
| `calcular_prioridade`  | O(1)         | Sequência fixa de comparações (máx. ~6 checks)   |
| `ordenar_fila`         | O(n log n)   | Timsort do Python — comparações com tupla de 3   |
| `__post_init__` (N px) | O(n)         | Chamado 1× por paciente na criação               |
| **Pipeline completo**  | **O(n log n)**| Dominado pela ordenação                         |

Timsort é especialmente eficiente quando a lista já está parcialmente ordenada (caso real: pacientes chegam em blocos de prioridade similares).

---

## 3. Como as regras interagem

As regras formam uma **cascata exclusiva**: a primeira regra satisfeita encerra a avaliação. Isso cria uma hierarquia estrita de gravidade.

**Pontos-chave de interação:**

- **Combinação OR dentro de cada nível**: um paciente com PA=95 (< 100) é URGENTE *mesmo* que sua dor seja 0. A lógica OR dentro de cada regra captura vias clínicas independentes de deterioração.
- **Prioridade da PA crítica**: PA < 80 é EMERGENCIA independentemente de qualquer outra variável — inclusive dor=10. Isso evita que pacientes em choque sejam subestimados.
- **Idosos protegidos mesmo sem sintomas agudos**: idade ≥ 60 garante pelo menos NORMAL, reconhecendo maior vulnerabilidade fisiológica.
- **Desempate dentro do mesmo nível**: idosos são atendidos antes de jovens com mesma prioridade, e a ordem de chegada é o critério final (FIFO justo).

**Exemplo de interação complexa:**
> Paciente: dor=9, PA=70, T=37.0
> → Regra 1 bate (PA=70 < 80) → EMERGENCIA
> → Regra 2 **nunca é avaliada**, mesmo com dor=9

---

## 4. Como estender o sistema

### Adicionar novos critérios de prioridade
A função `calcular_prioridade` segue o **padrão Chain of Responsibility** implícito. Para adicionar um novo critério:
1. Adicionar o campo ao `Paciente`
2. Inserir a condição na posição correta da cascata

```python
# Exemplo: oximetria < 92% → EMERGENCIA
if p.oximetria < 92 or p.pressao_sistolica < 80 or p.temperatura >= 39.5:
    return Prioridade.EMERGENCIA
```

### Novos critérios de desempate
A `key` do `sorted()` é uma tupla — basta adicionar mais elementos:

```python
key=lambda p: (p.prioridade, -p.idade, p.vulnerabilidade_social, p.chegada)
```

### Persistência e escalabilidade
- **Banco de dados**: o `Paciente` pode ser mapeado para ORM (SQLAlchemy) sem alterar a lógica de triagem.
- **Atualização dinâmica**: trocar `sorted()` por `heapq` se novos pacientes chegam continuamente e a fila precisa ser reordenada incrementalmente — O(log n) por inserção.
- **Regras configuráveis**: extrair os limiares (`< 80`, `>= 39.5`, etc.) para um objeto de configuração ou banco de regras, permitindo ajustes sem alterar código.

---

## Modelagem SQL (opcional)

```sql
-- Enum de prioridade
CREATE TYPE prioridade_enum AS ENUM (
    'EMERGENCIA', 'URGENTE', 'ALTA', 'NORMAL', 'BAIXA'
);

-- Tabela de pacientes na fila
CREATE TABLE fila_triagem (
    id                  SERIAL PRIMARY KEY,
    nome                VARCHAR(100)     NOT NULL,
    idade               SMALLINT         NOT NULL CHECK (idade >= 0),
    nivel_dor           SMALLINT         NOT NULL CHECK (nivel_dor BETWEEN 0 AND 10),
    pressao_sistolica   SMALLINT         NOT NULL,
    temperatura         NUMERIC(4,1)     NOT NULL,
    chegada             TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    prioridade          prioridade_enum  NOT NULL,
    atendido_em         TIMESTAMPTZ,
    criado_em           TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

-- Índice para ordenação eficiente da fila
CREATE INDEX idx_fila_ordenacao
    ON fila_triagem (prioridade, idade DESC, chegada ASC)
    WHERE atendido_em IS NULL;

-- View da fila ativa ordenada
CREATE VIEW fila_ativa AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY
            CASE prioridade
                WHEN 'EMERGENCIA' THEN 1
                WHEN 'URGENTE'    THEN 2
                WHEN 'ALTA'       THEN 3
                WHEN 'NORMAL'     THEN 4
                WHEN 'BAIXA'      THEN 5
            END,
            idade DESC,
            chegada ASC
    ) AS posicao,
    id, nome, idade, prioridade, nivel_dor, pressao_sistolica,
    temperatura, chegada
FROM fila_triagem
WHERE atendido_em IS NULL
ORDER BY posicao;
```