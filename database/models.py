from sqlalchemy.orm import declarative_base, deferred
from sqlalchemy import String, Integer, Column, LargeBinary, ARRAY, ForeignKey, Text, UniqueConstraint, CheckConstraint, Float, Index, text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB


"""Jednorazowe tworzenie tabel"""
Base = declarative_base()

class Chunks(Base):
    __tablename__ = 'chunks'
    chunk_id = Column(Integer, primary_key = True, nullable = False)
    book_id = Column(Integer, ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False)
    chunk_index = Column(Integer, nullable = False)
    section = Column(String)
    page = Column(Integer)
    kind = Column(String, nullable = False)
    number = Column(String)
    title = Column(String)
    text = Column(Text, nullable = False)
    embed_text = Column(Text)
    refs = Column(ARRAY(Integer))

    __table_args__ = (UniqueConstraint('book_id', 'chunk_index'),)

class Books(Base):
    __tablename__ = 'books'
    book_id = Column(Integer, primary_key = True)
    title = Column(String, unique = True, nullable = False)
    pdf = deferred(Column(LargeBinary, nullable=False))
    md = deferred(Column(Text))
    marker_json = deferred(Column(JSONB)) 


class BookRaport(Base):
    __tablename__ = 'book_report'
    raport_id = Column(Integer, primary_key = True, nullable = False)
    book_id = Column(Integer, ForeignKey('books.book_id', ondelete = 'RESTRICT'), nullable = False)
    status = Column(String, nullable=False)
    pages = Column(Integer)
    seconds = Column(Float)
    seconds_per_page = Column(Float)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at = Column(DateTime(timezone=True))
    error = Column(Text)
    config_name = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('running', 'converted', 'failed')", name="status_valid"),
        Index("one_active_report", "book_id", "config_name", unique=True, postgresql_where=text("status IN ('running', 'converted')")),
    )
    
