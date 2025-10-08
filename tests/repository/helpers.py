"""Модуль классов, необходимых для запуска тестов репо."""

from dataclasses import dataclass

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from weblite_framework.database.models import BaseModel
from weblite_framework.repository.base import BaseRepositoryClass


class SampleModel(BaseModel):
    """Класс ORM модели для проведения тестов.

    Args:
        id_: Уникальный идентификатор
        name: Название записи

    Returns:
        SQLModel: Дочерний класс BaseModel
    """

    __tablename__ = 'sample_table'

    id_: Mapped[int] = mapped_column(
        name='id',
        type_=Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        name='name',
        type_=String(length=255),
    )


@dataclass
class SampleDTO:
    """Класс DTO для проведения тестов.

    Attributes:
        id_: Уникальный идентификатор
        name: Название записи
    """

    id_: int
    name: str


class SampleRepo(BaseRepositoryClass[SampleDTO, SampleModel]):
    """Дочерний класс базового репозитория для проведения тестов."""

    def _model_to_dto(
        self,
        model: SampleModel,
    ) -> SampleDTO:
        return SampleDTO(
            id_=model.id_,
            name=model.name,
        )

    def _dto_to_model(
        self,
        dto: SampleDTO,
    ) -> SampleModel:
        return SampleModel(
            id_=dto.id_,
            name=dto.name,
        )
