
import argparse
import sys
from pathlib import Path
from sqlalchemy import text

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from database.connection import get_db_connection

SEND_JSON = text("""
UPDATE books SET marker_json = CAST(:marker_json AS jsonb)
WHERE title = :title AND pdf IS NOT NULL AND md IS NOT NULL
  AND (marker_json IS NULL OR :overwrite)
RETURNING book_id
""")

parser = argparse.ArgumentParser()
parser.add_argument("--config", default="config_final")
parser.add_argument("--overwrite", action="store_true")
args = parser.parse_args()

engine = get_db_connection()
with engine.connect() as conn:
    books = {t: (has_md, has_json) for t, has_md, has_json in conn.execute(text(
        "SELECT title, md IS NOT NULL, marker_json IS NOT NULL FROM books"))}

sent, skipped = 0, []
for path in sorted((REPO / "papers_json" / args.config).glob("*.json")):
    title = path.stem
    if title not in books:
        skipped.append(f"{title}: not in db")
        continue
    has_md, has_json = books[title]
    if not has_md:
        skipped.append(f"{title}: no md in db")
        continue
    if has_json and not args.overwrite:
        skipped.append(f"{title}: already has json (use --overwrite)")
        continue
    data = path.read_text(encoding="utf-8").replace("\\u0000", "")   # jsonb rejects \u0000
    try:
        with engine.begin() as conn:
            conn.execute(SEND_JSON, {"marker_json": data, "title": title, "overwrite": args.overwrite})
        sent += 1
        print(f"OK   {title} ({len(data) / 1_048_576:.1f} MB)")
    except Exception as e:
        skipped.append(f"{title}: ERROR {str(e).splitlines()[0]}")

print(f"\nSent {sent}, skipped {len(skipped)}")
for s in skipped:
    print(" -", s)
