"""
PDF -> Markdown conversion with Marker, built to run unattended on a server.

- No print(): everything goes through `logging`. The calling script decides
  where logs go (console, file, nowhere) with logging.basicConfig(...).
- Configuration comes from outside: pass kwargs, a dict, or a YAML/JSON file
  via PdfToMarkdownConverter.from_config(...).
- Outputs both formats from ONE conversion (Marker builds the document once,
  then renders it twice): Markdown -> papers_md/, Marker JSON -> papers_json/.
- Every file returns a structured FileResult (status, pages, timing, error),
  so test scripts can compare setups and write JSON reports.
- Specific files and mixed page selections are supported, e.g.
      conv.convert({"a.pdf": "0-4,9", "b.pdf": None, "c.pdf": "all"})

Page numbers are 0-based by default (same as Marker). Set
pages_one_indexed=True to write them the way a PDF viewer shows them.

Stuck llama.cpp server?  Linux: pkill -f llama-server
                         Windows: taskkill /IM llama-server.exe /F
"""
from __future__ import annotations

import inspect
import json
import logging
import os
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Union

log = logging.getLogger(__name__)

repo_root = Path(__file__).resolve().parents[1]

PageSpec = Union[None, int, str, Sequence[Union[int, str]]]

# Sentinel: "use the converter's default page_range" (different from "all pages").
_DEFAULT = object()

# Marker options accepted in add_config. A typo like "force_orc" would otherwise
# be silently ignored by Marker. Check against `marker_single config --help`.
KNOWN_MARKER_KEYS = {
    "mode", "force_ocr", "strip_existing_ocr", "disable_ocr", "ocr_inline_math",
    "use_llm", "redo_inline_math", "llm_service",
    "openai_base_url", "openai_model", "openai_api_key", "ollama_base_url", "ollama_model",
    "extract_images", "paginate_output", "keep_pageheader_in_output", "keep_pagefooter_in_output",
}


