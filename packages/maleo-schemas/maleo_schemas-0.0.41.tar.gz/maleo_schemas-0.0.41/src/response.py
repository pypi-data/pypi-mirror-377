from pydantic import BaseModel, Field
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Literal,
    Mapping,
    Optional,
    Type,
    TypeVar,
    Union,
)
from maleo.mixins.general import SuccessT, Success, CodeT, Descriptor
from maleo.types.dict import StringToAnyDict
from maleo.types.string import OptionalString
from .data import DataPair, AnyDataT, ModelDataT
from .error.descriptor import (
    ErrorDescriptor,
    BadRequestErrorDescriptor,
    UnauthorizedErrorDescriptor,
    ForbiddenErrorDescriptor,
    NotFoundErrorDescriptor,
    MethodNotAllowedErrorDescriptor,
    ConflictErrorDescriptor,
    UnprocessableEntityErrorDescriptor,
    TooManyRequestsErrorDescriptor,
    InternalServerErrorDescriptor,
    DatabaseErrorDescriptor,
    NotImplementedErrorDescriptor,
    BadGatewayErrorDescriptor,
    ServiceUnavailableErrorDescriptor,
)
from .error.enums import Code as ErrorCode
from .metadata import MetadataT
from .pagination import OptionalPaginationT, PaginationT
from .payload import (
    Payload,
    NoDataPayload,
    SingleDataPayload,
    CreateSingleDataPayload,
    ReadSingleDataPayload,
    UpdateSingleDataPayload,
    DeleteSingleDataPayload,
    OptionalSingleDataPayload,
    MultipleDataPayload,
    CreateMultipleDataPayload,
    ReadMultipleDataPayload,
    UpdateMultipleDataPayload,
    DeleteMultipleDataPayload,
    OptionalMultipleDataPayload,
)
from .success.descriptor import (
    SuccessDescriptor,
    AnyDataSuccessDescriptor,
    NoDataSuccessDescriptor,
    SingleDataSuccessDescriptor,
    OptionalSingleDataSuccessDescriptor,
    CreateSingleDataSuccessDescriptor,
    ReadSingleDataSuccessDescriptor,
    UpdateSingleDataSuccessDescriptor,
    DeleteSingleDataSuccessDescriptor,
    MultipleDataSuccessDescriptor,
    OptionalMultipleDataSuccessDescriptor,
    CreateMultipleDataSuccessDescriptor,
    ReadMultipleDataSuccessDescriptor,
    UpdateMultipleDataSuccessDescriptor,
    DeleteMultipleDataSuccessDescriptor,
)
from .success.enums import Code as SuccessCode


class Response(
    Payload[AnyDataT, OptionalPaginationT, MetadataT],
    Descriptor[CodeT],
    Success[SuccessT],
    BaseModel,
    Generic[SuccessT, CodeT, AnyDataT, OptionalPaginationT, MetadataT],
):
    pass


ResponseT = TypeVar("ResponseT", bound=Response)


class ResponseMixin(BaseModel, Generic[ResponseT]):
    response: ResponseT = Field(..., description="Response")


# Failure Response
class ErrorResponse(
    NoDataPayload[None],
    ErrorDescriptor,
    Response[Literal[False], ErrorCode, None, None, None],
):
    success: Literal[False] = False
    data: None = None
    pagination: None = None
    metadata: None = None
    other: Any = "Please try again later or contact administrator"


ErrorResponseT = TypeVar("ErrorResponseT", bound=ErrorResponse)


class BadRequestResponse(
    BadRequestErrorDescriptor,
    ErrorResponse,
):
    pass


class UnauthorizedResponse(
    UnauthorizedErrorDescriptor,
    ErrorResponse,
):
    pass


class ForbiddenResponse(
    ForbiddenErrorDescriptor,
    ErrorResponse,
):
    pass


class NotFoundResponse(
    NotFoundErrorDescriptor,
    ErrorResponse,
):
    pass


class MethodNotAllowedResponse(
    MethodNotAllowedErrorDescriptor,
    ErrorResponse,
):
    pass


class ConflictResponse(
    ConflictErrorDescriptor,
    ErrorResponse,
):
    pass


