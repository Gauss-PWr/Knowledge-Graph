import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path
from database.connection import SessionLocal
from database.models import Books
import json

BASE_DIR = Path(__file__).resolve().parent.parent


class PdfUploader:
    """
    Uploads PDF files (plus their markdown, if it exists) to the 'books' table.

    Title = PDF file name without '.pdf'. The matching markdown is
    papers_md/<md_config>/<title>.md. Books already in the table are skipped.
    """
    def __init__(self, md_config: str = 'config_final', require_md: bool = False):
        self.papers_location = BASE_DIR / 'papers'
        self.papers_location_md = BASE_DIR / 'papers_md' / md_config
        self.require_md = require_md

    def add_to_db(self, only: list[str] | None = None):
        files = {f.stem: f for f in sorted(self.papers_location.glob('*.pdf'))}
        files_md = {f.stem: f for f in self.papers_location_md.glob('*.md')}

        if only:
            files = {t: f for t, f in files.items() if t in only}
            for name in set(only) - files.keys():
                print(f"Nie znaleziono PDF: {name}")

        with SessionLocal() as session:
            existing = {t for (t, ) in session.query(Books.title)}
            new_titles = sorted(files.keys() - existing)
            missing = self.check_similarities(new_titles, files_md)

            skipped_existing = len(files) - len(new_titles)
            if skipped_existing:
                print(f"Pominięto {skipped_existing} książek, które już są w bazie.")
            if not new_titles:
                print("Nic nowego do wysłania.")
                return

            print(f"Wysyłam {len(new_titles)} PDF(ów)...")
            uploaded, failed = 0, []
            for i, title in enumerate(new_titles, 1):
                if title in missing and self.require_md:
                    continue
                pdf_path = files[title]
                md_path = files_md.get(title)
                size_mb = pdf_path.stat().st_size / 1_048_576
                try:
                    session.add(Books(
                        title=title,
                        pdf=pdf_path.read_bytes(),
                        md=md_path.read_text(encoding="utf-8") if md_path else None,
                    ))
                    session.commit()
                    uploaded += 1
                    md_note = "+ md" if md_path else "bez md"
                    print(f"[{i}/{len(new_titles)}] OK  {title} ({size_mb:.1f} MB, {md_note})")
                except Exception as e:
                    session.rollback()
                    failed.append(title)
                    print(f"[{i}/{len(new_titles)}] BŁĄD {title}: {e}")

            print(f"\nGotowe: wysłano {uploaded}, błędy {len(failed)}.")
            if missing:
                label = 'Nie dodano (brak .md)' if self.require_md else 'Dodano bez .md'
                print(f"{label}:")
                for m in sorted(missing):
                    print(f" - {m}")
            if failed:
                print("Nie udało się wysłać:")
                for f in failed:
                    print(f" - {f}")

    @staticmethod
    def check_similarities(new_titles, files_md):
        """Titles that have no matching markdown file."""
        return {t for t in new_titles if t not in files_md}
