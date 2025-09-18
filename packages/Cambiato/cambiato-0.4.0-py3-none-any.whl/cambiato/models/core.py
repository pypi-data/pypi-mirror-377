r"""The core data models of Cambiato."""

# Standard library
from abc import abstractmethod
from collections.abc import Callable, Mapping, Sequence
from typing import Any, ClassVar, Generic, TypeAlias, TypeVar

# Third party
import pandas as pd
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, ValidationError
from streamlit_passwordless import User as User

# Local
from cambiato import exceptions

StrMapping: TypeAlias = Mapping[str, str]
ColumnList: TypeAlias = list[str]


class BaseModel(PydanticBaseModel):
    r"""The BaseModel that all models inherit from."""

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, frozen=True)

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        try:
            super().__init__(**kwargs)
        except ValidationError as e:
            raise exceptions.CambiatoError(str(e)) from None


IndexT = TypeVar('IndexT', int, str)


class BaseDataFrameModel(BaseModel, Generic[IndexT]):
    """The base model that all DataFrame models will inherit from.

    A DataFrame model represents a database table, a query or some other table like structure.
    using a :class:`pandas.DataFrame`. The DataFrame is accessible from the `df` attribute.
    Each column name of the DataFrame should be implemented as a class variable starting with
    the prefix "c_", e.g. `c_name: ClassVar[str] = 'name'` for a name column. The class variables
    listed below should be defined for each subclass of this model.

    Class Variables
    ---------------
    dtypes : ClassVar[dict[str, str]]
        The mapping of column names to their datatypes of the DataFrame.

    index_cols : ClassVar[list[str]]
        The index columns of the DataFrame.

    parse_dates : ClassVar[list[str]]
        The columns of the DataFrame that should be parsed into datetime columns.

    Parameters
    ----------
    df : pandas.DataFrame, default pandas.DataFrame()
        The contents of the model as a DataFrame.
    """

    dtypes: ClassVar[StrMapping] = {}
    index_cols: ClassVar[ColumnList] = []
    parse_dates: ClassVar[ColumnList] = []

    df: pd.DataFrame = Field(default_factory=pd.DataFrame)

    @property
    def shape(self) -> tuple[int, int]:
        r"""The shape (rows, cols) of the DataFrame."""

        return self.df.shape

    @property
    def index(self) -> pd.Index:
        r"""The index column(s) of the DataFrame."""

        return self.df.index

    @property
    def row_count(self) -> int:
        r"""The number of rows of the DataFrame."""

        return self.df.shape[0]

    @property
    def empty(self) -> bool:
        r"""Check if the DataFrame is empty or not."""

        return self.row_count == 0

    @property
    def col_dtypes(self) -> pd.Series:
        r"""The dtypes of the columns of the DataFrame `df`."""

        return self.df.dtypes

    @property
    @abstractmethod
    def index_type(self) -> Callable[[Any], IndexT]:
        """The constructor for the index type, which should be int or str."""

    def display_row(self, id_: int | str) -> str:
        r"""String representation of a row in the DataFrame.

        Each subclass should override this method to fit its DataFrame content.

        Parameters
        ----------
        id_: int or str
            The index ID of the DataFrame for which to retrieve a row.

        Returns
        -------
        str
            The string representation of the row.
        """

        return str(id_)

    @property
    def format_func(self) -> Callable[[int | str], str]:
        r"""A function to format a row of the DataFrame as a string.

        The function takes an index ID of the DataFrame and displays its row as a string.
        """

        return lambda x: self.display_row(x)

    def get_index(self, value: Any, column: str) -> IndexT | None:
        r"""Get the index of a row from a value of a column.

        Should only be used for columns with values that uniquely identifies a row.

        Parameters
        ----------
        value : Any
            The value of the `column` for which to get the row index ID.

        column : str
            The column to filter by `value`.

        Returns
        -------
        int or str or None
            The index ID of row matching `value` in `column`. If no match None is returned.

        Raises
        ------
        cambiato.MissingColumnError
            If `column` is not among the columns of the DataFrame.

        cambiato.MultipleRowsForColumnValueError
            If multiple rows match the supplied column value.
        """

        df = self.df

        if column not in df.columns:
            raise exceptions.MissingColumnError(
                f'Column "{column}" is not among the columns '
                f'of the DataFrame : {df.columns.tolist()}'
            )

        mask = df[column].eq(value)

        if not mask.any():
            return None

        pos = int(mask.to_numpy().argmax())

        if mask.iloc[pos + 1 :].any():
            raise exceptions.MultipleRowsForColumnValueError(
                f'Multiple rows match column "{column}" == {value!r}!'
            )

        return self.index_type(df.index[pos])

    def get_index_by_row_nr(self, row_nr: int) -> IndexT:
        r"""Get the index of a row from its row number in the DataFrame.

        Parameters
        ----------
        row_nr : int
            The row number of the DataFrame (zero indexed).

        Returns
        -------
        int or str
            The index ID of the row matching `row_nr`.

        Raises
        ------
        cambiato.MissingRowError
            If `row_nr` does not exist in the DataFrame.
        """

        try:
            return self.index_type(self.df.index[row_nr])
        except IndexError:
            raise exceptions.MissingRowError(
                f'Row number {row_nr} does not exist in DataFrame with nr_rows = {self.row_count}!'
            ) from None

    def get_column(
        self, column: str, unique: bool = False, sort_ascending: bool | None = None
    ) -> pd.Series:
        r"""Get the values of a column in the DataFrame.

        Parameters
        ----------
        column : str
            The name of the column to extract.

        unique : bool, default False
            True if only the unique values from the column should be extracted and
            False for the entire column as is.

        sort_ascending : bool or None, default None
            True if the column values should be sorted in ascending order and False
            for descending order. If None no sorting is performed.

        Returns
        -------
        pandas.Series
            The extracted column.

        Raises
        ------
        cambiato.MissingColumnError
            If `column` is not among the columns of the DataFrame.
        """

        df = self.df

        if column not in df.columns:
            raise exceptions.MissingColumnError(
                f'Column "{column}" is not among the columns '
                f'of the DataFrame : {df.columns.tolist()}'
            )

        s = df[column].drop_duplicates() if unique else df[column]

        return s if sort_ascending is None else s.sort_values(ascending=sort_ascending)

    def localize_and_convert_timezone(
        self,
        df: pd.DataFrame | None = None,
        location_tz: str = 'UTC',
        target_tz: str | None = None,
        ensure_datetime_cols: Sequence[str] | None = None,
        copy: bool = False,
    ) -> pd.DataFrame:
        r"""Localize datetime columns and optionally convert them to timezone `target_tz`.

        Parameters
        ----------
        df : pandas.DataFrame or None, default None
            The DataFrame subject to the timezone operations.
            If None the underlying DataFrame of the model is used.

        location_tz : str, default 'UTC'
            The timezone to localize naive datetime columns into.

        target_tz : str or None, default None
            The timezone to convert localized datetimes columns into.
            If None, only localization is applied.

        ensure_datetime_cols : Sequence[str] or None, default None
            A sequence of columns that may need to be converted to the datetime datatype.
            If a datetime column has all missing values it may be of datatype string and
            thus needs conversion to datetime before localization/timezone conversion.

        copy : bool, default False
            True if the operation should be performed on a copy of the underlying DataFrame.
            If False the DataFrame of the model is modified inplace.

        Returns
        -------
        df : pandas.DataFrame
            The DataFrame with its datetime columns localized/converted.
        """

        df = (self.df.copy() if copy else self.df) if df is None else (df.copy() if copy else df)

        datetime_cols = set(df.select_dtypes(include=['datetime64[ns]']).columns)

        if ensure_datetime_cols:
            cols_to_process = datetime_cols.union(set(ensure_datetime_cols))
        else:
            cols_to_process = datetime_cols

        for col in cols_to_process:
            if col in datetime_cols:
                s = df[col]
            else:
                s = pd.to_datetime(df[col]).astype('timestamp[ns][pyarrow]')

            if s.dt.tz is None:
                s = s.dt.tz_localize(location_tz)
            if target_tz is not None:
                s = s.dt.tz_convert(target_tz)

            df[col] = s

        return df


class IntIndexedDataFrameModel(BaseDataFrameModel[int]):
    """A DataFrame model with an integer based index column."""

    @property
    def index_type(self) -> Callable[[Any], int]:
        return int


class StrIndexedDataFrameModel(BaseDataFrameModel[str]):
    """A DataFrame model with a string based index column."""

    @property
    def index_type(self) -> Callable[[Any], str]:
        return str
