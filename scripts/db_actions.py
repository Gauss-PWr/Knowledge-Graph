import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import get_db_connection
from database.pdf_uploader import PdfUploader
from database.models import Base

engine = get_db_connection()
#PdfUploader().add_to_db() 

Base.metadata.create_all(engine)