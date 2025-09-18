from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID


class MaleoCredentials(BaseModel):
    id: int = Field(..., description="ID")
    uuid: UUID = Field(..., description="UUID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email")
    password: str = Field(..., description="Password")


class Credentials(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    google: ServiceAccountCredentials = Field(..., description="Google credentials")
    maleo: MaleoCredentials = Field(..., description="Maleo credentials")
