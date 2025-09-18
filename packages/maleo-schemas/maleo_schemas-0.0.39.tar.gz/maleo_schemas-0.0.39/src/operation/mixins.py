from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator
from typing import Self
from uuid import UUID
from .enums import OperationType as OperationTypeEnum
from maleo.mixins.timestamp import ExecutionTimestamp, CompletionTimestamp, Duration


class Id(BaseModel):
    id: UUID = Field(..., description="Operation's id")


class OperationType(BaseModel):
    type: OperationTypeEnum = Field(..., description="Operation's type")


class Timestamp(
    Duration[float],
    CompletionTimestamp[datetime],
    ExecutionTimestamp[datetime],
):
    duration: float = Field(0.0, ge=0.0, description="Duration")

    @model_validator(mode="after")
    def calculate_duration(self) -> Self:
        self.duration = (self.completed_at - self.executed_at).total_seconds()
        return self

    @classmethod
    def now(cls) -> "Timestamp":
        now = datetime.now(tz=timezone.utc)
        return cls(executed_at=now, completed_at=now, duration=0)

    @classmethod
    def completed_now(cls, executed_at: datetime) -> "Timestamp":
        completed_at = datetime.now(tz=timezone.utc)
        return cls(
            executed_at=executed_at,
            completed_at=completed_at,
            duration=(completed_at - executed_at).total_seconds(),
        )


class TimestampMixin(BaseModel):
    timestamp: Timestamp = Field(..., description="Operation's timestamp")


class Summary(BaseModel):
    summary: str = Field(..., description="Operation's summary")
