"""
PDF -> chunki (jednostki matematyczne) -> JSON      [wersja 7, klasa PdfChunker]

Użycie w innym pliku:
    from pdf_chunker import PdfChunker
    ch = PdfChunker(force_ocr=True)
    chunks = ch.chunk_pdf("ksiazka.pdf", book="Tytuł", book_id=1)   # Marker + chunkowanie
    ch.save(chunks, "ksiazka.json")
    # albo bez Markera, z gotowych bloków:  chunks = ch.chunk_blocks(raw, "Tytuł", 1)


Zmiany względem v6:
  1. convert() zapisuje surowe bloki Markera obok PDF-a (<plik>.pdf.ocr.raw.json)
     i przy kolejnym uruchomieniu czyta je z dysku - Marker liczy się tylko raz.
  2. Model Markera ładowany raz na proces (ważne przy wielu książkach w pętli).
  3. Koniec dowodu (∎ □ \\square QED) zamyka jednostkę - tekst po nim wraca do prozy.
  4. Przypisy (block_type "Footnote") trafiają na koniec chunka w [Przypisy],
     zamiast rozcinać zdanie.
  5. Tabele jako Markdown (| a | b |).
  6. Pola prev_id / next_id (sąsiednie chunki w książce).
  7. report_text(chunks) - raport kontrolny; process() drukuje go domyślnie.

Wymaga: pip install marker-pdf
"""
import argparse
import html
import json
import os
import re
import sys
import time
from collections import Counter

SKIP = {"PageHeader", "PageFooter"}
MAX_CHARS = 6000   # miękki limit dla twierdzeń/definicji (z dowodem)
MAX_PROSE = 2500   # limit dla zwykłego tekstu

# --- słowa rozpoznające typ jednostki (dopasuj do swoich książek) ---
KIND_WORDS = {
    "definition": r"Definition|Definicja",
    "theorem": r"Theorem|Twierdzenie|Lemma|Lemat|Proposition|Propozycja|Corollary|Wniosek|Stwierdzenie",
    "conjecture": r"Conjecture|Hipoteza",
    "proof": r"Proof|Dowód",
    "example": r"Example|Przykład",
    "remark": r"Remark|Uwaga",
}
WORD2KIND = {w.lower(): k for k, ws in KIND_WORDS.items() for w in ws.split("|")}
ALL_WORDS = "|".join(w for ws in KIND_WORDS.values() for w in ws.split("|"))
NON_PROOF_WORDS = "|".join(w for k, ws in KIND_WORDS.items() if k != "proof" for w in ws.split("|"))
# etykieta: numer (2.4) albo POJEDYNCZA WIELKA litera (A) - litera tylko wielka, nawet przy re.I
LABEL = r"(\d+(?:\.\d+)*|(?-i:[A-Z])\b)"

# styl Wassermana: "2.4 Theorem." / "2.3 Example (Nerve data)."
NUM_FIRST = re.compile(rf"^\W*(\d+(?:\.\d+)+)\s+({ALL_WORDS})\b\s*(?:\(([^)]*)\))?\s*[.:]?", re.I)
# styl klasyczny: "Theorem 2.4." / "THEOREM A." - po etykiecie MUSI być kropka lub dwukropek
WORD_FIRST = re.compile(rf"^\W*({ALL_WORDS})\s+{LABEL}\s*(?:\(([^)]*)\))?\s*[.:](?:\s|$)", re.I)
# bez numeru: "COROLLARY." / "Conjecture." - słowo, od razu kropka/dwukropek
UNNUMBERED = re.compile(rf"^\W*({NON_PROOF_WORDS})\s*(?:\(([^)]*)\))?\s*[.:](?:\s|$)", re.I)
# "Proof." / "Dowód." / "Proof of Theorem 2.4." / "Proof of theorem B."
PROOF = re.compile(r"^\W*(Proof|Dowód)\b(?=\s*[.:]|\s+of\b|\s+twierdzenia\b|\s+lematu\b)", re.I)
PROOF_OF = re.compile(rf"^\W*(?:Proof|Dowód)\s+(?:of|twierdzenia|lematu)\s+(?:the\s+)?(?:\w+\s+)?{LABEL}", re.I)
# koniec dowodu: ∎ □ ■ \square \Box \blacksquare QED na końcu bloku (ewentualnie przed $ albo kropką)
END_PROOF = re.compile(r"(?:∎|□|■|\\square|\\Box|\\blacksquare|\bQ\.?\s?E\.?\s?D\.?)\s*[.$]*\s*$", re.I)
REF = re.compile(
    rf"\b(?:Definition|Theorem|Lemma|Proposition|Corollary|Definicj\w+|Twierdzeni\w+|Lemat\w*|Wniosek|Wniosk\w+)\s+{LABEL}",
    re.I,
)
REFERENCES_SECTION = re.compile(r"(references|bibliography|bibliografia|literatura)\s*$", re.I)


