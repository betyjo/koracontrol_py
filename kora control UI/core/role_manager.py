from enum import Enum


class Role(Enum):
    ADMIN    = "admin"
    OPERATOR = "operator"
    VIEWER   = "viewer"


ROLE_PERMISSIONS = {
    Role.ADMIN: {
        "can_edit_hmi":           True,
        "can_override":           True,
        "can_view_alarms":        True,
        "can_acknowledge_alarms": True,
        "can_view_trends":        True,
        "can_manage_users":       True,
    },
    Role.OPERATOR: {
        "can_edit_hmi":           False,
        "can_override":           True,
        "can_view_alarms":        True,
        "can_acknowledge_alarms": True,
        "can_view_trends":        True,
        "can_manage_users":       False,
    },
    Role.VIEWER: {
        "can_edit_hmi":           False,
        "can_override":           False,
        "can_view_alarms":        True,
        "can_acknowledge_alarms": False,
        "can_view_trends":        True,
        "can_manage_users":       False,
    },
}


class RoleManager:
    def __init__(self):
        self._current_role: Role | None = None
        self._current_user: str | None = None

    def set_user(self, username: str, role: Role):
        self._current_user = username
        self._current_role = role

    def clear(self):
        self._current_user = None
        self._current_role = None

    @property
    def current_user(self) -> str | None:
        return self._current_user

    @property
    def current_role(self) -> Role | None:
        return self._current_role

    def has_permission(self, permission: str) -> bool:
        if self._current_role is None:
            return False
        return ROLE_PERMISSIONS.get(self._current_role, {}).get(permission, False)


role_manager = RoleManager()
