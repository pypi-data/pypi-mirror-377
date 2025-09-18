r"""Core functionality to work with translations."""

# Standard library
from collections.abc import Mapping, Sequence
from importlib.resources import files
from typing import Any, Protocol, TypeAlias, TypeVar, overload

# Third party
import pandas as pd

# Local
from cambiato import exceptions
from cambiato.config import Language
from cambiato.models.core import BaseModel
from cambiato.translations.components import Components
from cambiato.translations.controllers import Controllers
from cambiato.translations.database import Database
from cambiato.translations.pages import OrderPage, PageTranslationModels
from cambiato.translations.views import Views

_Translated: TypeAlias = Mapping[str, str]
TranslationMapping: TypeAlias = Mapping[int, _Translated] | Mapping[str, _Translated]
TranslationColumns: TypeAlias = Sequence[str] | str | None
TranslationIdColumn: TypeAlias = str | None


class SupportsModelDump(Protocol):
    r"""Implements the `model_dump` method."""

    def model_dump(self) -> dict[str, Any]: ...


T = TypeVar('T', bound=SupportsModelDump)


class TranslationModel(BaseModel):
    r"""The model of the translations.

    Parameters
    ----------
    database : cambiato.translations.Database
        The translations for the default data in the database.

    components : cambiato.translations.Components
        The translations for the components of the app.

    views : cambiato.translations.Views
        The translations for the views of the app.

    controllers : cambiato.translations.Controllers
        The translations for the page controllers of the app.
    """

    database: Database
    components: Components
    views: Views
    controllers: Controllers


def load_translation(language: Language) -> PageTranslationModels:
    r"""Load the translations for the selected language.

    Parameters
    ----------
    language : cambiato.config.Language
        The translation language to load.

    Returns
    -------
    cambiato.app.translations.PageTranslationModels
        The model of the translations for the pages of the app.
    """

    lang_file = files('cambiato.translations.translations').joinpath(f'{language}.json')
    tm = TranslationModel.model_validate_json(lang_file.read_text())
    comp = tm.components

    order_page = OrderPage(
        controller=tm.controllers.order,
        db=tm.database,
        create_order_button=comp.buttons.create_order_button,
        create_order_form=comp.forms.create_order_form,
        edit_orders_view=tm.views.orders.edit_orders_view,
        edit_orders_df=comp.dataframes.edit_orders,
    )

    return PageTranslationModels(order_page=order_page)


def create_translation_mapping(translation: Mapping[int, T]) -> TranslationMapping:
    r"""Create a translation mapping to use for translating a DataFrame.

    Parameters
    ----------
    translation : Mapping[int, T]
        A mapping of ID:s (usually primary keys) to objects that implement the method:
        `model_dump() -> dict[str, Any]`.

    Returns
    -------
    cambiato.translations.TranslationMapping
        The translations for each ID defined as the keys in `translation`.
    """

    return {key: value.model_dump() for key, value in translation.items()}


@overload
def translate_dataframe(
    df: pd.DataFrame,
    translation: TranslationMapping,
    columns: TranslationColumns = None,
    id_column: TranslationIdColumn = None,
    copy: bool = False,
) -> pd.DataFrame: ...


@overload
def translate_dataframe(
    df: pd.DataFrame,
    translation: Sequence[TranslationMapping],
    columns: Sequence[TranslationColumns],
    id_column: Sequence[TranslationIdColumn],
    copy: bool = False,
) -> pd.DataFrame: ...


def translate_dataframe(
    df: pd.DataFrame,
    translation: TranslationMapping | Sequence[TranslationMapping],
    columns: TranslationColumns | Sequence[TranslationColumns] = None,
    id_column: TranslationIdColumn | Sequence[TranslationIdColumn] = None,
    copy: bool = False,
) -> pd.DataFrame:
    r"""Translate selected columns of a :class:`pandas.DataFrame`.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to in which to translate columns. It should have a named index column.

    translation : cambiato.translations.TranslationMapping or Sequence[cambiato.translations.TranslationMapping]
        The translations for the columns of `df`. The keys should match the index of
        `df`. A sequence of translations can be provided to apply different translations
        to different `columns`.

    columns : Sequence[str] | str | None or Sequence[Sequence[str] | str | None], default None
        The columns of `df` to translate. The supplied columns should be found `df` and will
        replace the column names in `translation` in the order they are defined. If None all
        columns are translated. If `translation` is a sequence of translations then `columns`
        should be a sequence of equal length.

    id_column : str | None or Sequence[str | None], default None
        The identity column to use for aligning the translation mapping to translate rows
        for the selected `columns`. If None the original index column of `df` is used.
        If `translation` and `columns` are sequences, specify a sequence of equal length.

        E.g. specifying 'order_type_id' when columns = 'order_type_name' will translate the
        order_type_name column with translation keys matching the values of the order_type_id
        column.

    copy : bool, default False
        True if a copy of the translated DataFrame should be returned.
        If False the DataFrame `df` is modified inplace.

    Returns
    -------
    df : pandas.DataFrame
        An updated version of `df` with selected columns translated.

    Raises
    ------
    cambiato.CambiatoError
        If `translation` is a sequence of unequal length to the `columns` and `id_column` sequences.
    """

    df = df.copy() if copy else df

    if isinstance(translation, Mapping):
        trans_iter: Sequence[TranslationMapping] = [translation]
        cols_iter = [columns]
        id_col_iter = [id_column]
    else:
        trans_iter = translation
        cols_iter = columns  # type: ignore[assignment]
        id_col_iter = id_column  # type: ignore[assignment]

    len_trans_iter = len(trans_iter)
    len_cols_iter = 0 if cols_iter is None else len(cols_iter)
    len_id_col_iter = 0 if id_col_iter is None else len(id_col_iter)

    if len_trans_iter != len_cols_iter != len_id_col_iter:
        raise exceptions.CambiatoError(
            'Mismatch in lengths of translations, columns and id_column '
            f'({len_trans_iter} != {len_cols_iter} != {len_id_col_iter}) !'
        )

    original_index_col = df.index.name
    original_col_order = df.columns.tolist()

    for trans, cols, id_col in zip(trans_iter, cols_iter, id_col_iter, strict=True):
        _cols = [cols] if isinstance(cols, str) else cols

        df_trans = pd.DataFrame.from_dict(trans, orient='index')  # type: ignore[call-overload]

        if _cols is not None:  # Rename the columns to translate
            df_trans = df_trans.iloc[:, 0 : len(_cols)]
            df_trans.columns = _cols

        if id_col is not None and df.index.name != id_col:
            df = df.reset_index().set_index(id_col)

        df.update(df_trans)

    return df.reset_index().set_index(original_index_col).loc[:, original_col_order]