# ---------- 1. Marker (z cache na dysku) ----------
_MODELS = None
_CONVERTERS = {}
RAW_KEYS = ("id", "block_type", "html", "page", "section_hierarchy")


def _marker_blocks(pdf_path, force_ocr):
    """Uruchamia Marker. Modele i konwerter budowane raz na proces."""
    global _MODELS
    conv = _CONVERTERS.get(force_ocr)
    if conv is None:
        from marker.config.parser import ConfigParser
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict

        if _MODELS is None:
            _MODELS = create_model_dict()
        cfg = ConfigParser({"output_format": "chunks", "force_ocr": force_ocr})
        conv = PdfConverter(
            config=cfg.generate_config_dict(),
            artifact_dict=_MODELS,
            processor_list=cfg.get_processors(),
            renderer=cfg.get_renderer(),
        )
        _CONVERTERS[force_ocr] = conv
    rendered = conv(pdf_path)
    # marker 2.x: ChunkOutput ma pole .blocks; starsze wersje: .chunks
    return getattr(rendered, "blocks", None) or getattr(rendered, "chunks")


def block_to_dict(b):
    """Blok Markera (obiekt pydantic albo dict) -> zwykły dict tylko z potrzebnymi polami."""
    if isinstance(b, dict):
        d = dict(b)
    else:  # NIE model_dump(): w Markerze 2.x wywala się na polach typu polygon/images
        d = {k: getattr(b, k) for k in RAW_KEYS if hasattr(b, k)}
    out = {k: d[k] for k in RAW_KEYS if k in d}
    bt = out.get("block_type")
    if bt is not None and not isinstance(bt, str):
        out["block_type"] = getattr(bt, "name", None) or str(bt)  # Enum -> "SectionHeader"
    elif isinstance(bt, str) and bt.startswith("BlockTypes."):
        out["block_type"] = bt.split(".", 1)[1]
    return out


def convert(pdf_path, force_ocr=False, use_cache=True):
    """Zwraca listę bloków (dict). Surowy wynik Markera jest zapisywany obok PDF-a
    i używany ponownie, dopóki PDF się nie zmieni (porównanie czasu modyfikacji)."""
    cache = f"{pdf_path}.{'ocr' if force_ocr else 'text'}.raw.json"
    if use_cache and os.path.exists(cache) and os.path.getmtime(cache) >= os.path.getmtime(pdf_path):
        with open(cache, encoding="utf-8") as f:
            return json.load(f)
    raw = [block_to_dict(b) for b in _marker_blocks(pdf_path, force_ocr)]
    if use_cache:
        with open(cache, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, default=str)
    return raw


def get(c, key, default=None):  # chunk może być dictem lub obiektem
    return c.get(key, default) if isinstance(c, dict) else getattr(c, key, default)


def page_of(c):
    """Marker 2.x w polu 'page' zwraca numer bloku, nie strony.
    Prawdziwa strona (od 0) jest w id: '/page/10/Text/3'."""
    m = re.search(r"/page/(\d+)/", str(get(c, "id", "")))
    return int(m.group(1)) + 1 if m else get(c, "page", get(c, "page_id"))


# ---------- 2. HTML -> tekst z zachowaniem LaTeX-a i tabel ----------
def math_text(h):
    """Wzory wyciągamy do placeholderów, żeby '<' w LaTeX-u nie wyglądało jak tag."""
    store = []

    def keep(wrap):
        def _r(m):
            store.append(wrap(html.unescape(m.group(1))))
            return f"\x00{len(store) - 1}\x00"
        return _r

    h = re.sub(r"<math[^>]*display=.block.[^>]*>(.*?)</math>", keep(lambda t: f"\n$${t}$$\n"), h, flags=re.S)
    h = re.sub(r"<math[^>]*>(.*?)</math>", keep(lambda t: f"${t}$"), h, flags=re.S)
    h = html.unescape(re.sub(r"<[^>]+>", " ", h))
    h = re.sub(r"\x00(\d+)\x00", lambda m: store[int(m.group(1))], h)
    return h.strip()


