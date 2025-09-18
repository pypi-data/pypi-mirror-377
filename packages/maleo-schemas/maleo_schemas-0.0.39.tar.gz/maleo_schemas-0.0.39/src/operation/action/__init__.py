from pydantic import BaseModel, Field
from typing import Generic, TypeVar


ActionT = TypeVar("ActionT", bound=BaseModel)


class ActionMixin(BaseModel, Generic[ActionT]):
    action: ActionT = Field(..., description="Action.")
