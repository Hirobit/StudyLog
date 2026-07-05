import os
from datetime import datetime, timedelta, timezone
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7  # 7日間有効


def verify_google_id_token(token: str) -> dict:
    """
    フロントから送られてきたGoogleのIDトークンを検証し、
    ユーザー情報（google_id, email, name）を返す。
    不正・改ざん・期限切れのトークンの場合は例外を投げる。
    """
    idinfo = id_token.verify_oauth2_token(
        token, google_requests.Request(), GOOGLE_CLIENT_ID
    )

    if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
        raise ValueError("Invalid issuer")

    return {
        "google_id": idinfo["sub"],
        "email": idinfo["email"],
        "name": idinfo.get("name"),
    }


def create_access_token(user_id: str) -> str:
    """
    StudyLog独自のJWTを発行する。中身はuser_id（UUID文字列）と有効期限のみ。
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    """
    StudyLogのJWTを検証し、user_id（文字列）を返す。
    無効・改ざん・期限切れの場合は例外を投げる。
    """
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    return payload["sub"]