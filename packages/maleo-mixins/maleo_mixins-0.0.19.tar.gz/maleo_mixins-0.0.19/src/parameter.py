import re
import urllib.parse
from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field, field_validator
from typing import Generic, List, Optional, TypeVar
from maleo.constants.patterns import DATE_FILTER_PATTERN, SORT_COLUMN_PATTERN
from maleo.constants.status import FULL_STATUSES
from maleo.enums.operation import ResourceOperationStatusUpdateType
from maleo.enums.sort import Order
from maleo.types.base.integer import OptionalListOfIntegers, ListOfIntegers
from maleo.types.base.string import (
    ListOfStrings,
    OptionalListOfStrings,
    OptionalString,
)
from maleo.types.base.uuid import ListOfUUIDs, OptionalListOfUUIDs
from maleo.types.enums.status import (
    ListOfDataStatuses as ListOfDataStatusesEnum,
    OptionalListOfDataStatuses as OptionalListOfDataStatusesEnum,
)
from .general import DateFilter, SortColumn


IdentifierTypeT = TypeVar("IdentifierTypeT", bound=StrEnum)


class IdentifierType(BaseModel, Generic[IdentifierTypeT]):
    identifier: IdentifierTypeT = Field(..., description="Identifier's type")


IdentifierValueT = TypeVar("IdentifierValueT")


class IdentifierValue(BaseModel, Generic[IdentifierValueT]):
    value: IdentifierValueT = Field(..., description="Identifier's value")


class IdentifierTypeValue(
    IdentifierValue[IdentifierValueT],
    IdentifierType[IdentifierTypeT],
    BaseModel,
    Generic[IdentifierTypeT, IdentifierValueT],
):
    pass


class Ids(BaseModel):
    ids: ListOfIntegers = Field([], description="Ids")


class OptionalIds(BaseModel):
    ids: OptionalListOfIntegers = Field(None, description="Ids")


class OrganizationIds(BaseModel):
    organization_ids: ListOfIntegers = Field([], description="Organization Ids")


class OptionalOrganizationIds(BaseModel):
    organization_ids: OptionalListOfIntegers = Field(
        None, description="Organization Ids"
    )


class ParentIds(BaseModel):
    parent_ids: ListOfIntegers = Field([], description="Parent Ids")


class OptionalParentIds(BaseModel):
    parent_ids: OptionalListOfIntegers = Field(None, description="Parent Ids")


class UserIds(BaseModel):
    user_ids: ListOfIntegers = Field([], description="User Ids")


class OptionalUserIds(BaseModel):
    user_ids: OptionalListOfIntegers = Field(None, description="User Ids")


class UUIDs(BaseModel):
    uuids: ListOfUUIDs = Field([], description="UUIDs")


class OptionalUUIDs(BaseModel):
    uuids: OptionalListOfUUIDs = Field(None, description="UUIDs")


class Filters(BaseModel):
    filters: ListOfStrings = Field(
        [],
        description="Date range filters with '<COLUMN_NAME>|from::<ISO_DATETIME>|to::<ISO_DATETIME>' format.",
    )

    @field_validator("filters")
    @classmethod
    def validate_date_filters(cls, values):
        if isinstance(values, list):
            decoded_values = [urllib.parse.unquote(value) for value in values]
            # Replace space followed by 2 digits, colon, 2 digits with + and those digits
            fixed_values = []
            for value in decoded_values:
                # Look for the pattern: space followed by 2 digits, colon, 2 digits
                fixed_value = re.sub(
                    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+) (\d{2}:\d{2})",
                    r"\1+\2",
                    value,
                )
                fixed_values.append(fixed_value)
            final_values = [
                value for value in fixed_values if DATE_FILTER_PATTERN.match(value)
            ]
            return final_values

    @property
    def date_filters(self) -> List[DateFilter]:
        # Process filter parameters
        date_filters = []
        for filter_item in self.filters:
            parts = filter_item.split("|")
            if len(parts) >= 2 and parts[0]:
                name = parts[0]
                from_date = None
                to_date = None

                # Process each part to extract from and to dates
                for part in parts[1:]:
                    if part.startswith("from::"):
                        try:
                            from_date_str = part.replace("from::", "")
                            from_date = datetime.fromisoformat(from_date_str)
                        except ValueError:
                            continue
                    elif part.startswith("to::"):
                        try:
                            to_date_str = part.replace("to::", "")
                            to_date = datetime.fromisoformat(to_date_str)
                        except ValueError:
                            continue

                # Only add filter if at least one date is specified
                if from_date or to_date:
                    date_filters.append(
                        DateFilter(name=name, from_date=from_date, to_date=to_date)
                    )

        # Update date_filters
        return date_filters


