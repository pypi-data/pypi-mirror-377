from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Generic, TypeVar


TypeT = TypeVar("TypeT", bound=StrEnum)


class BaseOperationAction(BaseModel, Generic[TypeT]):
    type: TypeT = Field(..., description="Action's type")
