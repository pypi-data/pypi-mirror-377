r"""Core functionality of DataFrame components."""

# Standard library
from collections.abc import Sequence
from typing import Any, TypeAlias, TypedDict

DataFrameRow: TypeAlias = dict[str, Any]


class ChangedDataFrameRows(TypedDict):
    r"""Changed rows in an editable DataFrame."""

    edited_rows: dict[str, DataFrameRow]
    added_rows: Sequence[DataFrameRow]
    deleted_rows: Sequence[int]
