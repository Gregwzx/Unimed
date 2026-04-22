# ENGENHARIA.md — Kata 2: Decisões de Arquitetura

## Stack escolhida

| Camada     | Tecnologia             | Justificativa                                              |
|------------|------------------------|------------------------------------------------------------|
| Backend    | ASP.NET Core 8 Minimal API | Stack sugerida; Minimal API reduz cerimônia sem perder poder |
| Frontend   | React 18 + TypeScript  | Tipagem estática previne bugs em runtime; ecossistema maduro |
| Persistência | In-memory (ConcurrentDictionary) | Sem dependências externas; escopo do kata              |
| Build      | Vite                   | HMR instantâneo; zero config para React + TS              |

---

## Decisões de arquitetura

### 1. Minimal API vs Controllers
**Decisão:** Minimal API (sem `[ApiController]`)

**Justificativa:** Para uma API CRUD simples com 5 endpoints, Minimal API é mais legível e tem menor overhead. Controllers fazem mais sentido quando há middlewares complexos por controller, versionamento ou múltiplas áreas de domínio. Neste kata, a clareza supera a convenção.

### 2. Repositório em memória com interface
**Decisão:** Classe `TaskRepository` injetada via DI como Singleton.

**Justificativa:**
- Isola a lógica de acesso a dados dos endpoints
- Facilita trocar por repositório com EF Core/banco sem tocar nos endpoints
- DI permite mock em testes de integração

**Evolução natural:**
```csharp
// Para adicionar persistência real, basta:
builder.Services.AddDbContext<AppDbContext>(opt => opt.UseSqlite("tasks.db"));
builder.Services.AddScoped<TaskRepository, EfTaskRepository>();
```

### 3. ConcurrentDictionary para thread-safety
**Decisão:** `ConcurrentDictionary` + `Interlocked.Increment` para IDs.

**Justificativa:** ASP.NET Core é multi-threaded por padrão. `Dictionary` simples causaria race conditions com requests simultâneas. `ConcurrentDictionary` é lock-free para operações de leitura.

### 4. Frontend sem biblioteca de estado global
**Decisão:** `useState` + `useCallback` — sem Redux/Zustand/Jotai.

**Justificativa:** O estado da aplicação é simples (uma lista de tarefas + filtro). Adicionar biblioteca de estado global seria over-engineering. Se crescesse para múltiplas entidades relacionadas ou real-time updates (WebSockets), revisitaríamos.

### 5. Estilos inline no React
**Decisão:** Inline styles + objetos de estilo nomeados — sem CSS externo ou Tailwind.

**Justificativa:** Zero dependências extras, sem risco de conflito de classes, facilidade de copiar. Trade-off: sem pseudo-classes (`:hover`) sem JavaScript extra.

---

## Trade-offs conscientes

| Decisão                  | Benefício                        | Trade-off aceito                          |
|--------------------------|----------------------------------|-------------------------------------------|
| In-memory storage        | Setup imediato, sem banco        | Dados perdidos ao reiniciar               |
| Sem autenticação         | Foco na arquitetura CRUD         | Não adequado para produção                |
| Sem paginação            | Código mais simples              | Degrada com milhares de tarefas           |
| Inline styles            | Sem dependências CSS             | Sem hover/focus states sem JS extra       |
| Status só `pending→done` | Modelo simples e consistente     | Não permite reabertura de tarefas         |

---

## Como executar

### Backend
```bash
cd kata-2/backend
dotnet run
# API disponível em http://localhost:5000
```

### Frontend
```bash
cd kata-2/frontend
npm install
npm run dev
# Interface disponível em http://localhost:5173
```

---

## Endpoints da API

| Método   | Rota            | Descrição                        |
|----------|-----------------|----------------------------------|
| `GET`    | `/tasks`        | Lista todas as tarefas           |
| `GET`    | `/tasks?status=pending` | Lista por status         |
| `GET`    | `/tasks/{id}`   | Busca tarefa por ID              |
| `POST`   | `/tasks`        | Cria nova tarefa                 |
| `PATCH`  | `/tasks/{id}`   | Atualiza título, categoria ou status |
| `DELETE` | `/tasks/{id}`   | Remove tarefa                    |