from maleo.mixins.filter import Filters
from maleo.mixins.sort import Sorts
from maleo.mixins.parameter import (
    Search,
    UseCache,
)
from maleo.mixins.status import DataStatuses
from .operation.action import StatusUpdateAction
from .pagination import BaseFlexiblePagination, BaseStrictPagination


class ReadSingleQuery(
    DataStatuses,
    UseCache,
):
    pass


class BaseReadMultipleQuery(
    Sorts,
    Search,
    DataStatuses,
    Filters,
    UseCache,
):
    pass


class ReadUnpaginatedMultipleQuery(
    BaseFlexiblePagination,
    BaseReadMultipleQuery,
):
    pass


class ReadPaginatedMultipleQuery(
    BaseStrictPagination,
    BaseReadMultipleQuery,
):
    pass


class StatusUpdateBody(StatusUpdateAction):
    pass
