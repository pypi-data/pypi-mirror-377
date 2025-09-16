from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar
from maleo.mixins.general import OrganizationId, UserId
from maleo.types.base.integer import OptionalInteger


class Impersonation(UserId[int], OrganizationId[OptionalInteger]):
    pass


OptionalImpersonationT = TypeVar(
    "OptionalImpersonationT", bound=Optional[Impersonation]
)


class ImpersonationMixin(BaseModel, Generic[OptionalImpersonationT]):
    impersonation: OptionalImpersonationT = Field(..., description="Impersonation")
