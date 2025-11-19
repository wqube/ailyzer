import secrets
from time import time
import uuid
from fastapi import APIRouter, Cookie, Depends, HTTPException, Header, Response
from typing import Annotated
from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter(prefix="/demo_auth", tags=["Demo Auth"])

security = HTTPBasic()

# Базовая аутентификация (Base64)
@router.get("/basic-auth/")
def demo_basic_auth_credentials(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    return {
        "message": "hello",
        "username": credentials.username,
        "password": credentials.password,
    }

# временно
usernames_to_password = {
    "admin": "admin",
    "john": "password",
}

static_auth_token_to_username = {
    "jfkldsjflkdsjflksdajoiasdj": "admin",
    "dfshjkhdsaslfjldsakjfiofsa": "john",
}


def get_username_by_static_auth_token(static_token: str = Header(alias="x-auth-token")) -> str:
    if static_token not in static_auth_token_to_username:
        raise HTTPException(
            status_code=401,
            detail="token_invalid",
        )
    
    return static_auth_token_to_username[static_token]


def get_auth_user_username (credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    unauthed_exeption = HTTPException(
        status_code=401,
        detail="Invalid username or password",
        # Для браузера, чтобы он понял, с какой мы работаем аутентификацией
        headers={"WWW-Authenticate": "Basic"}
    )

    # correct_password = usernames_to_password.get(credentials.username)
    # if not correct_password or not secrets.compare_digest(
    #     credentials.password.encode(), correct_password.encode()
    # ):
    #     raise unauthed_exeption
    
    if credentials.username not in usernames_to_password:
        raise unauthed_exeption
    
    correct_password = usernames_to_password.get(credentials.username)
    
    if not secrets.compare_digest(credentials.password.encode("utf-8"), correct_password.encode("utf-8")): # type: ignore
        raise unauthed_exeption
    
    return credentials.username


# авторизация через http запрос (так же как и Base Auth)
@router.get("/some-http-username/")
def demo_auth_some_http_header(username: str = Depends(get_username_by_static_auth_token)):
    return {
        "message": f"hello, {username}",
        "username": username,
    }


# Временное хранилище cookie для пользователей
COOKIES: dict[str, dict] = {}
COOKIE_SESSION_ID_KEY = "web-app-cookie-session-id"


def generate_session_id() -> str:
    return uuid.uuid4().hex


def get_session_data(session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY)) -> dict:
    if session_id not in COOKIES:
        raise HTTPException(
            status_code=401,
            detail="not authenticated",
        )
    return COOKIES[session_id]


# авторизация через coockie (cookie auth)
@router.post("/login-cookie/")
def demo_auth_login_cookie(
    responce: Response, 
    auth_username: str = Depends(get_username_by_static_auth_token)
):
    session_id = generate_session_id()

    COOKIES[session_id] = {
        "username": auth_username,
        "login_at": int(time()),
    }

    responce.set_cookie(COOKIE_SESSION_ID_KEY, session_id)

    return {
        "result": "ok"
    }


@router.get("/check_cookie")
def demo_auth_check_cookie(user_session_data: dict = Depends(get_session_data)):
    username = user_session_data["username"]
    return {
        "message": f"hello, {username}",
        **user_session_data
    }

@router.get("/logout_cookie")
def demo_logout_cookiee(
    responce: Response,
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
    user_session_data: dict = Depends(get_session_data)
):
    COOKIES.pop(session_id)
    responce.delete_cookie(COOKIE_SESSION_ID_KEY)
    username = user_session_data["username"]
    return {
        "message": f"goodbye, {username}",
        **user_session_data
    }