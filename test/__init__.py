from sqlalchemy import ForeignKey, and_, or_
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, aliased

from sqlalchemy_query_addons import select


class Base(DeclarativeBase):
    pass


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


class Collab(Base):
    __tablename__ = "collab"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    producer_id: Mapped[int] = mapped_column(ForeignKey("producer.id"))


def run():
    collab2 = aliased(Collab, name="collab2")
    qs = (
        select(Album.title)
        .join(Album.songs)
        .join(Song.producer)
        .join(Album.artist)
        .join(
            Collab,
            and_(Artist.id == Collab.artist_id, Producer.id == Collab.producer_id),
            isouter=True,
        )
        .join(
            collab2,
            and_(Artist.id == collab2.artist_id, Producer.id == collab2.producer_id),
            isouter=True,
        )
        .filter(
            or_(
                Producer.name.contains("Hello World"),
                Album.title.contains("Goodbye"),
                Collab.name.contains("Foo"),
            )
        )
        .order_by(Artist.name, collab2.name)
    )
    print(qs.compile(dialect=postgresql.dialect()))


if __name__ == "__main__":
    run()
