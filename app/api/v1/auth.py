from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.services import get_auth_service, AuthService, RefreshTokenService, get_refresh_token_service
from app.schemas import RegistrationInputSchema, RegistrationOutputSchema, LoginOutputSchema, VerifyOutputSchema, UserSchema, InputRefreshSchema



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")
router = APIRouter(tags=["Регистрация и аутентификация"])


@router.post(
    "/register",
    summary="Регистрация пользователя",
    description="Регистрация пользователя",
    response_model=RegistrationOutputSchema,
    status_code=status.HTTP_201_CREATED
)
async def register(
    user: RegistrationInputSchema,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    user_data = await auth_service.register(**user.model_dump())
    return user_data


@router.post(
    "/login",
    description="Аутентификация пользователя",
    summary="Аутентификация пользователя",
    response_model=LoginOutputSchema
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    user, token, refresh_token = await auth_service.login(login=form_data.username, password=form_data.password)

    user_data = UserSchema.model_validate(user).model_dump()

    return LoginOutputSchema(**user_data, access_token=token, refresh_token=refresh_token)


@router.get(
    "/verify", 
    summary="Подтверждение токена",
    description="Подтверждение токена",
    response_model=VerifyOutputSchema
)
async def verify_token(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user_data = await auth_service.verify(token)
        
    return user_data


@router.post(
    "/refresh",
    summary="Обновление токена",
    description="Обновление токена",
    response_model=LoginOutputSchema
)
async def refresh(
    refresh_data: InputRefreshSchema,
    refresh_service: Annotated[RefreshTokenService, Depends(get_refresh_token_service)]
):
    user, access, refresh = await refresh_service.refresh(refresh_data.refresh_token)
    user_data = UserSchema.model_validate(user).model_dump()

    return LoginOutputSchema(**user_data, access_token=access, refresh_token=refresh)
