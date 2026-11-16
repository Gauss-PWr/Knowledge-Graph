"""
PDF -> Markdown + Marker JSON, as a library to call from other scripts.

Nothing here reads folders or writes outputs on its own. You pass a PDF
(bytes from the database, or a path) and get the results back in memory:

    from pdf_to_md_processing import PdfToMarkdownConverter

    conv = PdfToMarkdownConverter("config_final", backend="vllm", parallel=None)  # loads models once
    res = conv.convert_pdf(pdf_bytes, name="Boyd.pdf")    # raises on failure
    res.markdown        # str  -> books.md
    res.json_text       # str  -> Marker JSON for the chunker
    res.pages, res.seconds, res.sec_per_page, res.warnings
    conv.settings       # config + versions, for book_report

- Marker's models load once, in __init__, and are reused for every PDF.
- Marker builds each document once; Markdown and JSON are rendered from it.
- No print(): everything goes through `logging`; the caller decides where it goes.
- convert_pdf() raises when a PDF fails, so the caller can mark it as failed.

Page numbers are 0-based (same as Marker): pages="0-4,9" converts 6 pages.
"""
from __future__ import annotations

import inspect
import json
import logging
import os
import tempfile
import time
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Union

log = logging.getLogger(__name__)

repo_root = Path(__file__).resolve().parents[1]

PageSpec = Union[None, int, str, Sequence[Union[int, str]]]

# Named Marker setups. "config_final" is the one chosen for the pipeline;
# the others are kept so earlier test runs can be repeated (see run_setups.py).
CONFIGS: dict[str, dict] = {
    "config_final":            {"mode": "balanced", "force_ocr": True, "keep_pageheader_in_output": True},
    "config1_balanced":        {"mode": "balanced"},
    "config2_force_ocr":       {"mode": "balanced", "force_ocr": True},
    "config3_fast_force_ocr":  {"mode": "fast", "force_ocr": True},
    "config4_force_ocr_strip": {"mode": "balanced", "force_ocr": True, "strip_existing_ocr": True},
}

# Marker options accepted in a config. A typo like "force_orc" would otherwise
# be silently ignored by Marker. Check against `marker_single config --help`.
KNOWN_MARKER_KEYS = {
    "mode", "force_ocr", "strip_existing_ocr", "disable_ocr", "ocr_inline_math",
    "use_llm", "redo_inline_math", "llm_service",
    "openai_base_url", "openai_model", "openai_api_key", "ollama_base_url", "ollama_model",
    "extract_images", "paginate_output", "keep_pageheader_in_output", "keep_pagefooter_in_output",
}

MAX_WARNINGS = 200   # cap on log lines kept per conversion


# --------------------------------------------------------------------------- #
# Page parsing
# --------------------------------------------------------------------------- #
def parse_pages(spec: PageSpec) -> list[int] | None:
    """
    Turn a page selection into a sorted list of unique 0-based page numbers.

        5                 -> [5]
        "0,3,5-8"         -> [0, 3, 5, 6, 7, 8]
        [0, "3-5", 9]     -> [0, 3, 4, 5, 9]
        None / "" / "all" -> None  (all pages)
    """
    if spec is None:
        return None
    if isinstance(spec, bool):
        raise ValueError(f"Invalid page spec: {spec!r}")
    if isinstance(spec, int):
        parts: list[Any] = [spec]
    elif isinstance(spec, str):
        if spec.strip().lower() in ("", "all"):
            return None
        parts = spec.split(",")
    else:
        parts = list(spec)
        if not parts:
            return None

    pages: set[int] = set()
    for part in parts:
        if isinstance(part, bool):
            raise ValueError(f"Invalid page value: {part!r}")
        if isinstance(part, int):
            pages.add(part)
            continue
        text = str(part).strip()
        if not text:
            continue
        try:
            if "-" in text:
                start_s, end_s = text.split("-", 1)
                start, end = int(start_s), int(end_s)
                if start > end:
                    raise ValueError
                pages.update(range(start, end + 1))
            else:
                pages.add(int(text))
        except ValueError:
            raise ValueError(f"Invalid page range {text!r} in {spec!r}") from None

    result = sorted(pages)
    if result and result[0] < 0:
        raise ValueError(f"Page numbers must start at 0: {spec!r}")
    return result


