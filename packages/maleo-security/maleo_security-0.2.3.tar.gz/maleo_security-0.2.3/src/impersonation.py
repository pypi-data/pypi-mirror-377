from enum import StrEnum
from fastapi import status, HTTPException, Request, Header
from pydantic import BaseModel, Field
from typing import Annotated, Callable, Generic, Optional, TypeVar
from maleo.enums.request import Header as HeaderEnum
from maleo.mixins.identity import OrganizationId, UserId
from maleo.types.integer import OptionalInteger


class Source(StrEnum):
    HEADER = "header"
    STATE = "state"


class Impersonation(OrganizationId[OptionalInteger], UserId[int]):
    user_id: int = Field(..., ge=1)
    organization_id: OptionalInteger = Field(None, ge=1)

    @classmethod
    def extract(cls, source: Source, *, request: Request) -> Optional["Impersonation"]:
        if source is Source.HEADER:
            user_id = request.headers.get(HeaderEnum.X_USER_ID, None)
            if user_id is not None:
                user_id = int(user_id)

            organization_id = request.headers.get(HeaderEnum.X_ORGANIZATION_ID, None)
            if organization_id is not None:
                organization_id = int(organization_id)

            if user_id is not None:
                return cls(
                    user_id=user_id,
                    organization_id=organization_id,
                )

            if organization_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization ID must be None if User ID is None",
                )

            return None
        elif source is Source.STATE:
            impersonation = request.state.impersonation
            if not isinstance(impersonation, Impersonation):
                return None
            return impersonation

    @classmethod
    def assign_to_state(cls, request: Request):
        impersonation = cls.extract(Source.HEADER, request=request)
        request.state.impersonation = impersonation

    @classmethod
    def as_dependency(
        cls, source: Optional[Source] = None
    ) -> Callable[..., Optional["Impersonation"]]:
        def dependency(
            request: Request,
            user_id: Annotated[
                OptionalInteger,
                Header(
                    None,
                    alias=HeaderEnum.X_USER_ID.value,
                    description="User ID. (Optional)",
                    ge=1,
                ),
            ],
            organization_id: Annotated[
                OptionalInteger,
                Header(
                    None,
                    alias=HeaderEnum.X_ORGANIZATION_ID.value,
                    description="Organization ID. (Optional)",
                    ge=1,
                ),
            ],
        ) -> Optional["Impersonation"]:
            if source is None:
                if user_id is not None:
                    return cls(
                        user_id=user_id,
                        organization_id=organization_id,
                    )

                if organization_id is not None:
                    raise HTTPException(
                        status_code=400,
                        detail="Organization ID must be None if User ID is None",
                    )

                return None

            return cls.extract(source, request=request)

        return dependency


ImpersonationT = TypeVar("ImpersonationT", bound=Optional[Impersonation])


class ImpersonationMixin(BaseModel, Generic[ImpersonationT]):
    impersonation: ImpersonationT = Field(..., description="Impersonation")
