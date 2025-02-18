from datetime import datetime, timezone


class User:
    def __init__(
        self,
        username,
        email,
        password,
        role="user",
        created_at=None,
        updated_at=None,
        deleted=False,
    ):
        self.username = username
        self.email = email
        self.password = password  # Hashed password will be stored here
        self.role = role
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or None
        self.deleted = deleted

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted": self.deleted,
        }

    @staticmethod
    def from_dict(data):
        return User(**data)

class Trash:
    def __init__(self, original_user_id, deleted_by, reason=None):
        self.original_user_id = original_user_id
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by = deleted_by
        self.reason = reason

    def to_dict(self):
        return {
            "original_user_id": self.original_user_id,
            "deleted_at": self.deleted_at,
            "deleted_by": self.deleted_by,
            "reason": self.reason,
        }

    @staticmethod
    def from_dict(data):
        return Trash(**data)