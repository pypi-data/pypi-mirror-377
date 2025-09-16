from typing import Generic
from maleo.mixins.parameter import (
    IdentifierTypeT,
    IdentifierValueT,
    IdentifierTypeValue,
    DateFilters,
    DataStatuses,
    SortColumns,
    Search,
    UseCache,
    StatusUpdateAction,
)
from .pagination import BaseFlexiblePagination, BaseStrictPagination


class ReadSingleParameter(
    DataStatuses,
    UseCache,
    IdentifierTypeValue[IdentifierTypeT, IdentifierValueT],
    Generic[IdentifierTypeT, IdentifierValueT],
):
    pass


class BaseReadMultipleParameter(
    SortColumns,
    Search,
    DataStatuses,
    DateFilters,
    UseCache,
):
    pass


class ReadUnpaginatedMultipleParameter(
    BaseFlexiblePagination,
    BaseReadMultipleParameter,
):
    pass


class ReadPaginatedMultipleParameter(
    BaseStrictPagination,
    BaseReadMultipleParameter,
):
    pass


class StatusUpdateParameter(
    StatusUpdateAction,
    IdentifierTypeValue[IdentifierTypeT, IdentifierValueT],
    Generic[IdentifierTypeT, IdentifierValueT],
):
    pass
