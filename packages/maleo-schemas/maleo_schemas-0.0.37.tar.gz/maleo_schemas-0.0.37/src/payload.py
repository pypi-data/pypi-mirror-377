from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from maleo.mixins.general import Other
from .data import DataPair, AnyDataT, DataMixin, ModelDataT
from .pagination import OptionalPaginationT, PaginationT, PaginationMixin
from .metadata import MetadataMixin, MetadataT


class Payload(
    Other,
    MetadataMixin[MetadataT],
    PaginationMixin[OptionalPaginationT],
    DataMixin[AnyDataT],
    BaseModel,
    Generic[AnyDataT, OptionalPaginationT, MetadataT],
):
    pass


PayloadT = TypeVar("PayloadT", bound=Payload)


class PayloadMixin(BaseModel, Generic[PayloadT]):
    payload: PayloadT = Field(..., description="Payloaf")


class NoDataPayload(
    Payload[None, None, MetadataT],
    Generic[MetadataT],
):
    data: None = None
    pagination: None = None


class SingleDataPayload(
    Payload[ModelDataT, None, MetadataT],
    Generic[ModelDataT, MetadataT],
):
    pagination: None = None


class CreateSingleDataPayload(
    Payload[DataPair[None, ModelDataT], None, MetadataT],
    Generic[ModelDataT, MetadataT],
):
    pass


class ReadSingleDataPayload(
    Payload[DataPair[ModelDataT, None], None, MetadataT],
    Generic[ModelDataT, MetadataT],
):
    pass


class UpdateSingleDataPayload(
    Payload[DataPair[ModelDataT, ModelDataT], None, MetadataT],
    Generic[ModelDataT, MetadataT],
):
    pass


class DeleteSingleDataPayload(
    Payload[DataPair[ModelDataT, None], None, MetadataT],
    Generic[ModelDataT, MetadataT],
):
    pass


class OptionalSingleDataPayload(
    Payload[Optional[ModelDataT], None, MetadataT],
    Generic[ModelDataT, MetadataT],
):
    pagination: None = None


class MultipleDataPayload(
    Payload[List[ModelDataT], PaginationT, MetadataT],
    Generic[ModelDataT, PaginationT, MetadataT],
):
    pass


class CreateMultipleDataPayload(
    Payload[DataPair[None, List[ModelDataT]], PaginationT, MetadataT],
    Generic[ModelDataT, PaginationT, MetadataT],
):
    pass


class ReadMultipleDataPayload(
    Payload[DataPair[List[ModelDataT], None], PaginationT, MetadataT],
    Generic[ModelDataT, PaginationT, MetadataT],
):
    pass


class UpdateMultipleDataPayload(
    Payload[DataPair[List[ModelDataT], List[ModelDataT]], PaginationT, MetadataT],
    Generic[ModelDataT, PaginationT, MetadataT],
):
    pass


class DeleteMultipleDataPayload(
    Payload[DataPair[List[ModelDataT], None], PaginationT, MetadataT],
    Generic[ModelDataT, PaginationT, MetadataT],
):
    pass


class OptionalMultipleDataPayload(
    Payload[Optional[List[ModelDataT]], PaginationT, MetadataT],
    Generic[ModelDataT, PaginationT, MetadataT],
):
    pass
