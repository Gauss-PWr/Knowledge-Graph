import os
from chunker.pdf_marker_to_js import PdfChunker

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, "papers_samples")
OUT = os.path.join(ROOT, "papers_json")

PDF_NAME = "rozdzial2.pdf"
BOOK_NAME = "rozdzial2"
SAVE_NAME = "rozdzial2"

pdf_path = os.path.join(SAMPLES, PDF_NAME)
os.makedirs(OUT, exist_ok=True)

ch = PdfChunker(force_ocr=True)
chunks = ch.chunk_pdf(pdf_path, book=BOOK_NAME, book_id=1)
ch.save(chunks, os.path.join(OUT, f"{SAVE_NAME}.json"))
print(ch.last_timing)