class UnprocessableEntityResponse(
    UnprocessableEntityErrorDescriptor,
    ErrorResponse,
):
    pass


class TooManyRequestsResponse(
    TooManyRequestsErrorDescriptor,
    ErrorResponse,
):
    pass


class InternalServerErrorResponse(
    InternalServerErrorDescriptor,
    ErrorResponse,
):
    pass


class DatabaseErrorResponse(
    DatabaseErrorDescriptor,
    ErrorResponse,
):
    pass


class NotImplementedResponse(
    NotImplementedErrorDescriptor,
    ErrorResponse,
):
    pass


class BadGatewayResponse(
    BadGatewayErrorDescriptor,
    ErrorResponse,
):
    pass


class ServiceUnavailableResponse(
    ServiceUnavailableErrorDescriptor,
    ErrorResponse,
):
    pass


ERROR_RESPONSE_MAP: Mapping[ErrorCode, Type[ErrorResponse]] = {
    ErrorCode.BAD_REQUEST: BadRequestResponse,
    ErrorCode.UNAUTHORIZED: UnauthorizedResponse,
    ErrorCode.FORBIDDEN: ForbiddenResponse,
    ErrorCode.NOT_FOUND: NotFoundResponse,
    ErrorCode.METHOD_NOT_ALLOWED: MethodNotAllowedResponse,
    ErrorCode.CONFLICT: ConflictResponse,
    ErrorCode.UNPROCESSABLE_ENTITY: UnprocessableEntityResponse,
    ErrorCode.TOO_MANY_REQUESTS: TooManyRequestsResponse,
    ErrorCode.INTERNAL_SERVER_ERROR: InternalServerErrorResponse,
    ErrorCode.DATABASE_ERROR: DatabaseErrorResponse,
    ErrorCode.NOT_IMPLEMENTED: NotImplementedResponse,
    ErrorCode.BAD_GATEWAY: BadGatewayResponse,
    ErrorCode.SERVICE_UNAVAILABLE: ServiceUnavailableResponse,
}


STATUS_RESPONSE_MAP: Mapping[int, Type[ErrorResponse]] = {
    400: BadRequestResponse,
    401: UnauthorizedResponse,
    403: ForbiddenResponse,
    404: NotFoundResponse,
    405: MethodNotAllowedResponse,
    409: ConflictResponse,
    422: UnprocessableEntityResponse,
    429: TooManyRequestsResponse,
    500: InternalServerErrorResponse,
    501: NotImplementedResponse,
    502: BadGatewayResponse,
    503: ServiceUnavailableResponse,
}


OTHER_RESPONSES: Dict[
    Union[int, str],
    StringToAnyDict,
] = {
    400: {
        "description": "Bad Request Response",
        "model": BadRequestResponse,
    },
    401: {
        "description": "Unauthorized Response",
        "model": UnauthorizedResponse,
    },
    403: {
        "description": "Forbidden Response",
        "model": ForbiddenResponse,
    },
    404: {
        "description": "Not Found Response",
        "model": NotFoundResponse,
    },
    405: {
        "description": "Method Not Allowed Response",
        "model": MethodNotAllowedResponse,
    },
    409: {
        "description": "Conflict Response",
        "model": ConflictResponse,
    },
    422: {
        "description": "Unprocessable Entity Response",
        "model": UnprocessableEntityResponse,
    },
    429: {
        "description": "Too Many Requests Response",
        "model": TooManyRequestsResponse,
    },
    500: {
        "description": "Internal Server Error Response",
        "model": Union[
            InternalServerErrorResponse,
            DatabaseErrorResponse,
        ],
    },
    501: {
        "description": "Not Implemented Response",
        "model": NotImplementedResponse,
    },
    502: {
        "description": "Bad Gateway Response",
        "model": BadGatewayResponse,
    },
    503: {
        "description": "Service Unavailable Response",
        "model": ServiceUnavailableResponse,
    },
}


class SuccessResponse(
    SuccessDescriptor,
    Response[Literal[True], SuccessCode, AnyDataT, OptionalPaginationT, MetadataT],
    Generic[AnyDataT, OptionalPaginationT, MetadataT],
):
    success: Literal[True] = True


