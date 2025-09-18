r"""Components for selecting objects from a collection, e.g. selectboxes."""

# Third party
import streamlit as st

# Local
from cambiato.models import UtilityDataFrameModel

from . import keys
from .core import LabelVisibility


def utility_pills_selector(
    label: str,
    utilities: UtilityDataFrameModel,
    default: int | None = 0,
    label_visibility: LabelVisibility = 'visible',
    key: str = keys.UTILITY_PILLS_SELECTOR,
) -> int | None:
    r"""Select a utility from the available `utilities`.

    Parameters
    ----------
    label : str
        The label of the pills selector.

    utilities : cambiato.models.UtilityDataFrameModel
        The utilities to select from.

    default: int or None, default 0
        The index ID (zero indexed) of `utilities` that will get the default
        selected utility. If None no utility is selected by default.

    label_visibility : Literal['visible', 'hidden', 'collapsed']
        The visibility of the label. The default is 'visible'. If 'hidden' the space of the
        label is still occupied, which makes it easier to algin the component horizontally
        against other components. This is in contrast to 'collapsed' where the space of the
        label is removed.

    key : str, default cambiato.app.components.keys.UTILITY_PILLS_SELECTOR
        The unique identifier of the selector in the session state.

    Returns
    -------
    int or None
        The ID of the selected utility or None if no utility was selected.
    """

    return st.pills(
        label=label,
        options=utilities.index,
        format_func=utilities.format_func,
        default=default if default is None else utilities.index[default],
        disabled=utilities.empty,
        label_visibility=label_visibility,
        key=key,
    )
