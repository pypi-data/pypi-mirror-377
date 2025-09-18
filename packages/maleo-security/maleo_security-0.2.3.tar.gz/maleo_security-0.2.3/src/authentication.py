from fastapi import status, HTTPException, Request
from pydantic import BaseModel, Field
from starlette.authentication import (
    AuthCredentials as StarletteCredentials,
    BaseUser as StarletteUser,
)
from typing import Callable, Generic, Literal, Optional, TypeVar
from uuid import UUID
from maleo.types.string import (
    ListOfStrings,
    OptionalListOfStrings,
    OptionalSequenceOfStrings,
)
from maleo.types.uuid import OptionalUUID
from .token import BaseToken


class RequestCredentials(StarletteCredentials):
    def __init__(
        self,
        user_id: OptionalUUID = None,
        organization_id: OptionalUUID = None,
        roles: OptionalSequenceOfStrings = None,
        scopes: OptionalSequenceOfStrings = None,
    ):
        super().__init__(scopes)
        self.user_id = user_id
        self.organization_id = organization_id
        self.roles = [] if roles is None else list(roles)

    @classmethod
    def from_base_token(cls, token: Optional[BaseToken]) -> "RequestCredentials":
        if token is None:
            return cls()
        return cls(
            user_id=token.sub,
            organization_id=token.o,
            roles=token.r,
            scopes=["authenticated", *token.scopes],
        )


class RequestUser(StarletteUser):
    def __init__(
        self, authenticated: bool = False, username: str = "", email: str = ""
    ) -> None:
        self._authenticated = authenticated
        self._username = username
        self._email = email

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    @property
    def display_name(self) -> str:
        return self._username

    @property
    def identity(self) -> str:
        return self._email


UserIdT = TypeVar("UserIdT", bound=OptionalUUID)
OrganizationIdT = TypeVar("OrganizationIdT", bound=OptionalUUID)
RolesT = TypeVar("RolesT", bound=OptionalListOfStrings)
ScopesT = TypeVar("ScopesT", bound=OptionalListOfStrings)


class GenericCredentials(BaseModel, Generic[UserIdT, OrganizationIdT, RolesT, ScopesT]):
    user_id: UserIdT = Field(..., description="User")
    organization_id: OrganizationIdT = Field(..., description="Organization")
    roles: RolesT = Field(..., description="Roles")
    scopes: ScopesT = Field(..., description="Scopes")


CredentialsT = TypeVar("CredentialsT", bound=GenericCredentials)


class CredentialsMixin(BaseModel, Generic[CredentialsT]):
    credentials: CredentialsT = Field(..., description="Credentials")


class BaseCredentials(
    GenericCredentials[
        OptionalUUID,
        OptionalUUID,
        OptionalListOfStrings,
        OptionalListOfStrings,
    ]
):
    pass


class AuthenticatedCredentials(
    GenericCredentials[UUID, OptionalUUID, ListOfStrings, ListOfStrings]
):
    pass


IsAuthenticatedT = TypeVar("IsAuthenticatedT", bound=bool)


class GenericUser(BaseModel, Generic[IsAuthenticatedT]):
    is_authenticated: IsAuthenticatedT = Field(..., description="Authenticated")
    display_name: str = Field("", description="Username")
    identity: str = Field("", description="Email")


UserT = TypeVar("UserT", bound=GenericUser)


class UserMixin(BaseModel, Generic[UserT]):
    user: UserT = Field(..., description="User")


class BaseUser(GenericUser[bool]):
    is_authenticated: bool = Field(..., description="Authenticated")


class AuthenticatedUser(GenericUser[Literal[True]]):
    is_authenticated: Literal[True] = True


class GenericAuthentication(
    UserMixin[UserT], CredentialsMixin[CredentialsT], Generic[CredentialsT, UserT]
):
    @classmethod
    def _validate_request_credentials(cls, request: Request):
        if not isinstance(request.auth, RequestCredentials):
            raise HTTPException(
                status_code=401,
                detail=f"Invalid type of request's credentials: '{type(request.auth)}'",
            )

    @classmethod
    def _validate_request_user(cls, request: Request):
        if not isinstance(request.user, RequestUser):
            raise HTTPException(
                status_code=401,
                detail=f"Invalid type of request's user: '{type(request.user)}'",
            )


AuthenticationT = TypeVar("AuthenticationT", bound=Optional[GenericAuthentication])


class AuthenticationMixin(BaseModel, Generic[AuthenticationT]):
    authentication: AuthenticationT = Field(..., description="Authentication")


class BaseAuthentication(GenericAuthentication[BaseCredentials, BaseUser]):
    @classmethod
    def extract(
        cls,
        request: Request,
        /,
    ) -> "BaseAuthentication":
        try:
            # validate credentials
            cls._validate_request_credentials(request=request)
            credentials = BaseCredentials.model_validate(
                request.auth, from_attributes=True
            )

            # validate user
            cls._validate_request_user(request=request)
            user = BaseUser.model_validate(request.user, from_attributes=True)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unable to validate {cls.__name__}: '{str(e)}'",
            )

        return cls(credentials=credentials, user=user)

    @classmethod
    def as_dependency(cls) -> Callable[..., "BaseAuthentication"]:
        """Create a FastAPI dependency for this authentication."""

        def dependency(request: Request) -> "BaseAuthentication":
            return cls.extract(request)

        return dependency


class AuthenticatedAuthentication(
    GenericAuthentication[AuthenticatedCredentials, AuthenticatedUser]
):
    @classmethod
    def extract(
        cls,
        request: Request,
        /,
    ) -> "AuthenticatedAuthentication":
        try:
            # validate credentials
            cls._validate_request_credentials(request=request)
            credentials = AuthenticatedCredentials.model_validate(
                request.auth, from_attributes=True
            )

            # validate user
            cls._validate_request_user(request=request)
            user = AuthenticatedUser.model_validate(request.user, from_attributes=True)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unable to validate {cls.__name__}: '{str(e)}'",
            )

        return cls(credentials=credentials, user=user)

    @classmethod
    def as_dependency(cls) -> Callable[..., "AuthenticatedAuthentication"]:
        """Create a FastAPI dependency for this authentication."""

        def dependency(request: Request) -> "AuthenticatedAuthentication":
            return cls.extract(request)

        return dependency
