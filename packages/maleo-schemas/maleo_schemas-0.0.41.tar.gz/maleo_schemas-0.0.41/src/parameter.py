from typing import Generic
from maleo.mixins.filter import DateFilters
from maleo.mixins.identity import (
    IdentifierTypeT,
    IdentifierValueT,
    IdentifierTypeValue,
)
from maleo.mixins.parameter import (
    Search,
    UseCache,
)
from maleo.mixins.sort import SortColumns
from maleo.mixins.status import DataStatuses
from .operation.action import StatusUpdateAction
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
