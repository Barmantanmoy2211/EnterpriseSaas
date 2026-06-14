class TestEmployeeCodeValidation:
    def test_employee_response_fields(self):
        from app.employee.schemas import EmployeeResponse

        r = EmployeeResponse(
            id="1",
            user_id=None,
            employee_code="EMP001",
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone="",
            org_node_id=None,
            job_title="Engineer",
            department="Engineering",
            employment_type="full_time",
            status="active",
            hire_date=None,
            manager_id=None,
            profile={},
        )
        assert r.employee_code == "EMP001"
        assert r.status == "active"