def format_pages(pages: list[int] | None) -> str:
    """[0,1,2,5,7,8] -> '0-2,5,7-8' (compact form for logs and reports)."""
    if not pages:
        return "all"
    chunks, start, prev = [], pages[0], pages[0]
    for p in pages[1:] + [None]:
        if p is not None and p == prev + 1:
            prev = p
            continue
        chunks.append(str(start) if start == prev else f"{start}-{prev}")
        if p is not None:
            start = prev = p
    return ",".join(chunks)


def page_tag(pages: list[int] | None) -> str:
    """[154,160,161,162] -> '.p154_160-162' for file names; all pages -> ''."""
    return "" if not pages else ".p" + format_pages(pages).replace(",", "_")


# --------------------------------------------------------------------------- #
# Result
# --------------------------------------------------------------------------- #
@dataclass
class ConversionResult:
    name: str                       # file name / title, for logs
    config_name: str
    markdown: str | None            # None if "markdown" was not requested
    json_text: str | None           # Marker JSON as text; None if "json" was not requested
    pages: int                      # pages converted
    page_range: str                 # "all" or e.g. "0-4,9"
    seconds: float
    sec_per_page: float
    started_at: str                 # UTC, ISO format
    finished_at: str
    warnings: list[str] = field(default_factory=list)  # Marker/Surya warnings + failed OCR requests
    images: dict = field(default_factory=dict, repr=False)  # only with extract_images=True

    @property
    def json(self) -> dict | None:
        """Marker JSON parsed into a dict (parsed on each access, so keep the result)."""
        return None if self.json_text is None else json.loads(self.json_text)

    def to_dict(self, with_content: bool = False) -> dict:
        """Metadata as a dict (for reports / book_report). Content only if asked."""
        d = asdict(self)
        d.pop("images")
        if not with_content:
            d.pop("markdown")
            d.pop("json_text")
        return d

    def save(self, out_dir: Path | str, stem: str | None = None) -> dict[str, Path]:
        """Write <stem>.md / <stem>.json into out_dir (for local tests only)."""
        out_dir = Path(out_dir)
        stem = stem or Path(self.name).stem
        paths = {}
        if self.markdown is not None:
            paths["markdown"] = _atomic_write(out_dir / f"{stem}.md", self.markdown)
        if self.json_text is not None:
            paths["json"] = _atomic_write(out_dir / f"{stem}.json", self.json_text)
        return paths