SuccessResponseT = TypeVar("SuccessResponseT", bound=SuccessResponse)


class AnyDataResponse(
    AnyDataSuccessDescriptor,
    SuccessResponse[ModelDataT, OptionalPaginationT, MetadataT],
    Generic[ModelDataT, OptionalPaginationT, MetadataT],
):
    pass


class NoDataResponse(
    NoDataPayload[MetadataT],
    NoDataSuccessDescriptor,
    SuccessResponse[None, None, MetadataT],
    Generic[MetadataT],
):
    data: None = None
    pagination: None = None

    @classmethod
    def new(
        cls,
        *,
        message: OptionalString = None,
        description: OptionalString = None,
        metadata: MetadataT = None,
        other: Any = None,
    ) -> "NoDataResponse[MetadataT]":
        descriptor = NoDataSuccessDescriptor()
        return cls(
            message=message if message is not None else descriptor.message,
            description=(
                description if description is not None else descriptor.description
            ),
            metadata=metadata,
            other=other,
        )


class SingleDataResponse(
    SingleDataPayload[ModelDataT, MetadataT],
    SingleDataSuccessDescriptor,
    SuccessResponse[ModelDataT, None, MetadataT],
    Generic[ModelDataT, MetadataT],
):
    pagination: None = None

    @classmethod
    def new(
        cls,
        *,
        message: OptionalString = None,
        description: OptionalString = None,
        data: ModelDataT,
        metadata: MetadataT = None,
        other: Any = None,
    ) -> "SingleDataResponse[ModelDataT, MetadataT]":
        descriptor = SingleDataSuccessDescriptor()
        return cls(
            message=message if message is not None else descriptor.message,
            description=(
                description if description is not None else descriptor.description
            ),
            data=data,
            metadata=metadata,
            other=other,
        )


class CreateSingleDataResponse(
    CreateSingleDataPayload[ModelDataT, MetadataT],
    CreateSingleDataSuccessDescriptor,
    SuccessResponse[DataPair[None, ModelDataT], None, MetadataT],
    Generic[ModelDataT, MetadataT],
):
    pagination: None = None

    @classmethod
    def new(
        cls,
        *,
        message: OptionalString = None,
        description: OptionalString = None,
        data: ModelDataT,
        metadata: MetadataT = None,
        other: Any = None,
    ) -> "CreateSingleDataResponse[ModelDataT, MetadataT]":
        descriptor = CreateSingleDataSuccessDescriptor()
        return cls(
            message=message if message is not None else descriptor.message,
            description=(
                description if description is not None else descriptor.description
            ),
            data=DataPair[None, ModelDataT](
                old=None,
                new=data,
            ),
            metadata=metadata,
            other=other,
        )


class ReadSingleDataResponse(
    ReadSingleDataPayload[ModelDataT, MetadataT],
    ReadSingleDataSuccessDescriptor,
    SuccessResponse[DataPair[ModelDataT, None], None, MetadataT],
    Generic[ModelDataT, MetadataT],
):
    pagination: None = None

    @classmethod
    def new(
        cls,
        *,
        message: OptionalString = None,
        description: OptionalString = None,
        data: ModelDataT,
        metadata: MetadataT = None,
        other: Any = None,
    ) -> "ReadSingleDataResponse[ModelDataT, MetadataT]":
        descriptor = ReadSingleDataSuccessDescriptor()
        return cls(
            message=message if message is not None else descriptor.message,
            description=(
                description if description is not None else descriptor.description
            ),
            data=DataPair[ModelDataT, None](
                old=data,
                new=None,
            ),
            metadata=metadata,
            other=other,
        )


class UpdateSingleDataResponse(
    UpdateSingleDataPayload[ModelDataT, MetadataT],
    UpdateSingleDataSuccessDescriptor,
    SuccessResponse[DataPair[ModelDataT, ModelDataT], None, MetadataT],
    Generic[ModelDataT, MetadataT],
):
    pagination: None = None

    @classmethod
    def new(
        cls,
        *,
        message: OptionalString = None,
        description: OptionalString = None,
        old_data: ModelDataT,
        new_data: ModelDataT,
        metadata: MetadataT = None,
        other: Any = None,
    ) -> "UpdateSingleDataResponse[ModelDataT, MetadataT]":
        descriptor = UpdateSingleDataSuccessDescriptor()
        return cls(
            message=message if message is not None else descriptor.message,
            description=(
                description if description is not None else descriptor.description
            ),
            data=DataPair[ModelDataT, ModelDataT](
                old=old_data,
                new=new_data,
            ),
            metadata=metadata,
            other=other,
        )


