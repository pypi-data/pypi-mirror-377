import datetime

from sqlalchemy import String, func, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from sqlalchemy_utils.types import UUIDType


class Base(AsyncAttrs, DeclarativeBase):
    """Base model"""

    pass


class PublishingActor(Base):
    __tablename__ = "html_display_publishing_actor"

    id: Mapped[int] = mapped_column(primary_key=True)

    actor: Mapped[str] = mapped_column(String(256))
    name: Mapped[str] = mapped_column(String(256), unique=True)


class PublishedObject(Base):
    """HTML display object in the database"""

    __tablename__ = "html_display_stored_object"
    """name of the table"""

    id: Mapped[bytes] = mapped_column(UUIDType(binary=True), primary_key=True)
    """The id (uuid as bytes)"""
    data: Mapped[dict] = mapped_column(JSON)
    """The object as JSON"""
    actor: Mapped[str] = mapped_column()
    """The actor that created the object"""
    create_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    """The create timestamp"""
