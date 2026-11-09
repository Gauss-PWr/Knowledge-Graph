from sqlalchemy.orm import declarative_base, deferred
from sqlalchemy import String, Integer, Column, LargeBinary

"""Jednorazowe tworzenie tabel"""
Base = declarative_base()

# class Chunks(Base):
#     __tablename__ = 'chunks'


class Books(Base):
    __tablename__ = 'books'
    book_id = Column(Integer, primary_key = True)
    title = Column(String)
    pdf = deferred(Column(LargeBinary))
