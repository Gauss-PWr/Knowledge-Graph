import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path
from database.connection import SessionLocal
from database.models import Books

BASE_DIR = Path(__file__).resolve().parent.parent


class PdfUploader:
    """
    Uploads PDF files to the 'books' table in the database.
    """
    def __init__(self):
        self.papers_location = BASE_DIR / 'papers'

    def add_to_db(self):
        files = {f.stem: f for f in self.papers_location.glob('*.pdf')}

        with SessionLocal() as session:
            print("Started uploading pdfs...")
            existing = {t for (t, ) in session.query(Books.title)}
            new_titles = files.keys() - existing

            for title in new_titles:
                session.add(Books(title=title, pdf=files[title].read_bytes()))
                session.commit()
                print(f"Uploaded: {title}")
            print("Done.")








