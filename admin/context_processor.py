from abc import ABC, abstractmethod


class ContextProcessor:
    def __init__(self, obj):
        self.obj = obj

    @abstractmethod
    def process(self) -> dict[str, dict]:
        pass

    @abstractmethod
    def form_context(self) -> dict[str, dict]:
        pass


class ContextProcessorFactory:
    pass