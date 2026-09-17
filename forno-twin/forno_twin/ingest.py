"""Eingangsdateien lesen: Text, Markdown, PDF (Backlog B7).

PDF-Text wird zuerst mit der Standardbibliothek gelesen (zlib für FlateDecode,
Tj/TJ-Operatoren). Ist `pypdf` installiert, wird es bevorzugt, weil es mehr
PDF-Varianten abdeckt. Kein Pflicht-Paket: fehlt pypdf, läuft der Fallback.

Der extrahierte Text ist immer nur Eingabe für die Regelextraktion. Er setzt
keine Fakten und wird wie jede andere Anfrage pseudonymisiert.
"""
from __future__ import annotations

import re
import zlib
from pathlib import Path

TEXT_SUFFIXES = {".txt", ".md", ".eml", ".text"}


def _pdf_strings(chunk: bytes) -> list[str]:
    """Textstücke aus den Operatoren Tj und TJ eines entpackten Content-Streams."""
    out = []
    for m in re.finditer(rb"\((?:\\.|[^\\()])*\)", chunk, re.S):
        raw = m.group(0)[1:-1]
        raw = raw.replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\")
        raw = raw.replace(b"\\n", b"\n").replace(b"\\r", b"\n").replace(b"\\t", b" ")
        try:
            out.append(raw.decode("utf-8"))
        except UnicodeDecodeError:
            out.append(raw.decode("latin-1", errors="replace"))
    return out


def pdf_text_stdlib(data: bytes) -> str:
    """PDF-Text ohne Fremdpakete. Deckt unkomprimierte und Flate-Streams ab."""
    parts: list[str] = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
        chunk = m.group(1)
        try:
            chunk = zlib.decompress(chunk)
        except zlib.error:
            pass
        if b"Tj" in chunk or b"TJ" in chunk:
            parts.extend(_pdf_strings(chunk))
    text = " ".join(p for p in parts if p.strip())
    return re.sub(r"[ \t]{2,}", " ", text).strip()


def pdf_text(path: Path) -> tuple[str, str]:
    """Gibt (Text, verwendete Methode) zurück."""
    data = Path(path).read_bytes()
    try:
        from pypdf import PdfReader  # type: ignore
        reader = PdfReader(str(path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
        if text:
            return text, "pypdf"
    except Exception:  # noqa: BLE001 - pypdf optional oder Datei unlesbar
        pass
    return pdf_text_stdlib(data), "stdlib"


def read_input(path: str | Path) -> dict:
    """Liest eine Anfrage aus einer Datei. Ergebnis: {text, source_type, method, chars}."""
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        text, method = pdf_text(p)
        return {"text": text, "source_type": "pdf", "method": method, "chars": len(text),
                "note": "PDF-Text extrahiert; Layout und Tabellen können verloren gehen"}
    if suffix in TEXT_SUFFIXES or suffix == "":
        text = p.read_text(encoding="utf-8", errors="replace")
        return {"text": text, "source_type": "text", "method": "read_text", "chars": len(text), "note": ""}
    raise ValueError(f"Nicht unterstützter Dateityp: {suffix or '(ohne Endung)'}")
