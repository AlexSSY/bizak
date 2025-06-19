"""
Plugin structure:
    __init__.py
    models.py
        отсюда импортируются все подклассы ModelAdmin
    routes.py
        отсюда импортируется и подключается 'api_router: APIRouter'
    middlewares.py
"""