class DeleteSingleDataResponse(
    DeleteSingleDataPayload[ModelDataT, MetadataT],
    DeleteSingleDataSuccessDescriptor,
    SuccessResponse[DataPair[ModelDataT, None], None, MetadataT],
    Generic[ModelDataT, MetadataT],
):
    pagination: None = None

    @classmethod
    def new(
        cls,
        *,
        message: OptionalString = None,
        description: OptionalString = None,
        data: ModelDataT,
        metadata: MetadataT = None,
        other: Any = None,
    ) -> "DeleteSingleDataResponse[ModelDataT, MetadataT]":
        descriptor = DeleteSingleDataSuccessDescriptor()
        return cls(
            message=message if message is not None else descriptor.message,
            description=(
                description if description is not None else descriptor.description
            ),
            data=DataPair[ModelDataT, None](
                old=data,
                new=None,
            ),
            metadata=metadata,
            other=other,
        )


class OptionalSingleDataResponse(
    OptionalSingleDataPayload[ModelDataT, MetadataT],
    OptionalSingleDataSuccessDescriptor,
    SuccessResponse[Optional[ModelDataT], None, MetadataT],
    Generic[ModelDataT, MetadataT],
):
    pagination: None = None

    @classmethod
    def new(
        cls,
        *,
        message: OptionalString = None,
        description: OptionalString = None,
        data: Optional[ModelDataT] = None,
        metadata: MetadataT = None,
        other: Any = None,
    ) -> "OptionalSingleDataResponse[ModelDataT, MetadataT]":
        descriptor = OptionalSingleDataSuccessDescriptor()
        return cls(
            message=message if message is not None else descriptor.message,
            description=(
                description if description is not None else descriptor.description
            ),
            data=data,
            metadata=metadata,
            other=other,
        )


class MultipleDataResponse(
    MultipleDataPayload[ModelDataT, PaginationT, MetadataT],
    MultipleDataSuccessDescriptor,
    SuccessResponse[List[ModelDataT], PaginationT, MetadataT],
    Generic[ModelDataT, PaginationT, MetadataT],
):
    @classmethod
    def new(
        cls,
        *,
        message: OptionalString = None,
        description: OptionalString = None,
        data: List[ModelDataT],
        pagination: PaginationT,
        metadata: MetadataT = None,
        other: Any = None,
    ) -> "MultipleDataResponse[ModelDataT, PaginationT, MetadataT]":
        descriptor = MultipleDataSuccessDescriptor()
        return cls(
            message=message if message is not None else descriptor.message,
            description=(
                description if description is not None else descriptor.description
            ),
            data=data,
            pagination=pagination,
            metadata=metadata,
            other=other,
        )


class CreateMultipleDataResponse(
    CreateMultipleDataPayload[ModelDataT, PaginationT, MetadataT],
    CreateMultipleDataSuccessDescriptor,
    SuccessResponse[DataPair[None, List[ModelDataT]], PaginationT, MetadataT],
    Generic[ModelDataT, PaginationT, MetadataT],
):
    @classmethod
    def new(
        cls,
        *,
        message: OptionalString = None,
        description: OptionalString = None,
        data: List[ModelDataT],
        pagination: PaginationT,
        metadata: MetadataT = None,
        other: Any = None,
    ) -> "CreateMultipleDataResponse[ModelDataT, PaginationT, MetadataT]":
        descriptor = CreateMultipleDataSuccessDescriptor()
        return cls(
            message=message if message is not None else descriptor.message,
            description=(
                description if description is not None else descriptor.description
            ),
            data=DataPair[None, List[ModelDataT]](
                old=None,
                new=data,
            ),
            pagination=pagination,
            metadata=metadata,
            other=other,
        )