def table_to_md(table_html):
    """<table>...</table> -> tabela Markdown. Pierwszy wiersz jest nagłówkiem."""
    rows = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, flags=re.S | re.I):
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, flags=re.S | re.I)
        cells = [re.sub(r"\s+", " ", math_text(c)).replace("|", "\\|") for c in cells]
        if cells:
            rows.append(cells)
    if not rows:
        return math_text(table_html)
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    md = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
    md += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(md)


def html_to_text(h):
    if "<table" not in h.lower():
        return math_text(h)
    tables = []

    def rep(m):
        tables.append(table_to_md(m.group(0)))
        return f"\x01{len(tables) - 1}\x01"

    rest = math_text(re.sub(r"<table.*?</table>", rep, h, flags=re.S | re.I))
    return re.sub(r"\x01(\d+)\x01", lambda m: "\n\n" + tables[int(m.group(1))] + "\n\n", rest).strip()


# ---------- 3. bloki -> sekcje ----------
def blocks_to_sections(raw):
    """Sekcja: {"path", "page", "blocks": [(block_type, tekst, strona), ...]}"""
    sections, cur, path = [], None, []

    def start(title, level):
        nonlocal cur, path
        if cur and cur["blocks"]:
            sections.append(cur)
        path = path[: level - 1] + [title]
        cur = {"path": list(path), "page": None, "blocks": []}

    start("", 1)
    for c in raw:
        btype = get(c, "block_type")
        if btype in SKIP:
            continue
        raw_html = get(c, "html", "") or ""
        text = html_to_text(raw_html)
        if not text:
            continue
        # Marker czasem uznaje "2.6 Theorem. Let" za nagłówek sekcji - to jednostka, nie sekcja
        if btype == "SectionHeader" and not classify(text)[0]:
            m = re.search(r"<h(\d)", raw_html)
            start(text, int(m.group(1)) if m else 1)
            continue
        page = page_of(c)
        if cur["page"] is None:
            cur["page"] = page
        cur["blocks"].append((btype, text, page))
    if cur and cur["blocks"]:
        sections.append(cur)
    return sections


# ---------- 4. sekcje -> jednostki matematyczne ----------
def classify(text):
    """Zwraca (kind, number, title) albo (None, None, None).
    'Theorem 2.41 is only useful...' (odwołanie w zdaniu) NIE jest nagłówkiem."""
    m = NUM_FIRST.match(text)
    if m:
        return WORD2KIND[m.group(2).lower()], m.group(1), m.group(3)
    if PROOF.match(text):
        return "proof", None, None
    m = WORD_FIRST.match(text)
    if m:
        return WORD2KIND[m.group(1).lower()], m.group(2), m.group(3)
    m = UNNUMBERED.match(text)
    if m:
        return WORD2KIND[m.group(1).lower()], None, m.group(2)
    return None, None, None


def proof_target(text):
    """'Proof of theorem B.' -> 'B';  'Proof of lemma 2.3.' -> '2.3';  'Proof.' -> None"""
    m = PROOF_OF.match(text)
    return m.group(1) if m else None


def _new_unit(kind, number, title, block):
    return {"kind": kind, "number": number, "title": title, "blocks": [block],
            "has_proof": False, "proves": None, "in_proof": kind == "proof"}


def units_from_section(blocks):
    units, cur = [], None

    def prose():
        return {"kind": "prose", "number": None, "title": None, "blocks": [],
                "has_proof": False, "proves": None, "in_proof": False}

    for btype, text, page in blocks:
        block = (btype, text, page)
        if btype == "Footnote":            # przypis: nie jest nagłówkiem, zostaje w bieżącej jednostce
            if cur is None:
                cur = prose()
            cur["blocks"].append(block)
            continue
        kind, num, title = classify(text) if btype != "Equation" else (None, None, None)
        if kind == "proof":
            target = proof_target(text)
            if cur and cur["kind"] == "theorem" and (target is None or target == cur["number"]):
                cur["has_proof"] = True  # dowód dołącza do twierdzenia, które właśnie czytamy
                cur["in_proof"] = True
                cur["blocks"].append(block)
            elif target is not None:
                # dowód INNEGO twierdzenia (np. 'Proof of theorem B' w innej sekcji) - osobna jednostka
                if cur:
                    units.append(cur)
                cur = _new_unit("proof", None, None, block)
                cur["proves"] = target
            else:
                if cur:
                    units.append(cur)
                cur = _new_unit("proof", None, None, block)
        elif kind:
            if cur:
                units.append(cur)
            cur = _new_unit(kind, num, title, block)
        else:
            if cur is None:
                cur = prose()
            cur["blocks"].append(block)
        # koniec dowodu zamyka jednostkę - dalszy tekst zaczyna nową prozę
        if cur and cur["in_proof"] and END_PROOF.search(text.rstrip()):
            units.append(cur)
            cur = None
    if cur:
        units.append(cur)
    return units


