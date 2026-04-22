namespace TasksApi.Models;

public enum TaskStatus
{
    PENDING,
    IN_PROGRESS,
    DONE
}

public enum TaskPriority
{
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL
}

public class TaskItem
{
    public int            Id         { get; set; }
    public string         Title      { get; set; } = string.Empty;
    public TaskStatus     Status     { get; set; } = TaskStatus.PENDING;
    public TaskPriority?  Priority   { get; set; }
    public DateTime       CreatedAt  { get; set; } = DateTime.UtcNow;
    public DateTime?      UpdatedAt  { get; set; }
}

/// <summary>DTO para criação de tarefa.</summary>
public record CreateTaskRequest(
    string        Title,
    TaskPriority? Priority = null
);

/// <summary>DTO para atualização parcial (todos os campos são opcionais).</summary>
public record UpdateTaskRequest(
    string?        Title    = null,
    TaskStatus?    Status   = null,
    TaskPriority?  Priority = null
);