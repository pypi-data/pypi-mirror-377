from pydantic import BaseModel, Field
from typing import Any, Generic, TypeVar, Union
from maleo.types.boolean import OptionalBoolean
from maleo.types.enum import OptionalStringEnum, OptionalListOfStringEnums
from maleo.types.float import OptionalFloat
from maleo.types.integer import OptionalInteger
from maleo.types.misc import StringOrStringEnum
from maleo.types.string import OptionalListOfStrings, OptionalString


class StatusCode(BaseModel):
    status_code: int = Field(..., description="Status code", ge=100, le=500)


SuccessT = TypeVar("SuccessT", bound=bool)


class Success(BaseModel, Generic[SuccessT]):
    success: SuccessT = Field(..., description="Success")


CodeT = TypeVar("CodeT", bound=StringOrStringEnum)


class Code(BaseModel, Generic[CodeT]):
    code: CodeT = Field(..., description="Code")


CodesT = TypeVar(
    "CodesT", bound=Union[OptionalListOfStringEnums, OptionalListOfStrings]
)


class Codes(BaseModel, Generic[CodesT]):
    codes: CodesT = Field(..., description="Codes")


class Message(BaseModel):
    message: str = Field(..., description="Message")


class Description(BaseModel):
    description: str = Field(..., description="Description")


class Descriptor(Description, Message, Code[CodeT], Generic[CodeT]):
    pass


OrderT = TypeVar("OrderT", bound=Union[OptionalInteger, OptionalStringEnum])


class Order(BaseModel, Generic[OrderT]):
    order: OrderT = Field(..., description="Order")


LevelT = TypeVar("LevelT", bound=OptionalStringEnum)


class Level(BaseModel, Generic[LevelT]):
    level: LevelT = Field(..., description="Level")


NoteT = TypeVar("NoteT", bound=OptionalString)


class Note(BaseModel, Generic[NoteT]):
    note: NoteT = Field(..., description="Note")


IsDefaultT = TypeVar("IsDefaultT", bound=OptionalBoolean)


class IsDefault(BaseModel, Generic[IsDefaultT]):
    is_default: IsDefaultT = Field(..., description="Whether is default")


class Other(BaseModel):
    other: Any = Field(None, description="Other")


AgeT = TypeVar("AgeT", float, int, OptionalFloat, OptionalInteger)


class Age(BaseModel, Generic[AgeT]):
    age: AgeT = Field(..., ge=0, description="Age")
