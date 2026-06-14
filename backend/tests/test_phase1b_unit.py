from app.permissions.service import PermissionService


class TestPermissionConditionsExtended:
    def test_multiple_conditions(self):
        result = PermissionService._evaluate_conditions(
            {"role": "admin", "level": 1},
            {"role": "admin", "level": 1},
        )
        assert result is True
