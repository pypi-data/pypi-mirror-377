from pydantic import BaseModel, Field
from typing import Any
from maleo.types.string import OptionalListOfStrings


class ErrorMetadata(BaseModel):
    details: Any = Field(None, description="Details")
    traceback: OptionalListOfStrings = Field(None, description="Traceback")
