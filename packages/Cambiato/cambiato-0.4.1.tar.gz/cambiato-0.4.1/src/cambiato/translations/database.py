r"""The translation models for the default data in the database."""

# Local
from cambiato.models.core import BaseModel


class Translatable(BaseModel):
    r"""A translation of a database object."""

    name: str
    description: str


class Database(BaseModel):
    r"""The translations of the default data in the database."""

    order_status: dict[int, Translatable]
    order_type: dict[int, Translatable]
    role: dict[int, Translatable]
    utility: dict[int, Translatable]
