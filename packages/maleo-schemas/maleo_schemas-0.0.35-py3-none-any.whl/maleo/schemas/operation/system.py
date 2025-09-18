from typing import Generic, Literal, Optional
from maleo.mixins.general import SuccessT
from maleo.security.authentication import AuthenticationT
from maleo.security.authorization import Authorization
from maleo.security.impersonation import Impersonation
from ..contexts.request import RequestContext
from ..error import (
    OptionalErrorT,
    ErrorT,
)
from ..response import ResponseT, ErrorResponseT, SuccessResponseT
from .action.system import SystemOperationAction
from .base import BaseOperation
from .enums import OperationType


class SystemOperation(
    BaseOperation[
        SystemOperationAction,
        None,
        SuccessT,
        OptionalErrorT,
        Optional[RequestContext],
        AuthenticationT,
        Optional[Authorization],
        Optional[Impersonation],
        ResponseT,
        None,
    ],
    Generic[
        SuccessT,
        OptionalErrorT,
        AuthenticationT,
        ResponseT,
    ],
):
    type: OperationType = OperationType.SYSTEM
    resource: None = None
    response_context: None = None


class FailedSystemOperation(
    SystemOperation[Literal[False], ErrorT, AuthenticationT, ErrorResponseT],
    Generic[ErrorT, AuthenticationT, ErrorResponseT],
):
    success: Literal[False] = False


class SuccessfulSystemOperation(
    SystemOperation[Literal[True], None, AuthenticationT, SuccessResponseT],
    Generic[AuthenticationT, SuccessResponseT],
):
    success: Literal[True] = True
    error: None = None
