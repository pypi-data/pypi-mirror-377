r"""Core functionality of the components."""

# Standard library
from typing import Literal, TypeAlias

# Third party
from streamlit_passwordless import BannerContainer as BannerContainer
from streamlit_passwordless import process_form_validation_errors as process_form_validation_errors

BannerContainerMapping: TypeAlias = dict[str, BannerContainer]
LabelVisibility: TypeAlias = Literal['visible', 'hidden', 'collapsed']
