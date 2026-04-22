using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using System.Collections.Concurrent;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
        policy.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader());
});

builder.Services.AddSingleton<TaskRepository>();
builder.Services.AddEndpointsApiExplorer();

var app = builder.Build();
app.UseCors();

// ── Seed inicial ────────────────────────────────────────────────────────────
var repo = app.Services.GetRequiredService<TaskRepository>();
repo.Add(new CreateTaskDto("Revisar Pull Request #42", "tech-debt"));
repo.Add(new CreateTaskDto("Escrever testes unitários", "quality"));
repo.Add(new CreateTaskDto("Atualizar documentação da API", "docs"));

// ── Endpoints ───────────────────────────────────────────────────────────────

// GET /tasks  — lista (com filtro opcional por status)
app.MapGet("/tasks", (string? status, TaskRepository r) =>
{
    var tasks = r.GetAll();
    if (!string.IsNullOrEmpty(status))
        tasks = tasks.Where(t => t.Status.Equals(status, StringComparison.OrdinalIgnoreCase)).ToList();
    return Results.Ok(tasks);
});

// GET /tasks/{id}
app.MapGet("/tasks/{id:int}", (int id, TaskRepository r) =>
    r.GetById(id) is TaskItem t ? Results.Ok(t) : Results.NotFound());

// POST /tasks
app.MapPost("/tasks", (CreateTaskDto dto, TaskRepository r) =>
{
    if (string.IsNullOrWhiteSpace(dto.Title))
        return Results.BadRequest(new { error = "Título é obrigatório." });

    var task = r.Add(dto);
    return Results.Created($"/tasks/{task.Id}", task);
});

// PATCH /tasks/{id}
app.MapMethods("/tasks/{id:int}", ["PATCH"], (int id, UpdateTaskDto dto, TaskRepository r) =>
{
    var updated = r.Update(id, dto);
    return updated is not null ? Results.Ok(updated) : Results.NotFound();
});

// DELETE /tasks/{id}
app.MapDelete("/tasks/{id:int}", (int id, TaskRepository r) =>
    r.Delete(id) ? Results.NoContent() : Results.NotFound());

app.Run();


// ── Modelos ─────────────────────────────────────────────────────────────────

public record TaskItem(
    int Id,
    string Title,
    string Category,
    string Status,       // "pending" | "done"
    DateTime CreatedAt,
    DateTime? CompletedAt
);

public record CreateTaskDto(string Title, string Category = "general");

public record UpdateTaskDto(
    string? Title,
    string? Category,
    string? Status
);


// ── Repositório em memória ───────────────────────────────────────────────────

public class TaskRepository
{
    private readonly ConcurrentDictionary<int, TaskItem> _store = new();
    private int _nextId = 1;

    public TaskItem Add(CreateTaskDto dto)
    {
        var id = Interlocked.Increment(ref _nextId) - 1;
        var task = new TaskItem(id, dto.Title, dto.Category, "pending", DateTime.UtcNow, null);
        _store[id] = task;
        return task;
    }

    public List<TaskItem> GetAll() => _store.Values.OrderByDescending(t => t.CreatedAt).ToList();

    public TaskItem? GetById(int id) => _store.TryGetValue(id, out var t) ? t : null;

    public TaskItem? Update(int id, UpdateTaskDto dto)
    {
        if (!_store.TryGetValue(id, out var existing)) return null;

        var newStatus      = dto.Status ?? existing.Status;
        var completedAt    = newStatus == "done" && existing.Status != "done"
                             ? DateTime.UtcNow
                             : existing.CompletedAt;

        var updated = existing with
        {
            Title       = dto.Title    ?? existing.Title,
            Category    = dto.Category ?? existing.Category,
            Status      = newStatus,
            CompletedAt = completedAt
        };

        _store[id] = updated;
        return updated;
    }

    public bool Delete(int id) => _store.TryRemove(id, out _);
}