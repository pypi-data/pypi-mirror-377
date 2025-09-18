from collections.abc import Iterable, Sequence
from Crypto.PublicKey.RSA import RsaKey
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field, model_validator
from typing import Generic, Optional, Self, Tuple, TypeVar, Union, overload
from uuid import UUID
from maleo.crypto.token import decode, encode
from maleo.enums.expiration import Expiration
from maleo.types.datetime import OptionalDatetime
from maleo.types.misc import BytesOrString, StringOrStringEnum
from maleo.types.string import ListOfStrings, OptionalString
from maleo.types.uuid import OptionalUUID
from .enums import Domain


class Claim(BaseModel):
    iss: OptionalString = Field(None, description="Issuer")
    sub: UUID = Field(..., description="Subject")
    aud: OptionalString = Field(None, description="Audience")
    exp: int = Field(..., description="Expired at")
    iat: int = Field(..., description="Issued at")

    @classmethod
    def new_timestamp(
        cls, iat_dt: OptionalDatetime = None, exp_in: Expiration = Expiration.EXP_15MN
    ) -> Tuple[int, int]:
        if iat_dt is None:
            iat_dt = datetime.now(tz=timezone.utc)
        exp_dt = iat_dt + timedelta(seconds=exp_in.value)
        return int(iat_dt.timestamp()), int(exp_dt.timestamp())


DomainT = TypeVar("DomainT", bound=StringOrStringEnum)
OrganizationT = TypeVar("OrganizationT", bound=OptionalUUID)


class Credential(BaseModel, Generic[DomainT, OrganizationT]):
    d: DomainT = Field(..., description="Domain")
    o: OrganizationT = Field(..., description="Organization")
    r: ListOfStrings = Field(..., min_length=1, description="Roles")


class GenericToken(
    Credential[DomainT, OrganizationT],
    Claim,
    Generic[DomainT, OrganizationT],
):
    @classmethod
    def from_string(
        cls,
        token: str,
        key: Union[RsaKey, BytesOrString],
        audience: str | Iterable[str] | None = None,
        subject: OptionalString = None,
        issuer: str | Sequence[str] | None = None,
        leeway: float | timedelta = 0,
    ) -> "GenericToken[DomainT, OrganizationT]":
        obj = decode(token, key, audience, subject, issuer, leeway)
        return cls.model_validate(obj)

    @classmethod
    def new(
        cls,
        *,
        sub: UUID,
        d: DomainT,
        o: OrganizationT,
        r: ListOfStrings,
        iss: OptionalString = None,
        aud: OptionalString = None,
        iat_dt: OptionalDatetime = None,
        exp_in: Expiration = Expiration.EXP_15MN,
    ) -> "GenericToken[DomainT, OrganizationT]":
        iat, exp = cls.new_timestamp(iat_dt, exp_in)
        return cls(iss=iss, sub=sub, aud=aud, exp=exp, iat=iat, d=d, o=o, r=r)

    @property
    def scopes(self) -> ListOfStrings:
        return [f"{str(self.d)}:{str(r)}" for r in self.r]

    @model_validator(mode="after")
    def validate_credential(self) -> Self:
        return self

    @overload
    def to_string(
        self,
        key: RsaKey,
    ) -> str: ...
    @overload
    def to_string(
        self,
        key: BytesOrString,
        *,
        password: OptionalString = None,
    ) -> str: ...
    def to_string(
        self,
        key: Union[RsaKey, BytesOrString],
        *,
        password: OptionalString = None,
    ) -> str:
        if isinstance(key, RsaKey):
            return encode(
                payload=self.model_dump(mode="json", exclude_none=True),
                key=key,
            )
        else:
            return encode(
                payload=self.model_dump(mode="json", exclude_none=True),
                key=key,
                password=password,
            )


GenericTokenT = TypeVar("GenericTokenT", bound=Optional[GenericToken])


class BaseToken(GenericToken[StringOrStringEnum, OptionalUUID]):
    @classmethod
    def from_string(
        cls,
        token: str,
        key: Union[RsaKey, BytesOrString],
        audience: str | Iterable[str] | None = None,
        subject: OptionalString = None,
        issuer: str | Sequence[str] | None = None,
        leeway: float | timedelta = 0,
    ) -> "BaseToken":
        obj = decode(token, key, audience, subject, issuer, leeway)
        return cls.model_validate(obj)

    @classmethod
    def new(
        cls,
        *,
        sub: UUID,
        d: StringOrStringEnum,
        o: OptionalUUID,
        r: ListOfStrings,
        iss: OptionalString = None,
        aud: OptionalString = None,
        iat_dt: OptionalDatetime = None,
        exp_in: Expiration = Expiration.EXP_15MN,
    ) -> "BaseToken":
        iat, exp = cls.new_timestamp(iat_dt, exp_in)
        return cls(iss=iss, sub=sub, aud=aud, exp=exp, iat=iat, d=d, o=o, r=r)

    @overload
    def to_string(
        self,
        key: RsaKey,
    ) -> str: ...
    @overload
    def to_string(
        self,
        key: BytesOrString,
        *,
        password: OptionalString = None,
    ) -> str: ...
    def to_string(
        self,
        key: Union[RsaKey, BytesOrString],
        *,
        password: OptionalString = None,
    ) -> str:
        if isinstance(key, RsaKey):
            return encode(
                payload=self.model_dump(mode="json", exclude_none=True),
                key=key,
            )
        else:
            return encode(
                payload=self.model_dump(mode="json", exclude_none=True),
                key=key,
                password=password,
            )


