r"""The core component that includes all component translation models."""

# Local
from cambiato.models.core import BaseModel

from .buttons import Buttons
from .dataframes import DataFrames
from .forms import Forms


class Components(BaseModel):
    r"""The translations of the components."""

    buttons: Buttons
    dataframes: DataFrames
    forms: Forms
