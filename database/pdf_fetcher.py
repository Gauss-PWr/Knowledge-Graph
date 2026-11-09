import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import SessionLocal
from database.models import Books


def fetch_pdf():
    """Yields (title, pdf_bytes) for every book in the 'books' table."""
    with SessionLocal() as session:
        print("Started downloading...")
        for book in session.query(Books):
            yield book.title, book.pdf
        print(f'Downloaded {book.title}')


if __name__ == "__main__":
    for title, pdf in fetch_pdf():
        print(title, len(pdf))


