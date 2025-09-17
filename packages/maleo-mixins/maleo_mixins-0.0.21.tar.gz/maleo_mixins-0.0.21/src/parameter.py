from pydantic import BaseModel, Field
from typing import Generic, TypeVar
from maleo.types.enum import OptionalListOfStringEnums
from maleo.types.string import OptionalString


class Search(BaseModel):
    search: OptionalString = Field(None, description="Search string.")


class UseCache(BaseModel):
    use_cache: bool = Field(True, description="Whether to use cache")


IncludeT = TypeVar("IncludeT", bound=OptionalListOfStringEnums)


class Include(BaseModel, Generic[IncludeT]):
    include: IncludeT = Field(..., description="Included field(s)")


ExcludeT = TypeVar("ExcludeT", bound=OptionalListOfStringEnums)


class Exclude(BaseModel, Generic[ExcludeT]):
    exclude: ExcludeT = Field(..., description="Excluded field(s)")
