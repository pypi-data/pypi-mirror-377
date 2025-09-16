import httpx
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from typing import Any, Generator, Generic, Optional, TypeVar


class Authorization(BaseModel):
    scheme: str = Field(..., description="Authorization's scheme")
    credentials: str = Field(..., description="Authorization's credentials")

    @classmethod
    def as_dependency(cls, security: Any, mandatory: bool = True):
        """Create a FastAPI for this Authorization"""
        security = HTTPBearer(auto_error=mandatory)

        def mandatory_dependency(
            token: HTTPAuthorizationCredentials = Security(security),
        ) -> "Authorization":
            return cls(scheme=token.scheme, credentials=token.credentials)

        def optional_dependency(
            token: Optional[HTTPAuthorizationCredentials] = Security(security),
        ) -> Optional["Authorization"]:
            if token is None:
                return None
            return cls(scheme=token.scheme, credentials=token.credentials)

        if mandatory:
            return mandatory_dependency
        else:
            return optional_dependency


OptionalAuthorizationT = TypeVar(
    "OptionalAuthorizationT", bound=Optional[Authorization]
)


class AuthorizationMixin(BaseModel, Generic[OptionalAuthorizationT]):
    authorization: OptionalAuthorizationT = Field(
        ...,
        description="Authorization",
    )


class BearerAuth(httpx.Auth):
    def __init__(self, token: str) -> None:
        self._auth_header = self._build_auth_header(token)

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = self._auth_header
        yield request

    def _build_auth_header(self, token: str) -> str:
        return f"Bearer {token}"
