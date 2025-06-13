from typing import List, Callable


class Widget:
    def __init__(
        self,
        template: str,
    ):
        self.template = template


class TextWidget(Widget):
    ...


class Field:
    def __init__(
        self,
        name: str,
        validators: List[Callable],
        widget: Widget = TextWidget,
    ):
        self.name = name
        self.validators = validators

    def __str__(self) -> str:
        return '<doc>Rendred HTML</doc>'
