# REQUISITOS.md — Kata 2: Levantamento de Ambiguidades

## Contexto

Os requisitos originais descrevem um CRUD de tarefas com listagem, criação, atualização e exclusão. Abaixo estão as ambiguidades identificadas e as decisões tomadas para cada uma.

---

## Ambiguidades identificadas

### 1. Persistência dos dados
**Ambiguidade:** O enunciado não especifica se os dados precisam sobreviver a reinicializações da aplicação.

**Perguntas:**
- Os dados precisam ser persistidos em banco de dados?
- Ou um armazenamento em memória é aceitável para esse kata?

**Decisão adotada:** Armazenamento em memória (`ConcurrentDictionary`), com seed de dados iniciais. Justificativa: simplifica o setup, mantém foco na arquitetura da API, e é explicitamente documentado.

---

### 2. Modelo de dados da tarefa
**Ambiguidade:** O que compõe uma "tarefa"? O enunciado menciona apenas "tarefas" sem detalhar campos.

**Perguntas:**
- Além de título, quais campos são necessários? (descrição, prazo, responsável, tags?)
- Existe hierarquia? (subtarefas, projetos, épicos?)
- Há prioridade numérica ou categórica?

**Decisão adotada:** Modelo mínimo viável: `id`, `title`, `category`, `status`, `createdAt`, `completedAt`. Categoria serve como agrupador simples sem hierarquia.

---

### 3. Regras de transição de status
**Ambiguidade:** É possível reabrir uma tarefa concluída? Quais transições são permitidas?

**Perguntas:**
- `done → pending` é permitido (reabertura)?
- Existem estados intermediários (ex: `in_progress`, `blocked`)?
- Uma tarefa pode ser editada depois de concluída?

**Decisão adotada:** Permitido apenas `pending → done`. Reabrir não é suportado nesta versão. Status é o único campo que não pode ser revertido via PATCH.

---

### 4. Filtros e paginação
**Ambiguidade:** A listagem de tarefas tem limites? Com muitas tarefas, como funciona?

**Perguntas:**
- É necessária paginação (`?page=1&limit=20`)?
- Quais filtros são suportados? (por status, categoria, data, texto livre?)
- Qual a ordenação padrão?

**Decisão adotada:** Sem paginação nesta versão (escopo do kata). Filtro por `status` implementado. Ordenação padrão: `createdAt` decrescente.

---

### 5. Autenticação e multiusuário
**Ambiguidade:** As tarefas são compartilhadas ou por usuário?

**Perguntas:**
- Há conceito de "dono" da tarefa?
- A API precisa de autenticação (JWT, API Key)?
- Múltiplos usuários podem ver/editar as mesmas tarefas?

**Decisão adotada:** API sem autenticação, estado global compartilhado. Escopo definido como single-tenant para este kata.

---

### 6. Validações e respostas de erro
**Ambiguidade:** Quais campos são obrigatórios? Qual formato de erro retornar?

**Perguntas:**
- Título tem comprimento máximo?
- Categoria aceita valores livres ou é um enum?
- Erros retornam `{ message }` ou `{ errors: [...] }`?

**Decisão adotada:** Título obrigatório, máximo 200 chars. Categoria: string livre com sugestões no frontend. Erros retornam `{ error: string }`.