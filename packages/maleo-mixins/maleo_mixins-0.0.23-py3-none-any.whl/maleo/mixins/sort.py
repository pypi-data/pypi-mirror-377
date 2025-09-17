from pydantic import BaseModel, Field, field_validator
from typing import List
from maleo.enums.order import Order as OrderEnum
from maleo.types.string import ListOfStrings
from .constants import SORT_COLUMN_PATTERN
from .general import Order
from .identity import Name


class SortColumn(
    Order[OrderEnum],
    Name[str],
):
    pass


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
            if len(parts) == 2 and parts[1].lower() in OrderEnum:
                try:
                    sort_columns.append(
                        SortColumn(
                            name=parts[0],
                            order=OrderEnum(parts[1].lower()),
                        )
                    )
                except Exception:
                    continue

        return sort_columns


class SortColumns(BaseModel):
    sort_columns: List[SortColumn] = Field(
        [SortColumn(name="id", order=OrderEnum.ASC)],
        description="List of columns to be sorted",
    )

    @property
    def sorts(self) -> ListOfStrings:
        # Process sort_columns parameters
        sorts = []
        for item in self.sort_columns:
            sorts.append(f"{item.name}.{item.order.value}")

        return sorts