def _atomic_write(path: Path, text: str) -> Path:
    """Write via a .tmp file so a reader never sees a half-written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)
    return path


def _versions() -> dict:
    from importlib.metadata import PackageNotFoundError, version
    out = {}
    for pkg in ("marker-pdf", "surya-ocr"):
        try:
            out[pkg] = version(pkg)
        except PackageNotFoundError:
            out[pkg] = None
    return out


def _page_count(pdf: Path) -> int | None:
    try:
        import pypdfium2 as pdfium   # installed with Marker
    except ImportError:
        return None
    doc = pdfium.PdfDocument(str(pdf))
    try:
        return len(doc)
    finally:
        doc.close()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class _WarningCollector(logging.Handler):
    """
    Collects, during one conversion, what the caller should know about:
    WARNING+ messages (e.g. 'Equation recognition failed for /page/154/Equation/7')
    and OCR requests that did not return 200 (e.g. '400 Bad Request').
    The request lines are logged by httpx at INFO, so they are only seen when the
    caller's logging level is INFO or lower (logging.basicConfig(level=logging.INFO)).
    """
    def __init__(self):
        super().__init__(level=logging.INFO)
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = record.getMessage()
        except Exception:  # noqa: BLE001
            return
        failed_request = record.name.startswith("httpx") and "HTTP Request" in msg and " 200 " not in msg
        if (record.levelno >= logging.WARNING or failed_request) and len(self.messages) < MAX_WARNINGS:
            self.messages.append(f"{record.levelname} {record.name}: {msg}")


# --------------------------------------------------------------------------- #
# Converter
# --------------------------------------------------------------------------- #
class PdfToMarkdownConverter:
    """
    Load once, then call convert_pdf() for each PDF.

    config_name  a key of CONFIGS ("config_final" by default), or any label
                 when you pass the Marker options yourself in add_config.
    add_config   Marker options; overrides/extends the named config.
    """

    def __init__(
        self,
        config_name: str = "config_final",
        add_config: dict | None = None,
        output_formats: Sequence[str] = ("markdown", "json"),
        disable_image_extraction: bool = True,
        # marker / inference settings
        backend: str = "vllm",
        inference_url: str | None = None,   # existing server, e.g. http://localhost:8765/v1
        vllm_gpus: str | None = None,       # e.g. "0"
        llama_cpp_binary: str | None = None,
        parallel: int | None = None,        # None = let Marker auto-scale
        keep_alive: bool = False,
        hf_home: str | None = None,
        artifacts: dict | None = None,      # reuse loaded Marker models from another converter
    ):
        if add_config is None and config_name not in CONFIGS:
            raise ValueError(f"Unknown config_name {config_name!r}; known: {sorted(CONFIGS)}, "
                             "or pass the Marker options in add_config")
        self.config_name = config_name
        self.output_formats = tuple(dict.fromkeys(output_formats))
        bad = set(self.output_formats) - {"markdown", "json"}
        if bad or not self.output_formats:
            raise ValueError(f"output_formats must be 'markdown' and/or 'json', got {list(output_formats)}")

        # Environment must be set BEFORE marker/surya are imported.
        self._set_env(backend, inference_url, vllm_gpus, llama_cpp_binary, parallel, keep_alive, hf_home)

        # "disable_image_extraction" is only understood by Marker's CLI;
        # the renderers read "extract_images".
        options = dict(CONFIGS.get(config_name, {}))
        options.update(add_config or {})
        options.pop("page_range", None)       # pages are chosen per PDF in convert_pdf()
        unknown = set(options) - KNOWN_MARKER_KEYS
        if unknown:
            raise ValueError(f"Unknown Marker options: {sorted(unknown)}")
        if options.get("redo_inline_math") and not options.get("use_llm"):
            raise ValueError("redo_inline_math needs use_llm=True")
        if options.get("use_llm") and not options.get("llm_service"):
            raise ValueError("use_llm=True needs llm_service, otherwise Marker silently uses Gemini")
        self.base_config: dict = {"extract_images": not disable_image_extraction, **options}

        # What exactly produces the outputs (store it with every result).
        self.settings = {
            "config_name": config_name,
            "marker_config": {k: ("***" if "api_key" in k else v) for k, v in self.base_config.items()},
            "output_formats": list(self.output_formats),
            "backend": backend,
            "parallel": parallel,
            "versions": _versions(),
        }

        # Slow part: loading Marker's models. Done once, reused for every PDF.
        t0 = time.perf_counter()
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered
        from marker.renderers.json import JSONRenderer
        from marker.renderers.markdown import MarkdownRenderer

        self._PdfConverter = PdfConverter
        self._text_from_rendered = text_from_rendered
        self._renderers = {"markdown": MarkdownRenderer, "json": JSONRenderer}
        self._artifacts = artifacts if artifacts is not None else create_model_dict()
        self._converters: dict[tuple[int, ...] | None, Any] = {}
        self.model_load_seconds = round(time.perf_counter() - t0, 2)
        log.info("Marker models loaded in %.1f s (config %s)", self.model_load_seconds, config_name)

    # ------------------------------------------------------------------ #
    @classmethod
    def from_config(cls, config: Mapping | str | Path, **overrides) -> "PdfToMarkdownConverter":
        """
        Build a converter from a dict or a .yaml/.yml/.json file.
        Keyword overrides win over values from the config.
        Unknown keys raise ValueError (catches typos in config files).
        """
        if isinstance(config, (str, Path)):
            path = Path(config)
            text = path.read_text(encoding="utf-8")
            if path.suffix.lower() in (".yaml", ".yml"):
                import yaml
                data = yaml.safe_load(text) or {}
            elif path.suffix.lower() == ".json":
                data = json.loads(text)
            else:
                raise ValueError(f"Unsupported config format: {path.suffix}")
        else:
            data = dict(config)
        data.update(overrides)

        allowed = set(inspect.signature(cls.__init__).parameters) - {"self"}
        unknown = set(data) - allowed
        if unknown:
            raise ValueError(f"Unknown config keys: {sorted(unknown)}. Allowed: {sorted(allowed)}")
        return cls(**data)

    @property
    def artifacts(self) -> dict:
        """Loaded Marker models; pass to another converter to avoid loading them twice."""
        return self._artifacts

    @staticmethod
    def _set_env(backend, inference_url, vllm_gpus, llama_cpp_binary, parallel, keep_alive, hf_home):
        os.environ["SURYA_INFERENCE_BACKEND"] = backend
        if inference_url:
            os.environ["SURYA_INFERENCE_URL"] = inference_url
        if vllm_gpus is not None:
            os.environ["VLLM_GPUS"] = str(vllm_gpus)
        os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
        if keep_alive:
            os.environ["SURYA_INFERENCE_KEEP_ALIVE"] = "1"
        if parallel is not None:
            os.environ["SURYA_INFERENCE_PARALLEL"] = str(parallel)
        if llama_cpp_binary:
            os.environ["LLAMA_CPP_BINARY"] = str(Path(llama_cpp_binary).expanduser())
        if hf_home:
            os.environ["HF_HOME"] = str(Path(hf_home).expanduser())

    def _converter_for(self, pages: list[int] | None):
        """One PdfConverter per distinct page selection; models are shared."""
        key = tuple(pages) if pages else None
        if key not in self._converters:
            config = dict(self.base_config)
            if pages:
                config["page_range"] = list(pages)
            llm_service = config.get("llm_service") if config.get("use_llm") else None
            self._converters[key] = self._PdfConverter(
                artifact_dict=self._artifacts, config=config, llm_service=llm_service
            )
        return self._converters[key]

    # ------------------------------------------------------------------ #
    # Conversion
    # ------------------------------------------------------------------ #
    def convert_pdf(self, pdf: bytes | bytearray | memoryview | Path | str, name: str | None = None,
                    pages: PageSpec = None, formats: Sequence[str] | None = None) -> ConversionResult:
        """
        Convert one PDF and return the results in memory.

        pdf      the PDF content (bytes, e.g. books.pdf from the database) or a path
        name     label for logs/results; defaults to the file name, or "pdf" for bytes
        pages    0-based selection, e.g. "0-4,9"; None/"all" = every page
        formats  subset of output_formats, e.g. ("json",)

        Raises on any failure (unreadable PDF, OCR server down, bad page range).
        """
        formats = tuple(formats or self.output_formats)
        unknown = set(formats) - set(self._renderers)
        if unknown:
            raise ValueError(f"Unknown output formats: {sorted(unknown)}")
        page_list = parse_pages(pages)

        if isinstance(pdf, (bytes, bytearray, memoryview)):
            data = bytes(pdf)
            if not data.startswith(b"%PDF"):
                raise ValueError(f"{name or 'pdf'}: content does not look like a PDF")
            # Marker reads from a file path, so the bytes go to a temporary file.
            tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            try:
                tmp.write(data)
                tmp.close()
                return self._convert_path(Path(tmp.name), name or "pdf", page_list, formats)
            finally:
                Path(tmp.name).unlink(missing_ok=True)

        path = Path(pdf).expanduser()
        if not path.is_file():
            raise FileNotFoundError(path)
        return self._convert_path(path, name or path.name, page_list, formats)

    def _convert_path(self, path: Path, name: str, page_list: list[int] | None,
                      formats: tuple[str, ...]) -> ConversionResult:
        if page_list:
            n_total = _page_count(path)
            if n_total is not None and page_list[-1] >= n_total:
                raise ValueError(f"{name} has {n_total} pages; requested page {page_list[-1]} (0-based)")

        collector = _WarningCollector()
        root = logging.getLogger()
        root.addHandler(collector)
        started = _now_iso()
        t0 = time.perf_counter()
        try:
            converter = self._converter_for(page_list)
            document = converter.build_document(str(path))
            n_pages = len(document.pages)

            outputs: dict[str, str] = {}
            images: dict = {}
            for fmt in formats:
                rendered = converter.resolve_dependencies(self._renderers[fmt])(document)
                text, _, imgs = self._text_from_rendered(rendered)
                outputs[fmt] = text
                if fmt == "markdown" and imgs:
                    images = imgs
        finally:
            root.removeHandler(collector)

        seconds = time.perf_counter() - t0
        result = ConversionResult(
            name=name,
            config_name=self.config_name,
            markdown=outputs.get("markdown"),
            json_text=outputs.get("json"),
            pages=n_pages,
            page_range=format_pages(page_list),
            seconds=round(seconds, 2),
            sec_per_page=round(seconds / max(n_pages, 1), 2),
            started_at=started,
            finished_at=_now_iso(),
            warnings=collector.messages,
            images=images,
        )
        log.info("%s: %d pages [%s] in %.1f s (%.2f s/page), %d warning(s)",
                 name, result.pages, result.page_range, result.seconds, result.sec_per_page,
                 len(result.warnings))
        return result