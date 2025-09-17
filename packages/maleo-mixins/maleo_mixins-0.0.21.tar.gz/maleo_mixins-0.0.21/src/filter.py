import re
import urllib.parse
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List
from maleo.types.datetime import OptionalDatetime
from maleo.types.string import ListOfStrings
from .constants import DATE_FILTER_PATTERN
from .identity import Name
from .timestamp import FromTimestamp, ToTimestamp


class DateFilter(
    ToTimestamp[OptionalDatetime],
    FromTimestamp[OptionalDatetime],
    Name[str],
):
    pass


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
