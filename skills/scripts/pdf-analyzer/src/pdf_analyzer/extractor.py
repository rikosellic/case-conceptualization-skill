from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

from pypdf import PdfReader


WHITESPACE_RE = re.compile(r"[ \t]+")
BLANK_LINES_RE = re.compile(r"\n{3,}")
LINEBREAK_HYPHEN_RE = re.compile(r"(?<=\w)-\n(?=\w)")


@dataclass(frozen=True)
class ExtractOptions:
    preserve_line_breaks: bool = False
    page_start: int | None = None
    page_end: int | None = None
    min_chars_per_page: int = 20


@dataclass(frozen=True)
class PageText:
    page_number: int
    text: str
    warning: str | None = None


def extract_pdf_pages(pdf_path: Path, options: ExtractOptions) -> list[PageText]:
    reader = PdfReader(pdf_path)
    page_count = len(reader.pages)
    start_index = _normalize_start(options.page_start, page_count)
    end_index = _normalize_end(options.page_end, page_count)

    if start_index > end_index:
        raise ValueError("起始页不能大于结束页。")

    pages: list[PageText] = []
    for page_index in range(start_index, end_index + 1):
        page = reader.pages[page_index]
        raw_text = page.extract_text() or ""
        text = normalize_text(raw_text, preserve_line_breaks=options.preserve_line_breaks)
        warning = None
        if len(text.strip()) < options.min_chars_per_page:
            warning = "本页提取到的文字很少，可能是扫描页、图片页或排版特殊。"
        pages.append(PageText(page_number=page_index + 1, text=text, warning=warning))
    return pages


def write_markdown(pages: Iterable[PageText], output_path: Path, source_path: Path) -> None:
    parts = [
        f"# {source_path.stem}",
        "",
        f"Source PDF: `{source_path.name}`",
        "",
    ]

    for page in pages:
        parts.append(f"## Page {page.page_number}")
        if page.warning:
            parts.append(f"> Warning: {page.warning}")
            parts.append("")
        parts.append(page.text or "[No extractable text]")
        parts.append("")

    output_path.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")


def write_plain_text(pages: Iterable[PageText], output_path: Path) -> None:
    parts: list[str] = []
    for page in pages:
        parts.append(f"[[PAGE {page.page_number}]]")
        if page.warning:
            parts.append(f"[Warning: {page.warning}]")
        parts.append(page.text or "[No extractable text]")
        parts.append("")

    output_path.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")


def normalize_text(text: str, preserve_line_breaks: bool = False) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = LINEBREAK_HYPHEN_RE.sub("", text)
    lines = [WHITESPACE_RE.sub(" ", line).strip() for line in text.split("\n")]

    if preserve_line_breaks:
        normalized = "\n".join(lines)
    else:
        normalized = _join_wrapped_lines(lines)

    normalized = BLANK_LINES_RE.sub("\n\n", normalized)
    return normalized.strip()


def _join_wrapped_lines(lines: list[str]) -> str:
    paragraphs: list[str] = []
    current: list[str] = []

    for line in lines:
        if not line:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(line)

    if current:
        paragraphs.append(" ".join(current))

    return "\n\n".join(paragraphs)


def _normalize_start(page_start: int | None, page_count: int) -> int:
    if page_start is None:
        return 0
    if page_start < 1:
        raise ValueError("起始页必须大于等于 1。")
    if page_start > page_count:
        raise ValueError(f"起始页超过 PDF 总页数：{page_count}。")
    return page_start - 1


def _normalize_end(page_end: int | None, page_count: int) -> int:
    if page_end is None:
        return page_count - 1
    if page_end < 1:
        raise ValueError("结束页必须大于等于 1。")
    if page_end > page_count:
        raise ValueError(f"结束页超过 PDF 总页数：{page_count}。")
    return page_end - 1
