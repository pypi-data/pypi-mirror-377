from typing import Any, cast

from pydantic import Field

from bear_dereth.config._settings_manager._base_classes import Document
from bear_dereth.config._settings_manager._common import TypeList, ValueType
from bear_dereth.freezing import FrozenModel


class SettingsRecord[Value_T: ValueType](FrozenModel):
    """Pydantic model for a settings record."""

    key: str = Field(default=...)
    value: Value_T = Field(default=...)
    type: TypeList = Field(default="null")

    def model_post_init(self, context: Any) -> None:
        """Post-initialization to set the type based on the value."""
        match self.value:
            case None:
                self.type = "null"
            case bool():
                self.type = "boolean"
            case int():
                self.type = "number"
            case float():
                self.type = "float"
            case str():
                self.type = "string"
            case list():
                self.type = "list"
            case _:
                raise ValueError(f"Unsupported value type: {type(self.value)}")
        super().model_post_init(context)

    def __hash__(self) -> int:
        """Hash based on a frozen representation of the model."""
        return self.get_hash()

    def get_document(self) -> Document:
        """Get a dictionary representation of the record."""
        return cast("Document", self.model_dump(frozen=False))  # type: ignore[return-value]