class DateFilters(BaseModel):
    date_filters: List[DateFilter] = Field([], description="Date filters to be applied")

    @property
    def filters(self) -> ListOfStrings:
        # Process filter parameters
        filters = []
        for item in self.date_filters:
            if item.from_date or item.to_date:
                filter_string = item.name
                if item.from_date:
                    filter_string += f"|from::{item.from_date.isoformat()}"
                if item.to_date:
                    filter_string += f"|to::{item.to_date.isoformat()}"
                filters.append(filter_string)

        return filters


class DataStatuses(BaseModel):
    statuses: ListOfDataStatusesEnum = Field(
        list(FULL_STATUSES), description="Data's statuses."
    )


class OptionalDataStatuses(BaseModel):
    statuses: OptionalListOfDataStatusesEnum = Field(
        None, description="Data's statuses."
    )


class Codes(BaseModel):
    codes: ListOfStrings = Field([], description="Codes")


class OptionalCodes(BaseModel):
    codes: OptionalListOfStrings = Field(None, description="Codes")


class Keys(BaseModel):
    keys: ListOfStrings = Field([], description="Keys")


class OptionalKeys(BaseModel):
    keys: OptionalListOfStrings = Field(None, description="Keys")


class Names(BaseModel):
    names: ListOfStrings = Field([], description="Names")


class OptionalNames(BaseModel):
    names: OptionalListOfStrings = Field(None, description="Names")


class Search(BaseModel):
    search: OptionalString = Field(None, description="Search string.")


class Sorts(BaseModel):
    sorts: ListOfStrings = Field(
        ["id.asc"],
        description="Column sorts with '<COLUMN_NAME>.<ASC|DESC>' format.",
    )

    @field_validator("sorts")
    @classmethod
    def validate_sorts(cls, values):
        return [value for value in values if SORT_COLUMN_PATTERN.match(value)]

    @property
    def sort_columns(self) -> List[SortColumn]:
        # Process sort parameters
        sort_columns = []
        for item in self.sorts:
            parts = item.split(".")
            if len(parts) == 2 and parts[1].lower() in Order:
                try:
                    sort_columns.append(
                        SortColumn(
                            name=parts[0],
                            order=Order(parts[1].lower()),
                        )
                    )
                except Exception:
                    continue

        return sort_columns


class SortColumns(BaseModel):
    sort_columns: List[SortColumn] = Field(
        [SortColumn(name="id", order=Order.ASC)],
        description="List of columns to be sorted",
    )

    @property
    def sorts(self) -> ListOfStrings:
        # Process sort_columns parameters
        sorts = []
        for item in self.sort_columns:
            sorts.append(f"{item.name}.{item.order.value}")

        return sorts


class UseCache(BaseModel):
    use_cache: bool = Field(True, description="Whether to use cache")


IncludeT = TypeVar("IncludeT", bound=StrEnum)


class Include(BaseModel, Generic[IncludeT]):
    include: Optional[List[IncludeT]] = Field(None, description="Included field(s)")


ExcludeT = TypeVar("ExcludeT", bound=StrEnum)


class Exclude(BaseModel, Generic[ExcludeT]):
    exclude: Optional[List[ExcludeT]] = Field(None, description="Excluded field(s)")


class StatusUpdateAction(BaseModel):
    action: ResourceOperationStatusUpdateType = Field(
        ..., description="Status update action"
    )
