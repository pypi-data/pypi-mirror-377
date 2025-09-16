from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from .data import DataPair, AnyDataT, DataMixin, ModelDataT
from .pagination import OptionalPaginationT, PaginationT, PaginationMixin
from .metadata import MetadataMixin, OptionalMetadataT
from maleo.mixins.general import Other


class Payload(
    Other,
    MetadataMixin[OptionalMetadataT],
    PaginationMixin[OptionalPaginationT],
    DataMixin[AnyDataT],
    BaseModel,
    Generic[AnyDataT, OptionalPaginationT, OptionalMetadataT],
):
    pass


PayloadT = TypeVar("PayloadT", bound=Payload)


class PayloadMixin(BaseModel, Generic[PayloadT]):
    payload: PayloadT = Field(..., description="Payloaf")


class NoDataPayload(
    Payload[None, None, OptionalMetadataT],
    Generic[OptionalMetadataT],
):
    data: None = None
    pagination: None = None


class SingleDataPayload(
    Payload[ModelDataT, None, OptionalMetadataT],
    Generic[ModelDataT, OptionalMetadataT],
):
    pagination: None = None


class CreateSingleDataPayload(
    Payload[DataPair[None, ModelDataT], None, OptionalMetadataT],
    Generic[ModelDataT, OptionalMetadataT],
):
    pass


class ReadSingleDataPayload(
    Payload[DataPair[ModelDataT, None], None, OptionalMetadataT],
    Generic[ModelDataT, OptionalMetadataT],
):
    pass


class UpdateSingleDataPayload(
    Payload[DataPair[ModelDataT, ModelDataT], None, OptionalMetadataT],
    Generic[ModelDataT, OptionalMetadataT],
):
    pass


class DeleteSingleDataPayload(
    Payload[DataPair[ModelDataT, None], None, OptionalMetadataT],
    Generic[ModelDataT, OptionalMetadataT],
):
    pass


class OptionalSingleDataPayload(
    Payload[Optional[ModelDataT], None, OptionalMetadataT],
    Generic[ModelDataT, OptionalMetadataT],
):
    pagination: None = None


class MultipleDataPayload(
    Payload[List[ModelDataT], PaginationT, OptionalMetadataT],
    Generic[ModelDataT, PaginationT, OptionalMetadataT],
):
    pass


class CreateMultipleDataPayload(
    Payload[DataPair[None, List[ModelDataT]], PaginationT, OptionalMetadataT],
    Generic[ModelDataT, PaginationT, OptionalMetadataT],
):
    pass


class ReadMultipleDataPayload(
    Payload[DataPair[List[ModelDataT], None], PaginationT, OptionalMetadataT],
    Generic[ModelDataT, PaginationT, OptionalMetadataT],
):
    pass


class UpdateMultipleDataPayload(
    Payload[
        DataPair[List[ModelDataT], List[ModelDataT]], PaginationT, OptionalMetadataT
    ],
    Generic[ModelDataT, PaginationT, OptionalMetadataT],
):
    pass


class DeleteMultipleDataPayload(
    Payload[DataPair[List[ModelDataT], None], PaginationT, OptionalMetadataT],
    Generic[ModelDataT, PaginationT, OptionalMetadataT],
):
    pass


class OptionalMultipleDataPayload(
    Payload[Optional[List[ModelDataT]], PaginationT, OptionalMetadataT],
    Generic[ModelDataT, PaginationT, OptionalMetadataT],
):
    pass
