from pydantic import BaseModel, Field
from .enums import OperationType as OperationTypeEnum


class OperationType(BaseModel):
    type: OperationTypeEnum = Field(..., description="Operation's type")


class Summary(BaseModel):
    summary: str = Field(..., description="Operation's summary")
