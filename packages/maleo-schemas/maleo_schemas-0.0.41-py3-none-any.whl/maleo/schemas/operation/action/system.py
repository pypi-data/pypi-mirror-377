from pydantic import Field
from maleo.types.dict import OptionalStringToAnyDict
from ..enums import SystemOperationType
from .base import BaseOperationAction


class SystemOperationAction(BaseOperationAction[SystemOperationType]):
    details: OptionalStringToAnyDict = Field(None, description="Action's details")