def split_long(unit, max_chars_unit=None, max_prose=None):
    """Tnij tylko między blokami; nie tnij tuż po wzorze ani po zdaniu kończącym się
    na ':' lub ',' (bo dalej jest dokończenie). Dla twierdzeń powtarzaj ich początek.
    Przypisy dołączane są na koniec części, w której wystąpiły.
    Zwraca listę (tekst, strona_pierwszego_bloku)."""
    prose = unit["kind"] == "prose"
    max_chars = (max_prose or MAX_PROSE) if prose else (max_chars_unit or MAX_CHARS)
    head = unit["blocks"][0][1]
    parts, buf, size, first_page, foot = [], [], 0, None, []
    prev_type, prev_text = None, ""

    def flush():
        text = "\n\n".join(buf)
        if foot:
            text += ("\n\n" if text else "") + "[Przypisy]\n" + "\n".join(foot)
        parts.append((text, first_page))

    for btype, text, page in unit["blocks"]:
        if btype == "Footnote":
            foot.append(text)
            if first_page is None:
                first_page = page
            continue
        can_split = (
            buf
            and btype != "Equation"
            and prev_type != "Equation"
            and not prev_text.rstrip().endswith((":", ","))
        )
        if size + len(text) > max_chars and can_split:
            flush()
            buf, size, first_page = ([] if prose else [head[:300] + " (…)"]), 0, None
            foot.clear()
        if first_page is None:
            first_page = page
        buf.append(text)
        size += len(text)
        prev_type, prev_text = btype, text
    flush()
    return parts


def build_chunks(sections, book, book_id=0, max_chars=None, max_prose=None):
    chunks, index = [], {}
    for s in sections:
        sec = " > ".join(x for x in s["path"] if x)
        is_refs = bool(REFERENCES_SECTION.search(sec))
        for u in units_from_section(s["blocks"]):
            kind = "references" if (is_refs and u["kind"] == "prose") else u["kind"]
            for part, page in split_long(u, max_chars, max_prose):
                idx = len(chunks)
                cid = f"{book_id}-{idx}"
                chunks.append({
                    "id": cid,
                    "book_id": book_id,
                    "chunk_index": idx,
                    "book": book,
                    "section": sec,
                    "page": page if page is not None else s["page"],
                    "kind": kind,
                    "number": u["number"],
                    "title": u["title"],
                    "has_proof": u["has_proof"],
                    "proves": u["proves"],
                    "text": part,
                    "refs_raw": sorted(set(REF.findall(part))),
                    "embed_text": f"Książka: {book} | {sec} | {(kind + ' ' + (u['number'] or '') + ' ' + (u['title'] or '')).strip()}\n{part}",
                })
                if u["number"] and kind != "proof":
                    index.setdefault(u["number"], cid)
    by_id = {c["id"]: c for c in chunks}
    for c in chunks:  # numery/etykiety -> id chunków
        c["refs"] = [index[n] for n in c.pop("refs_raw") if n in index and index[n] != c["id"]]
        if c["proves"] and c["proves"] in index:  # dowód wskazuje swoje twierdzenie i odwrotnie
            target = index[c["proves"]]
            if target not in c["refs"]:
                c["refs"].insert(0, target)
            by_id[target]["has_proof"] = True
    for i, c in enumerate(chunks):  # sąsiedzi w obrębie książki
        c["prev_id"] = chunks[i - 1]["id"] if i > 0 else None
        c["next_id"] = chunks[i + 1]["id"] if i + 1 < len(chunks) else None
    return chunks


