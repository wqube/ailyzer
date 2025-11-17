from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from pydantic import BaseModel
# from backend.app.schemas import user
from schemas.user import UserSchema
from auth import utils as auth_utils
# from demo_auth.healper import create_access_token, create_refresh_token
from api.routers.demo_auth.healper import create_access_token, create_refresh_token, TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE


# Получаем токен, который приходит в запросе
http_bearer = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/demo_auth/jwt/login/")

# Модель запроса
class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


router = APIRouter(prefix="/jwt", tags=["JWT"], dependencies=[Depends(http_bearer)])


john = UserSchema(
    username="john",
    password=auth_utils.hash_password("qwerty"),
    email="john@gmail.com"
)

sam = UserSchema(
    username="sam",
    password=auth_utils.hash_password("secret"),
)

users_db: dict[str, UserSchema] = {
    john.username: john,
    sam.username: sam,
}


# Типо проверка валидности входа пользователя
def validate_jwt_user(
        username: str = Form(),
        password: str = Form()
):
    unauth_exception = HTTPException(
        status_code=401,
        detail="invalid username or password",
    )

    # gpt добавил
    user = users_db.get(username)
    # #####

    if not user:
        raise unauth_exception
    
    if not (auth_utils.validate_password(password=password, hashed_password=user.password)):
        raise unauth_exception
    
    if not user.active:
        raise HTTPException(
            status_code=403,
            detail="User not active"
        )
    return user


# Получаем полезную нагрузку, какие-то данные из тела токена, тут же проверяем токен на валидность (decode_jwt)
def get_current_token_payload(
        token: str = Depends(oauth2_scheme)
    ) -> dict:
    # token = credentials.credentials
    try:
        payload = auth_utils.decode_jwt(token=token)
    except InvalidTokenError as exp:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token error: {exp}"
        )
    return payload 


def validate_token_type(
        payload: dict,
        token_type: str
) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=401,
        detail=f"Invalid token type {token_type} expected {REFRESH_TOKEN_TYPE}"
    )


def get_user_by_token_sub(payload: dict) -> UserSchema:
    username: str | None = payload.get("sub")
    if user := users_db.get(username): # type: ignore
        return user
    raise HTTPException(
        status_code=403,
        detail="user not found"
    )


# Находим пользователя, сначала находим его username в токене, берем оттуда 
# subject(тему, то есть о ком идет речь), далее вытаскиваем user из базы данных, 
# если нашли, то возвращаем, если нет, то выкидываем исключени
def get_current_auth_user(
        payload: dict = Depends(get_current_token_payload)
    ) -> UserSchema:
    validate_token_type(payload=payload, token_type=ACCESS_TOKEN_TYPE)
    return get_user_by_token_sub(payload)


def get_current_auth_user_for_refresh(
        payload: dict = Depends(get_current_token_payload)
    ) -> UserSchema:
    validate_token_type(payload=payload, token_type=REFRESH_TOKEN_TYPE)
    return get_user_by_token_sub(payload)


# Если пользователь активен, то отдаем его, если нет, то выкидываем исключение
def get_current_active_auth_user(user: UserSchema = Depends(get_current_auth_user)):
    if user.active:
        return user
    raise HTTPException(
        status_code=403,
        detail="User is inactive"
    )


# Успешно залогиненые пользователи
@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(user: UserSchema = Depends(validate_jwt_user)):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


# Выпуск access токена на основе refresh токена
@router.post("/refresh/", response_model=TokenInfo, response_model_exclude_none=True)
def auth_refresh_jwt(user: UserSchema = Depends(get_current_auth_user_for_refresh)):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


# Получает текущего пользователя current_active_user
@router.get("/user_me/")
def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    iat = payload.get("iat")
    return  {
        "username": user.username,
        "email": user.email,
        "logget_in_at": iat,
    }
