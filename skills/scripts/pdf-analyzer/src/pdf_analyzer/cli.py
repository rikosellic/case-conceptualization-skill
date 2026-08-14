from __future__ import annotations

import argparse
from pathlib import Path
import sys

from pypdf.errors import PdfReadError

from pdf_analyzer.extractor import (
    ExtractOptions,
    extract_pdf_pages,
    write_markdown,
    write_plain_text,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdf-extract",
        description="Extract selectable PDF text into AI-friendly Markdown or plain text.",
    )
    parser.add_argument("pdf", type=Path, help="输入 PDF 文件路径。")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="输出文件路径。默认写到 PDF 同目录，扩展名由格式决定。",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "text"),
        default="markdown",
        help="输出格式，默认 markdown。",
    )
    parser.add_argument("--start", type=int, help="起始页，页码从 1 开始。")
    parser.add_argument("--end", type=int, help="结束页，包含该页。")
    parser.add_argument(
        "--preserve-line-breaks",
        action="store_true",
        help="保留 PDF 原始换行；默认会把同一段落内的换行合并，方便 AI 阅读。",
    )
    parser.add_argument(
        "--min-chars-per-page",
        type=int,
        default=20,
        help="少于该字符数的页面会被标记为疑似不可提取页，默认 20。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    pdf_path = args.pdf.expanduser().resolve()
    if not pdf_path.exists():
        parser.error(f"找不到 PDF 文件：{pdf_path}")
    if not pdf_path.is_file():
        parser.error(f"不是文件：{pdf_path}")

    output_path = _resolve_output_path(pdf_path, args.output, args.format)
    options = ExtractOptions(
        preserve_line_breaks=args.preserve_line_breaks,
        page_start=args.start,
        page_end=args.end,
        min_chars_per_page=args.min_chars_per_page,
    )

    try:
        pages = extract_pdf_pages(pdf_path, options)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if args.format == "markdown":
            write_markdown(pages, output_path, pdf_path)
        else:
            write_plain_text(pages, output_path)
    except (PdfReadError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    warning_count = sum(1 for page in pages if page.warning)
    print(f"Extracted {len(pages)} pages to {output_path}")
    if warning_count:
        print(f"Warning pages: {warning_count}")
    return 0


def _resolve_output_path(pdf_path: Path, output: Path | None, output_format: str) -> Path:
    if output is not None:
        return output.expanduser().resolve()
    suffix = ".md" if output_format == "markdown" else ".txt"
    return pdf_path.with_suffix(suffix)


if __name__ == "__main__":
    raise SystemExit(main())
