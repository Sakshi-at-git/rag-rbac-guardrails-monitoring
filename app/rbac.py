from dataclasses import dataclass
from typing import Callable, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth import decode_access_token, hash_password, verify_password


@dataclass
class User:
    username: str
    role: str


security = HTTPBearer()

_raw_users = {
    "admin": {"password": "admin123", "role": "admin"},
    "editor": {"password": "editor123", "role": "editor"},
    "viewer": {"password": "viewer123", "role": "viewer"},
}

USERS: Dict[str, Dict[str, str]] = {
    name: {"password_hash": hash_password(data["password"]), "role": data["role"]}
    for name, data in _raw_users.items()
}


def authenticate_user(username: str, password: str) -> User | None:
    user = USERS.get(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return User(username=username, role=user["role"])


def current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    payload = decode_access_token(credentials.credentials)
    username = payload.get("sub")
    role = payload.get("role")
    if not username or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return User(username=username, role=role)


def require_roles(*allowed_roles: str) -> Callable[[User], User]:
    def role_dependency(user: User = Depends(current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' not allowed",
            )
        return user

    return role_dependency
