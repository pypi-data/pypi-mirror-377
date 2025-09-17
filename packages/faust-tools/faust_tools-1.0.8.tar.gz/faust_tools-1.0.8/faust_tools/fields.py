from collections.abc import Iterable
from typing import Any

from faust.exceptions import ValidationError
from faust.models import FieldDescriptor


class ChoiceField(FieldDescriptor[str]):
    def __init__(self, choices: list[str], **kwargs: Any) -> None:
        self.choices = choices
        # Must pass any custom args to init,
        # so we pass the choices keyword argument also here.
        super().__init__(choices=choices, **kwargs)

    def validate(self, value: str) -> Iterable[ValidationError]:
        if value not in self.choices:
            choices = ", ".join(self.choices)
            yield self.validation_error(f"{self.field} must be one of {choices}")
