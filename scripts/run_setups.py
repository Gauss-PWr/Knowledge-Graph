"""
Run every setup in SETUPS on the same test pages, one after another.

Folder layout (all on the same level as scripts/):
    papers/                                   input PDFs
    papers_md/<setup>/<file>.p<pages>.md      Markdown per setup
    papers_json/<setup>/<file>.p<pages>.json  Marker JSON per setup
    setup_guides_measurments_test_results/
        <run>_<setup>_report.json             settings, versions, per-file times
        <run>_summary.csv                     one row per setup (pages, seconds, s/page)
        <run>.log                             full log of the run
    (<run> = date and time the run started, so earlier results are never overwritten)

Marker's models are loaded once and shared by all setups. All setups here use
the same backend (vLLM); to compare llama.cpp or another Marker version, change
COMMON and run the script again in a new process.
"""
import csv
import logging
from datetime import datetime

from pdf_to_md_processing import PdfToMarkdownConverter, repo_root

PAPERS_DIR = repo_root / "papers"
MD_DIR = repo_root / "papers_md"
JSON_DIR = repo_root / "papers_json"
RESULTS_DIR = repo_root / "setup_guides_measurments_test_results"

RUN = datetime.now().strftime("%Y-%m-%d_%H%M")

# File (in papers/) -> pages, 0-based. Replace with your file names and pages.
TEST_PAGES = {
    "Boyd_Vandenberghe_Convex_Optimization.pdf": "154,166,169,239,256,272,670",
    "Prince_Understanding_Deep_Learning.pdf": "101-102,115,221,224,375,377",
    "Sutton_Barto_Reinforcement_Learning_2nd.pdf": "81,84,138,158,170,191",
    "L_pez_de_Prado_Advances_in_Financial_Machine_Learning.pdf": "103-104,106,197-198,240",
    "Strogatz_Nonlinear_Dynamics_and_Chaos.pdf": "60-61,71,147,163,194,281,332",
    "Karatzas_Shreve__Brownian_Motion_and_Stochastic_Calculus.pdf": "51,168,185,224,346",
}

# Settings shared by every setup.
COMMON = dict(
    input_dir=PAPERS_DIR,
    backend="vllm",          # NVIDIA server
    parallel=None,           # let Marker auto-scale
    overwrite_mds=True,      # always convert fresh
)

# Local OpenAI-compatible vision LLM, only for the LLM setup.
LLM = {
    "llm_service": "marker.services.openai.OpenAIService",
    "openai_base_url": "http://localhost:8081/v1",
    "openai_model": "local-vision-model",
    "openai_api_key": "none",
}

SETUPS = [
    {"name": "config1_balanced",        "add_config": {"mode": "balanced"}},
    {"name": "config2_force_ocr",       "add_config": {"mode": "balanced", "force_ocr": True}},
    {"name": "config3_fast_force_ocr",  "add_config": {"mode": "fast", "force_ocr": True}},
    {"name": "config4_force_ocr_strip", "add_config": {"mode": "balanced", "force_ocr": True,
                                                       "strip_existing_ocr": True}},
    # Needs the LLM server running - remove the # to include it:
    # {"name": "config5_force_ocr_llm", "add_config": {"mode": "balanced", "force_ocr": True,
    #                                                  "use_llm": True, "redo_inline_math": True, **LLM}},
]

if __name__ == "__main__":
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(),
                  logging.FileHandler(RESULTS_DIR / f"{RUN}.log", encoding="utf-8")])
    log = logging.getLogger("run_setups")

    rows = []
    artifacts = None
    for setup in SETUPS:
        name = setup["name"]
        log.info("=== %s", name)
        conv = PdfToMarkdownConverter(
            **COMMON,
            output_dir=MD_DIR / name,
            json_output_dir=JSON_DIR / name,
            add_config=setup["add_config"],
            artifacts=artifacts,
        )
        artifacts = conv._artifacts          # load Marker's models only once
        results = conv.convert(TEST_PAGES)
        conv.write_report(results, RESULTS_DIR / f"{RUN}_{name}_report.json")

        s = conv.summarize(results)
        rows.append({"setup": name, **s, "marker_config": setup["add_config"]})
        log.info("=== %s: %d converted, %d failed, %s s/page",
                 name, s["converted"], s["failed"], s["avg_sec_per_page"])

        # Summary rewritten after every setup, so it is there even if a later one crashes.
        with open(RESULTS_DIR / f"{RUN}_summary.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows({**r, "marker_config": {k: ("***" if "api_key" in k else v)
                                                for k, v in r["marker_config"].items()}}
                        for r in rows)

    log.info("Results: %s", RESULTS_DIR)