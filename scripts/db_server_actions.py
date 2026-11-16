import logging
import signal
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
SQL_PATH = Path(__file__).resolve().parent.parent / 'sql'
CLAIM_JOB = text((SQL_PATH / 'claim_book.sql').read_text(encoding='utf-8'))
SEND_MD = text((SQL_PATH / 'send_md.sql').read_text(encoding='utf-8'))
CONVERSION_OK = text((SQL_PATH / 'conversion_ok.sql').read_text(encoding='utf-8'))
CONVERSION_FAILED = text((SQL_PATH / 'conversion_failed.sql').read_text(encoding='utf-8'))
RESET_STALE = text("UPDATE book_report SET status = 'failed', error = 'stale', finished_at = now() WHERE status = 'running' AND started_at < now() - interval '2 hours'")

from database.connection import get_db_connection
from pdf_to_md_processing import PdfToMarkdownConverter
engine = get_db_connection()
MAX_FAILS_IN_A_ROW = 2
log = logging.getLogger("worker")


def claim_book():
    with engine.begin() as conn:
        row = conn.execute(CLAIM_JOB).first()
    if row is None:
        return None
    return row.raport_id, row.book_id, row.title, row.pdf


def _no_nul(s):
    """Postgres text/jsonb cannot store NUL characters."""
    return None if s is None else s.replace("\x00", "").replace("\\u0000", "")


def run_worker_pdf_to_md():
    with engine.begin() as conn:
        conn.execute(RESET_STALE)

    converter = PdfToMarkdownConverter('config_final')
    fails_in_a_row = 0

    while (job := claim_book()) is not None:
        raport_id, book_id, title, pdf = job
        log.info("Claimed book %s (%s), report %s", book_id, title, raport_id)
        try:
            result = converter.convert_pdf(pdf, name=title) #res.markdown, res.json_text, res.pages, res.seconds, res.sec_per_page, res.warnings
            if any("400 Bad Request" in w for w in result.warnings):
                raise RuntimeError("Probably OCR requests rejected")

            with engine.begin() as conn:
                conn.execute(SEND_MD, {"md": _no_nul(result.markdown), "marker_json": _no_nul(result.json_text), "book_id": book_id})
                conn.execute(CONVERSION_OK, {"raport_id": raport_id, "pages": result.pages, "seconds": result.seconds, "seconds_per_page": result.sec_per_page})
            fails_in_a_row = 0

        except BaseException as e:
            log.exception("Book %s (%s) failed", book_id, title)
            with engine.begin() as conn:
                conn.execute(CONVERSION_FAILED, {"raport_id": raport_id, "error": f"{type(e).__name__}: {e}"[:2000]})
            if not isinstance(e, Exception):
                raise
            fails_in_a_row += 1
            if fails_in_a_row >= MAX_FAILS_IN_A_ROW:
                log.error("%d failures in a row, stopping", fails_in_a_row)
                break
    log.info("Worker finished")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    run_worker_pdf_to_md()
