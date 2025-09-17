from pydantic import BaseModel, Field
from typing import Generic, TypeVar
from maleo.enums.status import (
    OptionalDataStatus as OptionalDataStatusEnum,
    OptionalListOfDataStatuses as OptionalListOfDataStatusesEnum,
)


DataStatusT = TypeVar("DataStatusT", bound=OptionalDataStatusEnum)


class DataStatus(BaseModel, Generic[DataStatusT]):
    status: DataStatusT = Field(..., description="Data's status")


DataStatusesT = TypeVar("DataStatusesT", bound=OptionalListOfDataStatusesEnum)


class DataStatuses(BaseModel, Generic[DataStatusesT]):
    statuses: DataStatusesT = Field(..., description="Data's statuses.")
