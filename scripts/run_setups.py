"""
Compare Marker setups on test pages. Optional tool for experiments only:
the pipeline itself takes PDFs from the database and calls
PdfToMarkdownConverter.convert_pdf() directly, without this script.

Use it when something changes (new Marker version, new config idea) and you
want to compare setups on the same pages again.

Reads local PDFs from papers/ and writes into local_runs/<run>/ (keep that
folder out of git: it contains book text):
    local_runs/<run>/<setup>/<file><.pPAGES>.md / .json
    local_runs/<run>/<setup>_report.json      settings, versions, per-file results
    local_runs/<run>/summary.csv              one row per setup
    local_runs/<run>/run.log                  full log
"""
import csv
import json
import logging
from datetime import datetime

from pdf_to_md_processing import CONFIGS, PdfToMarkdownConverter, page_tag, parse_pages, repo_root

PAPERS_DIR = repo_root / "papers"
RUN = datetime.now().strftime("%Y-%m-%d_%H%M")
RUN_DIR = repo_root / "local_runs" / RUN

# File (in papers/) -> pages, 0-based ("all" = whole book).
TEST_PAGES = {
    "Boyd_Vandenberghe_Convex_Optimization.pdf": "154,166,169,239,256,272,670",
    "Prince_Understanding_Deep_Learning.pdf": "101-102,115,221,224,375,377",
    "Sutton_Barto_Reinforcement_Learning_2nd.pdf": "81,84,138,158,170,191",
    "Strogatz_Nonlinear_Dynamics_and_Chaos.pdf": "60-61,71,147,163,194,281,332",
}

# Setups to compare: names from CONFIGS in pdf_to_md_processing.py.
SETUPS = ["config_final", "config2_force_ocr"]

COMMON = dict(backend="vllm", parallel=None)

if __name__ == "__main__":
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(RUN_DIR / "run.log", encoding="utf-8")])
    log = logging.getLogger("run_setups")

    rows, artifacts = [], None
    for setup in SETUPS:
        log.info("=== %s %s", setup, CONFIGS[setup])
        conv = PdfToMarkdownConverter(setup, artifacts=artifacts, **COMMON)
        artifacts = conv.artifacts                      # load Marker's models only once

        files = []
        for file_name, pages in TEST_PAGES.items():
            try:
                res = conv.convert_pdf(PAPERS_DIR / file_name, pages=pages)
                stem = file_name.rsplit(".", 1)[0] + page_tag(parse_pages(pages))   # Boyd.p154_166
                res.save(RUN_DIR / setup, stem)
                files.append({"status": "converted", **res.to_dict()})
            except Exception as e:  # noqa: BLE001 - one bad PDF must not stop the comparison
                log.exception("%s: failed", file_name)
                files.append({"status": "failed", "name": file_name, "error": f"{type(e).__name__}: {e}"})

        done = [f for f in files if f["status"] == "converted"]
        pages_total = sum(f["pages"] for f in done)
        secs_total = round(sum(f["seconds"] for f in done), 2)
        summary = {"setup": setup, "converted": len(done), "failed": len(files) - len(done),
                   "pages": pages_total, "seconds": secs_total,
                   "sec_per_page": round(secs_total / pages_total, 2) if pages_total else None,
                   "warnings": sum(len(f["warnings"]) for f in done)}
        (RUN_DIR / f"{setup}_report.json").write_text(
            json.dumps({"settings": conv.settings, "summary": summary, "files": files},
                       indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append(summary)
        log.info("=== %s: %s", setup, summary)

        # Rewritten after every setup, so it is there even if a later one crashes.
        with open(RUN_DIR / "summary.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    log.info("Results: %s", RUN_DIR)
