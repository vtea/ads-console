"""Server-side session cookies, argon2 password hashing, and role checks."""

from __future__ import annotations

from typing import Callable

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, Request, status
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from ..db.models import User

SESSION_COOKIE = "claude_ads_session"
CSRF_HEADER = "x-csrf-token"
SESSION_MAX_AGE = 12 * 60 * 60
ROLES = ("admin", "operator", "approver")

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


class SessionSigner:
    def __init__(self, secret: str) -> None:
        self._serializer = URLSafeTimedSerializer(secret, salt="claude-ads-session")

    def issue(self, user_id: int, csrf: str) -> str:
        return self._serializer.dumps({"uid": user_id, "csrf": csrf})

    def read(self, token: str) -> dict | None:
        try:
            return self._serializer.loads(token, max_age=SESSION_MAX_AGE)
        except BadSignature:
            return None


def get_db(request: Request) -> Session:
    factory = request.app.state.session_factory
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(SESSION_COOKIE)
    payload = request.app.state.signer.read(token) if token else None
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "未登录或会话已过期")
    user = db.get(User, int(payload["uid"]))
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "账户不可用")
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        header = request.headers.get(CSRF_HEADER)
        if not header or header != payload.get("csrf"):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "CSRF 校验失败")
    request.state.csrf = payload.get("csrf")
    return user


def require_roles(*roles: str) -> Callable[[User], User]:
    def dependency(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"需要角色：{', '.join(roles)}")
        return user

    return dependency