class DomainToken(GenericToken[Domain, OrganizationT], Generic[OrganizationT]):
    @classmethod
    def new(
        cls,
        *,
        sub: UUID,
        d: Domain,
        o: OrganizationT,
        r: ListOfStrings,
        iss: OptionalString = None,
        aud: OptionalString = None,
        iat_dt: OptionalDatetime = None,
        exp_in: Expiration = Expiration.EXP_15MN,
    ) -> "DomainToken[OrganizationT]":
        iat, exp = cls.new_timestamp(iat_dt, exp_in)
        return cls(iss=iss, sub=sub, aud=aud, exp=exp, iat=iat, d=d, o=o, r=r)


DomainTokenT = TypeVar("DomainTokenT", bound=DomainToken)


class OrganizationToken(DomainToken[UUID]):
    d: Domain = Domain.ORGANIZATION

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if self.d is not Domain.ORGANIZATION:
            raise ValueError(f"Value of 'd' claim must be {Domain.ORGANIZATION}")
        if not isinstance(self.o, UUID):
            raise ValueError(f"Value of 'o' claim must be an UUID. Value: {self.o}")
        return self

    @classmethod
    def new(
        cls,
        *,
        sub: UUID,
        d: Domain = Domain.ORGANIZATION,
        o: UUID,
        r: ListOfStrings,
        iss: OptionalString = None,
        aud: OptionalString = None,
        iat_dt: OptionalDatetime = None,
        exp_in: Expiration = Expiration.EXP_15MN,
    ) -> "OrganizationToken":
        iat, exp = cls.new_timestamp(iat_dt, exp_in)
        return cls(iss=iss, sub=sub, aud=aud, exp=exp, iat=iat, o=o, r=r)

    @classmethod
    def from_other_token(
        cls,
        token: Union[
            GenericToken[DomainT, OrganizationT],
            BaseToken,
            DomainToken[OrganizationT],
        ],
    ) -> "OrganizationToken":
        if not isinstance(token.d, Domain):
            raise TypeError(f"Invalid type for 'd' claim: {type(token.d)}")
        if token.d is not Domain.ORGANIZATION:
            raise ValueError(f"Value of 'd' claim must be {Domain.ORGANIZATION}")
        if not isinstance(token.o, UUID):
            raise ValueError(f"Value of 'o' claim must be an UUID. Value: {token.o}")
        return cls.model_validate(token.model_dump(mode="json"))


class SystemToken(DomainToken[None]):
    d: Domain = Domain.SYSTEM
    o: None = None

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if self.d is not Domain.SYSTEM:
            raise ValueError(f"Value of 'd' claim must be {Domain.SYSTEM}")
        if self.o is not None:
            raise ValueError(f"Value of 'o' claim must be None. Value: {self.o}")
        return self

    @classmethod
    def new(
        cls,
        *,
        sub: UUID,
        d: Domain = Domain.SYSTEM,
        o: None = None,
        r: ListOfStrings,
        iss: OptionalString = None,
        aud: OptionalString = None,
        iat_dt: OptionalDatetime = None,
        exp_in: Expiration = Expiration.EXP_15MN,
    ) -> "SystemToken":
        iat, exp = cls.new_timestamp(iat_dt, exp_in)
        return cls(iss=iss, sub=sub, aud=aud, exp=exp, iat=iat, r=r)

    @classmethod
    def from_other_token(
        cls,
        token: Union[
            GenericToken[DomainT, OrganizationT],
            BaseToken,
            DomainToken[OrganizationT],
        ],
    ) -> "SystemToken":
        if not isinstance(token.d, Domain):
            raise TypeError(f"Invalid type for 'd' claim: {type(token.d)}")
        if token.d is not Domain.SYSTEM:
            raise ValueError(f"Value of 'd' claim must be {Domain.SYSTEM}")
        if token.o is not None:
            raise ValueError(f"Value of 'o' claim must be an None. Value: {token.o}")
        return cls.model_validate(token.model_dump(mode="json"))
