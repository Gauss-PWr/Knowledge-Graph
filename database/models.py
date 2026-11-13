from sqlalchemy.orm import declarative_base, deferred
from sqlalchemy import String, Integer, Column, LargeBinary, ARRAY, ForeignKey, Text, UniqueConstraint

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
    pdf = deferred(Column(LargeBinary))
    md = deferred(Column(LargeBinary))
