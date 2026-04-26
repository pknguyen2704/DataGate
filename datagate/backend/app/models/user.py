# Backward-compatibility shim. User model now lives in app.models.auth
from app.models.auth import User, Role, Permission  # noqa