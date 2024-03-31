from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Collab(Base):
    __tablename__ = "collab"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    producer_id: Mapped[int] = mapped_column(ForeignKey("producer.id"))


class Producer(Base):
    __tablename__ = "producer"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    songs: Mapped[list["Song"]] = relationship(back_populates="producer")


class Song(Base):
    __tablename__ = "song"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    length: Mapped[int]
    album_id: Mapped[int] = mapped_column(ForeignKey("album.id"))
    album: Mapped["Album"] = relationship(back_populates="songs")
    producer_id: Mapped[int] = mapped_column(ForeignKey("producer.id"))
    producer: Mapped[Producer] = relationship(back_populates="songs")


class Album(Base):
    __tablename__ = "album"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    songs: Mapped[list[Song]] = relationship(back_populates="album")
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    artist: Mapped["Artist"] = relationship(back_populates="albums")


class Artist(Base):
    __tablename__ = "artist"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    albums: Mapped[list[Album]] = relationship(back_populates="artist")
