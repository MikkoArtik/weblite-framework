"""Модуль вспомогательного класса для тестов базовой Pydantic модели."""

from pydantic import EmailStr, Field

from weblite_framework.schemas.base import CustomBaseModel

__all__ = [
    'UserSchemaExample',
]


class UserSchemaExample(CustomBaseModel):
    """Пример Pydantic модели пользователя для тестов."""

    id_: int = Field(
        alias='id',
        description='ID пользователя',
        examples=[1],
    )
    email: EmailStr = Field(
        alias='email',
        description='Email',
        examples=['a@b.c'],
    )
