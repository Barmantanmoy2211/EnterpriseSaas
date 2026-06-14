from app.permissions.service import PermissionService


class TestPermissionConditions:
    def test_evaluate_conditions_match(self):
        result = PermissionService._evaluate_conditions(
            {"owner_id": "user-1"},
            {"owner_id": "user-1"},
        )
        assert result is True

    def test_evaluate_conditions_mismatch(self):
        result = PermissionService._evaluate_conditions(
            {"owner_id": "user-1"},
            {"owner_id": "user-2"},
        )
        assert result is False

    def test_evaluate_conditions_empty(self):
        result = PermissionService._evaluate_conditions({}, {"any": "value"})
        assert result is True