# ---------- 5. raport kontrolny ----------
def report_text(chunks, max_chars=None):
    """Krótki raport jakości - co sprawdzić po przetworzeniu książki."""
    max_chars = max_chars or MAX_CHARS
    n = len(chunks)
    if not n:
        return "RAPORT: brak chunków - Marker nic nie zwrócił?"
    kinds = Counter(c["kind"] for c in chunks)
    lens = sorted(len(c["text"]) for c in chunks)
    median = lens[n // 2]
    long_ = sum(1 for L in lens if L > max_chars * 1.3)
    tiny = sum(1 for L in lens if L < 150)
    pages = [c["page"] for c in chunks if isinstance(c.get("page"), int)]
    lines = [
        f"RAPORT: {n} chunków, strony {min(pages) if pages else '?'}-{max(pages) if pages else '?'}",
        f"  typy: {dict(kinds)}",
        f"  długość znaków: min {lens[0]} / mediana {median} / max {lens[-1]}; "
        f"zbyt długich (>{int(max_chars * 1.3)}): {long_}; bardzo krótkich (<150): {tiny}",
    ]
    thm = [c for c in chunks if c["kind"] == "theorem"]
    if thm:
        lines.append(f"  twierdzenia: {len(thm)}, z dowodem: {sum(1 for c in thm if c['has_proof'])}")
    structured = sum(v for k, v in kinds.items() if k not in ("prose", "references"))
    if structured == 0:
        lines.append("  UWAGA: żadnych twierdzeń/definicji/przykładów - styl nagłówków tej książki "
                     "nie został rozpoznany albo to nie jest tekst matematyczny")
    # dziury w numeracji: grupujemy po przedrostku (2.1, 2.2, 2.4 -> w rozdz. 2 brakuje 3)
    groups = {}
    for c in chunks:
        num = c["number"]
        m = re.fullmatch(r"(\d+(?:\.\d+)*)\.(\d+)", num or "")
        if m and c["kind"] != "proof":
            groups.setdefault(m.group(1), set()).add(int(m.group(2)))
    gaps = []
    for prefix, nums in sorted(groups.items()):
        if len(nums) >= 3:
            missing = sorted(set(range(min(nums), max(nums) + 1)) - nums)
            if missing:
                gaps.append(f"{prefix}.{{{','.join(map(str, missing[:8]))}{'…' if len(missing) > 8 else ''}}}")
    if gaps:
        lines.append("  podejrzane braki w numeracji (część książek liczy osobno lematy i twierdzenia): "
                     + "; ".join(gaps[:10]))
    return "\n".join(lines)


# ---------- 6. całość ----------
def process(raw, book, book_id=0, report=True):
    chunks = build_chunks(blocks_to_sections(raw), book, book_id)
    if report:
        print(report_text(chunks))
    return chunks




# ---------- 7. klasa do importowania ----------
class PdfChunker:
    """Wygodny interfejs: ustawienia raz w konstruktorze, potem chunk_pdf / chunk_blocks."""

    def __init__(self, force_ocr=False, use_cache=True, max_chars=MAX_CHARS,
                 max_prose=MAX_PROSE, report=True):
        self.force_ocr = force_ocr
        self.use_cache = use_cache
        self.max_chars = max_chars
        self.max_prose = max_prose
        self.report = report
        self.last_timing = {}

    def convert(self, pdf_path):
        """PDF -> surowe bloki Markera (z cache .raw.json)."""
        return convert(pdf_path, force_ocr=self.force_ocr, use_cache=self.use_cache)

    def chunk_blocks(self, raw, book, book_id=0):
        """Surowe bloki -> lista chunków (bez Markera)."""
        chunks = build_chunks(blocks_to_sections(raw), book, book_id, self.max_chars, self.max_prose)
        if self.report:
            print(report_text(chunks, self.max_chars))
        return chunks

    def chunk_pdf(self, pdf_path, book=None, book_id=0):
        """PDF -> lista chunków. book domyślnie = nazwa pliku bez .pdf."""
        book = book or os.path.splitext(os.path.basename(pdf_path))[0]
        t0 = time.time()
        raw = self.convert(pdf_path)
        t1 = time.time()
        chunks = self.chunk_blocks(raw, book, book_id)
        self.last_timing = {"marker_s": round(t1 - t0, 1), "chunking_s": round(time.time() - t1, 2)}
        return chunks

    @staticmethod
    def save(chunks, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    report_text = staticmethod(report_text)
