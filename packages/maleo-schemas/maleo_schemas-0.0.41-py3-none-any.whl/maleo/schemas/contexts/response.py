from pydantic import (
    BaseModel,
    Field,
)
from typing import Generic, List, Optional, Tuple, TypeVar
from maleo.types.string import OptionalString


class ResponseContext(BaseModel):
    status_code: int = Field(..., description="Status code")
    media_type: OptionalString = Field(None, description="Media type (Optional)")
    headers: Optional[List[Tuple[str, str]]] = Field(
        None, description="Response's headers"
    )


ResponseContextT = TypeVar("ResponseContextT", bound=Optional[ResponseContext])


class ResponseContextMixin(BaseModel, Generic[ResponseContextT]):
    response_context: ResponseContextT = Field(..., description="Response's context")
