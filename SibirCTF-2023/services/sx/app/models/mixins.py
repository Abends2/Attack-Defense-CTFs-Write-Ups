from sqlalchemy import inspect
from sqlalchemy.future import select

from app.configs import RESPONSE_ITEMS_LIMIT
from app.db import execute_command


class ModelMixin:
    @property
    def __attrs(self):
        return (x.key for x in inspect(self.__class__).attrs)

    def to_dict(self):
        return dict((x, getattr(self, x)) for x in self.__attrs)

    @classmethod
    async def get_all(cls, *args, **kwargs):
        expressions = tuple(
            getattr(cls, kwarg_key) == kwarg_value
            for kwarg_key, kwarg_value in kwargs.items()
        )
        query = select(cls).where(*expressions)

        if hasattr(cls, "created_at"):
            query = query.order_by(getattr(cls, "created_at").desc())

        query = query.limit(RESPONSE_ITEMS_LIMIT)
        return list((await execute_command(query)).scalars())

    @classmethod
    async def get(cls, *args, **kwargs):
        instances = await cls.get_all(**kwargs)
        return instances[0] if instances else None
