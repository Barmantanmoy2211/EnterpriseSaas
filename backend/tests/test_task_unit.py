"""Unit tests for task schemas."""

from app.task.schemas import TaskCreate, TaskResponse


def test_task_create_defaults():
    t = TaskCreate(title="Review design")
    assert t.title == "Review design"
    assert t.status == "todo"
    assert t.priority == "medium"
    assert t.tags == []


def test_task_response_fields():
    r = TaskResponse(
        id="t1",
        title="Ship feature",
        description="",
        project_id="p1",
        assignee_id=None,
        created_by="u1",
        status="in_progress",
        priority="high",
        due_date=None,
        tags=["ops"],
        metadata={},
    )
    assert r.status == "in_progress"
    assert "ops" in r.tags
