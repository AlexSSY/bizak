from typing import List, Callable, Optional


class Widget:
    """
    Задачи:
    1. Хранение данных касающихся отрисовка поля
    """
    def __init__(
        self,
        template: str,
    ):
        self.template = template


class TextWidget(Widget):
    ...


class Field:
    """
    Задачи:
    1. Нормализация
    2. Валидация
    3. Хранение конекста касающиегося данных
    """
    def __init__(
        self,
        name: Optional[str] = None,
        validators: List[Callable] = [],
        widget: Widget = TextWidget,
    ):
        self.name = name
        self.validators = validators

    def _normalize(self):
        """Нормализирует данные например '  uSeR@mail.COM' -> 'user@mail.com"""

    def __str__(self) -> str:
        return '<doc>Rendred HTML</doc>'
