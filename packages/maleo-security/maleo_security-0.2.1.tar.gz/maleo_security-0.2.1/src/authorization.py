import httpx
from enum import StrEnum
from fastapi import status, HTTPException, Request, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from typing import (
    Annotated,
    Callable,
    Generator,
    Generic,
    Literal,
    Optional,
    TypeVar,
    Union,
    overload,
)
from maleo.enums.request import Header
from maleo.types.string import OptionalString


class Scheme(StrEnum):
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"


class Source(StrEnum):
    HEADER = "header"
    STATE = "state"


class Authorization(BaseModel):
    scheme: Scheme = Field(..., description="Authorization's scheme")
    credentials: str = Field(..., description="Authorization's credentials")

    @overload
    @classmethod
    def extract(
        cls, source: Source, *, request: Request, auto_error: Literal[False]
    ) -> Optional["Authorization"]: ...
    @overload
    @classmethod
    def extract(
        cls, source: Source, *, request: Request, auto_error: Literal[True] = True
    ) -> "Authorization": ...
    @classmethod
    def extract(
        cls, source: Source, *, request: Request, auto_error: bool = True
    ) -> Optional["Authorization"]:
        if source is Source.HEADER:
            # Extract authorization from Authorization header
            token = request.headers.get(Header.AUTHORIZATION.value, "")
            scheme, _, credentials = token.partition(" ")
            if token and scheme and credentials and scheme.lower() == "bearer":
                return cls(scheme=Scheme.BEARER_TOKEN, credentials=credentials)
            # Extract authorization from X-API-Key Header
            api_key = request.headers.get(Header.X_API_KEY)
            if api_key is not None:
                return cls(scheme=Scheme.API_KEY, credentials=api_key)
            if auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or unable to determine authorization",
                )
            return None
        elif source is Source.STATE:
            authorization = request.state.authorization
            if not isinstance(authorization, Authorization):
                if auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid type of authorization state: {type(authorization)}",
                    )
                else:
                    return None
            return authorization

    @classmethod
    def assign_to_state(cls, request: Request):
        authorization = cls.extract(Source.HEADER, request=request, auto_error=False)
        request.state.authorization = authorization

    @overload
    @classmethod
    def as_dependency(
        cls, auto_error: Literal[False]
    ) -> Callable[..., Optional["Authorization"]]: ...
    @overload
    @classmethod
    def as_dependency(
        cls, auto_error: Literal[True] = True
    ) -> Callable[..., "Authorization"]: ...
    @classmethod
    def as_dependency(cls, auto_error: bool = True) -> Union[
        Callable[..., Optional["Authorization"]],
        Callable[..., "Authorization"],
    ]:
        def dependency(
            request: Request,
            bearer: Annotated[
                Optional[HTTPAuthorizationCredentials],
                Security(HTTPBearer(auto_error=False)),
            ],
            api_key: Annotated[
                OptionalString,
                Security(APIKeyHeader(name=Header.X_API_KEY.value, auto_error=False)),
            ],
        ) -> Optional["Authorization"]:
            from_state = cls.extract(
                Source.STATE, request=request, auto_error=auto_error
            )
            if from_state is not None:
                return from_state
            from_header = cls.extract(
                Source.HEADER, request=request, auto_error=auto_error
            )
            if from_header is not None:
                return from_header
            if bearer is not None:
                return cls(scheme=Scheme.BEARER_TOKEN, credentials=bearer.credentials)
            if api_key is not None:
                return cls(scheme=Scheme.API_KEY, credentials=api_key)
            if auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or unable to determine authorization",
                )
            return None

        return dependency


AuthorizationT = TypeVar("AuthorizationT", bound=Optional[Authorization])


class AuthorizationMixin(BaseModel, Generic[AuthorizationT]):
    authorization: AuthorizationT = Field(
        ...,
        description="Authorization",
    )


class APIKeyAuth(httpx.Auth):
    def __init__(self, api_key: str) -> None:
        self._auth_header = self._build_auth_header(api_key)

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers[Header.X_API_KEY.value] = self._auth_header
        yield request

    def _build_auth_header(self, api_key: str) -> str:
        return api_key


class BearerAuth(httpx.Auth):
    def __init__(self, token: str) -> None:
        self._auth_header = self._build_auth_header(token)

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers[Header.AUTHORIZATION] = self._auth_header
        yield request

    def _build_auth_header(self, token: str) -> str:
        return f"Bearer {token}"


@overload
def generate_httpx_auth(
    scheme: Literal[Scheme.API_KEY], credentials: str
) -> APIKeyAuth: ...
@overload
def generate_httpx_auth(
    scheme: Literal[Scheme.BEARER_TOKEN], credentials: str
) -> BearerAuth: ...
def generate_httpx_auth(scheme: Scheme, credentials: str) -> Union[
    APIKeyAuth,
    BearerAuth,
]:
    if scheme is Scheme.API_KEY:
        return APIKeyAuth(api_key=credentials)
    elif scheme is Scheme.BEARER_TOKEN:
        return BearerAuth(token=credentials)
