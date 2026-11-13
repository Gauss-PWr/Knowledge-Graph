import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.pdf_uploader import PdfUploader

if __name__ == "__main__":
    uploader = PdfUploader()
    uploader.add_to_db()