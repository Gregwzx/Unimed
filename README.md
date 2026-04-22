# Teste de Seleção — Desenvolvimento | Unimed Caruaru

## Informações de contato

| Nome      Jailson Ferreira   

| Telefone 81 9896-5933

| E-mail    Jailsonjuniorcom12@gmail.com        

---

## Stack Utilizada e Justificativa

| Kata   | Stack                        | Justificativa                                                                                      |
|--------|------------------------------|----------------------------------------------------------------------------------------------------|
| Kata 1 | Python 3.12                  | Concisão algorítmica, `dataclass` e `IntEnum` nativos, Timsort embutido, pytest maduro.            |
| Kata 2 | C# / .NET 8 + React + TypeScript | Stack sugerida no enunciado; alinhada ao ambiente real da equipe de TI da Unimed Caruaru.     |
| Kata 3 | Markdown (documento)         | Kata sem código — documento técnico em Markdown é mais legível e versionável que PDF.              |
| Kata 4 | Python 3.12                  | Biblioteca padrão pura (`csv`, `json`, `datetime`) — sem dependências externas, zero fricção para rodar. |

---

## Estrutura do Repositório

```
/
├── README.md                  ← este arquivo
│
├── kata-1/
│   ├── triagem.py             ← implementação da fila de triagem
│   ├── test_triagem.py        ← 39 testes unitários (pytest)
│   └── ANALISE.md             ← análise técnica (perguntas 1–4 + SQL)
│
├── kata-2/
│   ├── REQUISITOS.md          ← análise de requisitos (perguntas 5–8)
│   ├── ENGENHARIA.md          ← decisões de arquitetura (perguntas 9–11)
│   ├── backend/
│   │   ├── TasksApi.csproj
│   │   ├── Program.cs         ← API REST completa (endpoints + Service + Repository)
│   │   └── Models/Task.cs     ← modelos de domínio e DTOs
│   └── frontend/
│       ├── package.json
│       └── src/
│           ├── App.tsx        ← interface React com listagem, criação, filtro e ações
│           └── api.ts         ← camada de comunicação com a API
│
├── kata-3/
│   └── PLANO.md               ← diagnóstico, plano de ação, decisão arquitetural, RNFs
│
└── kata-4/
    ├── pipeline.py            ← pipeline de transformação e indicadores
    ├── pedidos.csv            ← dados de exemplo com problemas intencionais
    ├── clientes.csv           ← dados de exemplo com cidades inconsistentes
    ├── entregas.csv           ← dados de exemplo com orphan records e datas mistas
    ├── consolidado.csv        ← saída gerada pelo pipeline
    ├── indicadores.json       ← métricas calculadas
    └── ANALISE.md             ← análise técnica (perguntas 12–15)
```

---

## Como Executar

### Pré-requisitos

- Python 3.10+ (Katas 1 e 4)
- .NET 8 SDK (Kata 2 — backend)
- Node.js 18+ e npm (Kata 2 — frontend)

---

### Kata 1 — Fila de Triagem

```bash
cd kata-1

# Executar a demo
python triagem.py

# Executar os testes (39 casos, cobrindo todas as 5 regras)
pip install pytest
pytest test_triagem.py -v
```

---

### Kata 2 — Painel de Tarefas

**Backend (API REST — .NET 8):**

```bash
cd kata-2/backend
dotnet run
# API disponível em http://localhost:5000
# Swagger UI em http://localhost:5000/swagger
```

**Frontend (React + TypeScript — Vite):**

```bash
cd kata-2/frontend
npm install
npm run dev
# Interface disponível em http://localhost:5173
```

> O frontend espera a API em `http://localhost:5000` por padrão.
> Para alterar, defina a variável de ambiente `VITE_API_URL` antes de rodar.

---

### Kata 3 — Plano Técnico

Documento disponível em:

```
kata-3/PLANO.md
```

Não requer execução — análise técnica escrita.

---

### Kata 4 — Pipeline de Dados

```bash
cd kata-4

# Sem dependências externas — biblioteca padrão Python pura
python pipeline.py

# Saídas geradas:
#   consolidado.csv    — registros transformados e unidos
#   indicadores.json   — 5 métricas de desempenho
```

---

## Resumo das entregas por Kata

### Kata 1 
- Implementação com `Urgencia` (IntEnum), `Paciente` (dataclass) e `ordenar_fila`.
- Regras do enunciado implementadas: prioridade CRÍTICA/ALTA/MÉDIA/BAIXA, FIFO por chegada, idosos 60+ com MÉDIA → ALTA (regra 4), menores de 18 +1 nível (regra 5).
- 39 testes unitários cobrindo casos normais, limites de faixa etária (59/60, 17/18) e interação entre regras 4 e 5.
- Modelagem SQL com tabelas `pacientes`, `filas`, `entradas_fila`, `atendimentos` e view `fila_ativa`.

### Kata 2 
- `REQUISITOS.md`: 5 ambiguidades identificadas com decisão documentada para cada uma; RF e RNF formais; tratamento do requisito de prioridade no backlog.
- Backend: API REST com 4 endpoints (`GET`, `POST`, `PATCH`, `DELETE`), separação Controller → Service → Repository, validação de entrada, respostas HTTP semânticas, CORS configurado.
- Frontend: listagem com indicador visual de status, criação de tarefa, filtros por status, ações de iniciar/concluir/excluir.
- `ENGENHARIA.md`: decisões de arquitetura, observabilidade (logs estruturados, healthcheck, tratamento global de exceções) e plano de migração para multi-usuário.

### Kata 3 
- `PLANO.md` com as 4 seções completas: diagnóstico dos 5 problemas com causa raiz e risco, plano de ação para os 3 prioritários com critério de sucesso, argumentação pela refatoração incremental (Opção A) com justificativa contextualizada, e 4 RNFs comprometidos com métricas mensuráveis.

### Kata 4 
- Pipeline com tratamento de todos os problemas intencionais: datas em 3 formatos, valores com vírgula decimal, campos nulos, orphan records e cidades inconsistentes.
- Arquivo `consolidado.csv` com todos os campos exigidos, incluindo `atraso_dias`.
- 5 indicadores calculados e exibidos em tela e exportados para `indicadores.json`.
- `ANALISE.md` com respostas às perguntas 12–15 incluindo estratégia para 10M linhas e plano de testes.

---

## Comentários — O que eu faria diferente com mais tempo

**Kata 1:** Adicionaria integração com banco de dados via SQLAlchemy usando a modelagem SQL entregue, e um endpoint HTTP simples para simular uma triagem em tempo real com `heapq` para inserção incremental.

**Kata 2:** Migraria a persistência em memória para SQLite com Entity Framework Core, adicionaria testes unitários para `TaskService` com repositório mockado, e configuraria pipeline de CI com GitHub Actions. O frontend ganharia edição de título inline e ordenação por prioridade.

**Kata 3:** Com mais tempo, entrevistaria os desenvolvedores do sistema para validar as causas raiz antes de propor soluções, e produziria um ADR (Architecture Decision Record) formal para a decisão de refatoração incremental.

**Kata 4:** Adicionaria os testes descritos na `ANALISE.md` (especialmente o teste de idempotência por hash), usaria `pathlib` para detecção automática de encoding e implementaria processamento em streaming para escalar para volumes maiores sem alteração de interface.
