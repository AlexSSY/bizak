class Widget:
    """
    Задачи:
    1. Хранение данных касающихся отрисовка поля
    """
    def __init__(
        self,
        template_name: str,
        attrs: dict = {}
    ):
        self.template_name = template_name

    def render(self, templating, name, value, **attrs) -> str:
        template = templating.get_template(self.template_name)
        context = self.get_context()
        return template.render(context)
    
    def get_context(self):
        return {
            'widget': {
                'template_name': self.template_name
            }
        }


class TextWidget(Widget):
    ...