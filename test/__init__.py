from sqlalchemy import and_, or_
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import aliased

from sqlalchemy_query_addons import select
from test.models import Producer, Song, Album, Artist, Collab


def run():
    collab2 = aliased(Collab, name="collab2")
    qsub = (
        select(Artist.name).filter(Artist.name.contains("Hello World")).subquery("qsub")
    )
    qs = (
        select(Album.title)
        .join(Album.songs)
        .join(Song.producer)
        .join(Album.artist)
        .join(qsub, Artist.name == qsub.c.name)
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
                collab2.name.contains("Foo"),
            )
        )
        .order_by(Artist.name, Collab.name)
    )
    print(qs.compile(dialect=postgresql.dialect()))


if __name__ == "__main__":
    run()
