from fastapi import Request


def dashboard(request: Request):
    for contextable in contextables:
        contextable.use_context(ctx)


def index(request: Request):
    ...


def detail(request: Request):
    ...


def new(request: Request):
    ...


def create(request: Request):
    ...


def destroy(request: Request):
    ...


def edit(request: Request):
    ...


def update(request: Request):
    ...