class ReadMultipleDataResponse(
    ReadMultipleDataPayload[ModelDataT, PaginationT, MetadataT],
    ReadMultipleDataSuccessDescriptor,
    SuccessResponse[DataPair[List[ModelDataT], None], PaginationT, MetadataT],
    Generic[ModelDataT, PaginationT, MetadataT],
):
    @classmethod
    def new(
        cls,
        *,
        message: OptionalString = None,
        description: OptionalString = None,
        data: List[ModelDataT],
        pagination: PaginationT,
        metadata: MetadataT = None,
        other: Any = None,
    ) -> "ReadMultipleDataResponse[ModelDataT, PaginationT, MetadataT]":
        descriptor = ReadMultipleDataSuccessDescriptor()
        return cls(
            message=message if message is not None else descriptor.message,
            description=(
                description if description is not None else descriptor.description
            ),
            data=DataPair[List[ModelDataT], None](
                old=data,
                new=None,
            ),
            pagination=pagination,
            metadata=metadata,
            other=other,
        )


class UpdateMultipleDataResponse(
    UpdateMultipleDataPayload[ModelDataT, PaginationT, MetadataT],
    UpdateMultipleDataSuccessDescriptor,
    SuccessResponse[
        DataPair[List[ModelDataT], List[ModelDataT]], PaginationT, MetadataT
    ],
    Generic[ModelDataT, PaginationT, MetadataT],
):
    @classmethod
    def new(
        cls,
        *,
        message: OptionalString = None,
        description: OptionalString = None,
        old_data: List[ModelDataT],
        new_data: List[ModelDataT],
        pagination: PaginationT,
        metadata: MetadataT = None,
        other: Any = None,
    ) -> "UpdateMultipleDataResponse[ModelDataT, PaginationT, MetadataT]":
        descriptor = UpdateMultipleDataSuccessDescriptor()
        return cls(
            message=message if message is not None else descriptor.message,
            description=(
                description if description is not None else descriptor.description
            ),
            data=DataPair[List[ModelDataT], List[ModelDataT]](
                old=old_data,
                new=new_data,
            ),
            pagination=pagination,
            metadata=metadata,
            other=other,
        )


class DeleteMultipleDataResponse(
    DeleteMultipleDataPayload[ModelDataT, PaginationT, MetadataT],
    DeleteMultipleDataSuccessDescriptor,
    SuccessResponse[DataPair[List[ModelDataT], None], PaginationT, MetadataT],
    Generic[ModelDataT, PaginationT, MetadataT],
):
    @classmethod
    def new(
        cls,
        *,
        message: OptionalString = None,
        description: OptionalString = None,
        data: List[ModelDataT],
        pagination: PaginationT,
        metadata: MetadataT = None,
        other: Any = None,
    ) -> "DeleteMultipleDataResponse[ModelDataT, PaginationT, MetadataT]":
        descriptor = DeleteMultipleDataSuccessDescriptor()
        return cls(
            message=message if message is not None else descriptor.message,
            description=(
                description if description is not None else descriptor.description
            ),
            data=DataPair[List[ModelDataT], None](
                old=data,
                new=None,
            ),
            pagination=pagination,
            metadata=metadata,
            other=other,
        )


class OptionalMultipleDataResponse(
    OptionalMultipleDataPayload[ModelDataT, PaginationT, MetadataT],
    OptionalMultipleDataSuccessDescriptor,
    SuccessResponse[Optional[List[ModelDataT]], PaginationT, MetadataT],
    Generic[ModelDataT, PaginationT, MetadataT],
):
    @classmethod
    def new(
        cls,
        *,
        message: OptionalString = None,
        description: OptionalString = None,
        data: Optional[List[ModelDataT]],
        pagination: PaginationT,
        metadata: MetadataT = None,
        other: Any = None,
    ) -> "OptionalMultipleDataResponse[ModelDataT, PaginationT, MetadataT]":
        descriptor = OptionalMultipleDataSuccessDescriptor()
        return cls(
            message=message if message is not None else descriptor.message,
            description=(
                description if description is not None else descriptor.description
            ),
            data=data,
            pagination=pagination,
            metadata=metadata,
            other=other,
        )
