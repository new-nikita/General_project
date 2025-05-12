from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from core.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.like import Like


class LikeableEntity(Base):
    __table_args__ = {"extend_existing": True}

    type: Mapped[str] = mapped_column(String(50), nullable=False)

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "likeable_entity",
    }

    @declared_attr
    def likes(cls) -> Mapped[list["Like"]]:
        return relationship("Like", back_populates="target")
