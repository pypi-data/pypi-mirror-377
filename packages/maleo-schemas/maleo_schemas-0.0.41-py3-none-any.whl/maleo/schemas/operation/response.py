from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Union
from ..response import Response


ResponseT = TypeVar("ResponseT", bound=Union[bytes, Response])


class ResponseMixin(BaseModel, Generic[ResponseT]):
    response: ResponseT = Field(..., description="Operation's Response")
