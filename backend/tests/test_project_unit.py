"""Unit tests for project schemas."""

from app.project.schemas import ProjectCreate, ProjectResponse


def test_project_create_defaults():
    p = ProjectCreate(name="Alpha Initiative")
    assert p.name == "Alpha Initiative"
    assert p.status == "active"
    assert p.priority == "medium"


def test_project_response_fields():
    r = ProjectResponse(
        id="abc",
        name="Alpha",
        description="",
        code="PRJ-001",
        status="active",
        priority="high",
        owner_id=None,
        org_node_id=None,
        start_date=None,
        end_date=None,
        metadata={},
    )
    assert r.code == "PRJ-001"
    assert r.priority == "high"
