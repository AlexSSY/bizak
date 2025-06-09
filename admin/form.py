from marshmallow import Schema


class Form:

    @classmethod
    def from_marshmallow(cls, schema: Schema):
        ...