# --------------------------------------------------------------------------- #
# Page parsing
# --------------------------------------------------------------------------- #
def parse_pages(spec: PageSpec, one_indexed: bool = False) -> list[int] | None:
    """
    Turn a page selection into a sorted list of unique 0-based page numbers.

    Accepted forms (can be mixed):
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

    shift = 1 if one_indexed else 0
    result = sorted(p - shift for p in pages)
    if result and result[0] < 0:
        lowest = "1" if one_indexed else "0"
        raise ValueError(f"Page numbers must start at {lowest}: {spec!r}")
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
# Results
# --------------------------------------------------------------------------- #
@dataclass
class FileResult:
    file: str
    outputs: dict               # {"markdown": path, "json": path}
    status: str                 # "converted" | "skipped" | "failed"
    pages: int = 0
    page_range: str = "all"
    seconds: float = 0.0
    sec_per_page: float = 0.0
    started_at: str = ""
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


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


# --------------------------------------------------------------------------- #
# Converter
# --------------------------------------------------------------------------- #
class PdfToMarkdownConverter:
    def __init__(
        self,
        input_dir: Path | str = repo_root / "papers",
        output_dir: Path | str = repo_root / "papers_md",
        json_output_dir: Path | str = repo_root / "papers_json",
        output_formats: Sequence[str] = ("markdown", "json"),
        mode: str = "balanced",
        disable_image_extraction: bool = True,
        page_range: PageSpec = None,
        pages_one_indexed: bool = False,
        add_config: dict | None = None,
        # file settings
        pattern: str = "*.pdf",
        search_subfolders: bool = False,
        overwrite_mds: bool = False,
        fail_fast: bool = False,
        # marker / inference settings (see SETUP_MARKER.md)
        backend: str = "llamacpp",
        inference_url: str | None = None,   # existing server, e.g. http://localhost:8000/v1
        vllm_gpus: str | None = None,       # e.g. "0"
        llama_cpp_binary: str | None = None,
        parallel: int | None = 4,
        keep_alive: bool = False,
        hf_home: str | None = None,
        artifacts: dict | None = None,      # reuse loaded Marker models from another converter
    ):
        self.input_dir = Path(input_dir).expanduser().resolve()
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.json_output_dir = Path(json_output_dir).expanduser().resolve()
        self.output_formats = tuple(dict.fromkeys(output_formats))
        bad = set(self.output_formats) - {"markdown", "json"}
        if bad or not self.output_formats:
            raise ValueError(f"output_formats must be 'markdown' and/or 'json', got {list(output_formats)}")
        self.pattern = pattern
        self.search_subfolders = search_subfolders
        self.overwrite_mds = overwrite_mds
        self.fail_fast = fail_fast
        self.save_images = not disable_image_extraction
        self.pages_one_indexed = pages_one_indexed

        # Environment must be set BEFORE marker/surya are imported.
        self._set_env(backend, inference_url, vllm_gpus, llama_cpp_binary, parallel, keep_alive, hf_home)

        # NOTE: "disable_image_extraction" is only understood by Marker's CLI.
        # The renderers read "extract_images", so set that directly.
        self.base_config: dict = {
            "mode": mode,
            "extract_images": not disable_image_extraction,
        }
        add_config = dict(add_config or {})
        if "page_range" in add_config:
            # page_range is handled per file; treat it as the default.
            if page_range is None:
                page_range = add_config["page_range"]
            add_config.pop("page_range")
        unknown = set(add_config) - KNOWN_MARKER_KEYS
        if unknown:
            raise ValueError(f"Unknown Marker options in add_config: {sorted(unknown)}")
        if add_config.get("redo_inline_math") and not add_config.get("use_llm"):
            raise ValueError("redo_inline_math needs use_llm=True")
        if add_config.get("use_llm") and not add_config.get("llm_service"):
            raise ValueError("use_llm=True needs llm_service, otherwise Marker silently uses Gemini")
        self.base_config.update(add_config)
        self.default_pages = parse_pages(page_range, pages_one_indexed)

        # Settings snapshot for reports (what exactly was this run?).
        self.settings = {
            "input_dir": str(self.input_dir),
            "output_dir": str(self.output_dir),
            "json_output_dir": str(self.json_output_dir),
            "output_formats": list(self.output_formats),
            "backend": backend,
            "parallel": parallel,
            "keep_alive": keep_alive,
            "page_range": format_pages(self.default_pages),
            "marker_config": {k: ("***" if "api_key" in k else v) for k, v in self.base_config.items()},
            "versions": _versions(),
        }

        # Slow part: loading Marker's models. Done once, reused for every file.
        t0 = time.perf_counter()
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import convert_if_not_rgb, text_from_rendered
        from marker.renderers.json import JSONRenderer
        from marker.renderers.markdown import MarkdownRenderer

        self._PdfConverter = PdfConverter
        self._text_from_rendered = text_from_rendered
        self._to_rgb = convert_if_not_rgb
        self._renderers = {"markdown": MarkdownRenderer, "json": JSONRenderer}
        self._artifacts = artifacts if artifacts is not None else create_model_dict()
        self._converters: dict[tuple[int, ...] | None, Any] = {}
        self.model_load_seconds = round(time.perf_counter() - t0, 2)
        log.info("Marker models loaded in %.1f s", self.model_load_seconds)

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
    # File selection
    # ------------------------------------------------------------------ #
    def find_pdfs(self) -> list[Path]:
        if not self.input_dir.is_dir():
            log.warning("Input directory does not exist: %s", self.input_dir)
            return []
        finder = self.input_dir.rglob if self.search_subfolders else self.input_dir.glob
        return sorted(p for p in finder(self.pattern) if p.is_file())

    def _resolve_path(self, p: str | Path) -> Path:
        """Absolute paths as given; relative ones looked up in input_dir first."""
        path = Path(p).expanduser()
        if path.is_absolute():
            return path
        candidate = self.input_dir / path
        return candidate if candidate.exists() else path.resolve()

    def resolve_files(self, files=None) -> list[tuple[Path, Any]]:
        """
        Normalize every supported `files` form into [(path, page_spec), ...].

            None                           -> all PDFs in input_dir
            "a.pdf" / Path                 -> one file
            ["a.pdf", "b.pdf"]             -> several files
            {"a.pdf": "0-3,7", "b.pdf": None}
            [("a.pdf", "0-3"), {"file": "b.pdf", "pages": [1, "4-6"]}]

        A page spec of None means "use the default page_range";
        "all" means every page regardless of the default.
        """
        if files is None:
            return [(p, _DEFAULT) for p in self.find_pdfs()]
        if isinstance(files, (str, Path)):
            return [(self._resolve_path(files), _DEFAULT)]
        if isinstance(files, Mapping):
            return [
                (self._resolve_path(f), _DEFAULT if spec is None else spec)
                for f, spec in files.items()
            ]

        resolved = []
        for item in files:
            if isinstance(item, (str, Path)):
                resolved.append((self._resolve_path(item), _DEFAULT))
            elif isinstance(item, Mapping):
                spec = item.get("pages")
                resolved.append((self._resolve_path(item["file"]), _DEFAULT if spec is None else spec))
            elif isinstance(item, Sequence) and len(item) == 2:
                f, spec = item
                resolved.append((self._resolve_path(f), _DEFAULT if spec is None else spec))
            else:
                raise ValueError(f"Cannot interpret file entry: {item!r}")
        return resolved

    def _relative(self, pdf: Path | str) -> Path:
        pdf = Path(pdf).resolve()
        try:
            return pdf.relative_to(self.input_dir)
        except ValueError:
            return Path(pdf.name)  # file from outside input_dir

    def _name(self, pdf: Path | str, pages: list[int] | None) -> Path:
        """papers/x/a.pdf, pages [3,4,5] -> x/a.p3-5 (no suffix; all pages -> x/a)"""
        rel = self._relative(pdf)
        return rel.parent / (rel.stem + page_tag(pages))

    def output_path(self, pdf: Path | str, pages: list[int] | None = None) -> Path:
        """papers/x/a.pdf -> papers_md/x/a.md  (with pages: a.p3-5.md)"""
        n = self._name(pdf, pages)
        return self.output_dir / n.parent / f"{n.name}.md"

    def json_output_path(self, pdf: Path | str, pages: list[int] | None = None) -> Path:
        """papers/x/a.pdf -> papers_json/x/a.json  (with pages: a.p3-5.json)"""
        n = self._name(pdf, pages)
        return self.json_output_dir / n.parent / f"{n.name}.json"

    def output_paths(self, pdf: Path | str, pages: list[int] | None = None) -> dict[str, Path]:
        """Output path per requested format."""
        paths = {"markdown": self.output_path(pdf, pages), "json": self.json_output_path(pdf, pages)}
        return {fmt: paths[fmt] for fmt in self.output_formats}

    @staticmethod
    def _atomic_write(path: Path, text: str) -> None:
        """Write via a .tmp file so a watcher never sees a half-written file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        try:
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(path)
        finally:
            tmp.unlink(missing_ok=True)

    # ------------------------------------------------------------------ #
    # Conversion
    # ------------------------------------------------------------------ #
    def convert_file(self, pdf: Path | str, pages: Any = _DEFAULT,
                     formats: Sequence[str] | None = None) -> FileResult:
        """
        Convert one PDF. Marker builds the document once; each requested format
        is rendered from that same document (no second conversion).
        Raises on failure (convert() catches and records it).
        """
        pdf = Path(pdf)
        formats = tuple(formats or self.output_formats)
        unknown = set(formats) - set(self._renderers)
        if unknown:
            raise ValueError(f"Unknown output formats: {sorted(unknown)}")
        page_list = self.default_pages if pages is _DEFAULT else parse_pages(pages, self.pages_one_indexed)
        if page_list:
            n_total = _page_count(pdf)
            if n_total is not None and page_list[-1] >= n_total:
                raise ValueError(f"{pdf.name} has {n_total} pages; requested page {page_list[-1]} (0-based)")
        all_paths = {"markdown": self.output_path(pdf, page_list), "json": self.json_output_path(pdf, page_list)}
        paths = {fmt: all_paths[fmt] for fmt in formats}

        started = _now_iso()
        t0 = time.perf_counter()

        converter = self._converter_for(page_list)
        document = converter.build_document(str(pdf))
        n_pages = len(document.pages)

        for fmt in formats:
            rendered = converter.resolve_dependencies(self._renderers[fmt])(document)
            text, _, images = self._text_from_rendered(rendered)
            self._atomic_write(paths[fmt], text)

            # Markdown references images by file name, so save them next to the .md
            if fmt == "markdown" and self.save_images and images:
                for name, img in images.items():
                    self._to_rgb(img).save(paths[fmt].parent / name)

        seconds = time.perf_counter() - t0
        return FileResult(
            file=str(pdf),
            outputs={fmt: str(p) for fmt, p in paths.items()},
            status="converted",
            pages=n_pages,
            page_range=format_pages(page_list),
            seconds=round(seconds, 2),
            sec_per_page=round(seconds / max(n_pages, 1), 2),
            started_at=started,
        )

    def convert(self, files=None) -> list[FileResult]:
        """
        Convert the given files (see resolve_files for accepted forms),
        or every PDF in input_dir when files is None.
        Failures are logged and recorded; set fail_fast=True to stop instead.
        """
        jobs = self.resolve_files(files)
        if not jobs:
            log.warning("No files matching %r in %s", self.pattern, self.input_dir)
            return []

        results: list[FileResult] = []
        total = len(jobs)
        for i, (pdf, pages) in enumerate(jobs, 1):
            tag = f"[{i}/{total}] {pdf.name}"
            try:
                page_list = self.default_pages if pages is _DEFAULT else parse_pages(pages, self.pages_one_indexed)
            except ValueError as e:
                log.error("%s: %s", tag, e)
                results.append(FileResult(str(pdf), {}, "failed", started_at=_now_iso(), error=str(e)))
                continue
            paths = self.output_paths(pdf, page_list)
            outs = {fmt: str(p) for fmt, p in paths.items()}

            if not pdf.is_file():
                log.error("%s: file not found (%s)", tag, pdf)
                results.append(FileResult(str(pdf), outs, "failed",
                                          started_at=_now_iso(), error="FileNotFoundError"))
                if self.fail_fast:
                    break
                continue

            # Only produce the formats that are missing (all of them if overwriting).
            todo = [fmt for fmt, p in paths.items() if self.overwrite_mds or not p.exists()]
            if not todo:
                log.info("%s: skipped (outputs exist)", tag)
                results.append(FileResult(str(pdf), outs, "skipped", started_at=_now_iso()))
                continue

            try:
                res = self.convert_file(pdf, pages, formats=todo)
                results.append(res)
                log.info("%s: %d pages [%s] -> %s in %.1f s (%.2f s/page)",
                         tag, res.pages, res.page_range, "+".join(todo), res.seconds, res.sec_per_page)
            except Exception as e:  # noqa: BLE001 - one bad PDF must not stop a batch
                log.exception("%s: failed", tag)
                results.append(FileResult(str(pdf), outs, "failed",
                                          started_at=_now_iso(), error=f"{type(e).__name__}: {e}"))
                if self.fail_fast:
                    break

        s = self.summarize(results)
        log.info("Done: %d converted, %d skipped, %d failed, %d pages, %.1f min",
                 s["converted"], s["skipped"], s["failed"], s["total_pages"], s["total_seconds"] / 60)
        return results

    # Backwards-compatible name
    def convert_all(self) -> list[FileResult]:
        return self.convert(None)

    # ------------------------------------------------------------------ #
    # Reporting
    # ------------------------------------------------------------------ #
    def summarize(self, results: list[FileResult]) -> dict:
        done = [r for r in results if r.status == "converted"]
        total_pages = sum(r.pages for r in done)
        total_seconds = round(sum(r.seconds for r in done), 2)
        return {
            "converted": len(done),
            "skipped": sum(r.status == "skipped" for r in results),
            "failed": sum(r.status == "failed" for r in results),
            "total_pages": total_pages,
            "total_seconds": total_seconds,
            "avg_sec_per_page": round(total_seconds / total_pages, 2) if total_pages else None,
            "model_load_seconds": self.model_load_seconds,
        }

    def write_report(self, results: list[FileResult], path: Path | str) -> Path:
        """Write settings + summary + per-file results as JSON."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "finished_at": _now_iso(),
            "settings": self.settings,
            "summary": self.summarize(results),
            "files": [r.to_dict() for r in results],
        }
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)
        return path
