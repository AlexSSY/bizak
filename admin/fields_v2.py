from typing import List, Callable, Optional

from .widgets_v2 import Widget, TextWidget


class Field:
    """
    Задачи:
    1. Нормализация
    2. Валидация
    3. Хранение контекста касающиегося данных
    """
    def __init__(
        self,
        name: Optional[str] = None,
        validators: List[Callable] = [],
        widget: Widget = TextWidget,
    ):
        self.name = name
        self.validators = validators

    def normalize(self, value):
        """Нормализирует данные например '  uSeR@mail.COM' -> 'user@mail.com"""
        return value # тут не нормализируем


class BoundField:
    """
    Предположительно контейнер содержащий данный и Field
    """
    def __init__(self, field: Field):
        self._field = field
