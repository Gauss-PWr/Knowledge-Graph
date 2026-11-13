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
        self.papers_location_md = BASE_DIR / 'papers_md'


    def add_to_db(self):
        files = {f.stem: f for f in self.papers_location.glob('*.pdf')}
        files_md = {f_md.stem: f_md for f_md in self.papers_location_md.glob('*.md')}

        with SessionLocal() as session:
            print("Started uploading pdfs and mds...")
            existing = {t for (t, ) in session.query(Books.title)}
            new_titles = files.keys() - existing
            missing = self.check_similarities(new_titles, files_md)
            for title in new_titles:
                if not title in missing:
                    session.add(Books(title=title, pdf=files[title].read_bytes(), md=files_md[title].read_bytes()))
                    session.commit()
                    print(f"Uploaded: {title}")
            if not missing:
                print("Done.")
            else:
                print('Nie dodano ksiązki:')
                for m in missing:
                    print(f' - {m}.')

    @staticmethod
    def check_similarities(new_titles, files_md):
        missing = set()
        for f in new_titles:
            if not f in files_md.keys():

                missing.add(f)
        return missing












