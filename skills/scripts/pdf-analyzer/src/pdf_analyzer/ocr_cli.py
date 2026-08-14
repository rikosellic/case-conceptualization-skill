from __future__ import annotations

import argparse
from pathlib import Path
import sys

from pypdf.errors import PdfReadError

from pdf_analyzer.extractor import PageText
from pdf_analyzer.ocr import OcrOptions, iter_ocr_pdf_pages


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdf-ocr",
        description="OCR scanned PDF pages into AI-friendly Markdown or plain text.",
    )
    parser.add_argument("pdf", type=Path, help="输入扫描版 PDF 文件路径。")
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
        "--rapid-score-thresh",
        type=float,
        default=0.0,
        help="RapidOCR 识别置信度阈值，默认 0.0。",
    )
    parser.add_argument("--dpi", type=int, default=200, help="页面渲染 DPI，默认 200。")
    parser.add_argument(
        "--pdftoppm",
        default="pdftoppm",
        help="pdftoppm 命令或完整路径。",
    )
    parser.add_argument(
        "--image-dir",
        type=Path,
        help="保留中间页图片到指定目录；不设置则使用临时目录并自动删除。",
    )
    parser.add_argument(
        "--preserve-line-breaks",
        action="store_true",
        help="保留 OCR 原始换行；默认会把同一段落内的换行合并。",
    )
    parser.add_argument(
        "--min-chars-per-page",
        type=int,
        default=20,
        help="少于该字符数的页面会被标记为疑似低识别页，默认 20。",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="不打印逐页 OCR 进度。",
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
    options = OcrOptions(
        rapid_score_thresh=args.rapid_score_thresh,
        dpi=args.dpi,
        page_start=args.start,
        page_end=args.end,
        preserve_line_breaks=args.preserve_line_breaks,
        pdftoppm_cmd=args.pdftoppm,
        min_chars_per_page=args.min_chars_per_page,
        image_dir=args.image_dir.expanduser().resolve() if args.image_dir else None,
    )

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        page_count, warning_count = _write_ocr_output(
            pdf_path=pdf_path,
            output_path=output_path,
            output_format=args.format,
            pages=iter_ocr_pdf_pages(
                pdf_path,
                options,
                progress_callback=None if args.quiet else _print_progress,
            ),
        )
    except (PdfReadError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"OCR extracted {page_count} pages to {output_path}")
    if warning_count:
        print(f"Warning pages: {warning_count}")
    return 0


def _print_progress(current_index: int, total_pages: int, page_number: int) -> None:
    print(f"OCR {current_index}/{total_pages} (PDF page {page_number})...", flush=True)


def _write_ocr_output(
    pdf_path: Path,
    output_path: Path,
    output_format: str,
    pages: object,
) -> tuple[int, int]:
    page_count = 0
    warning_count = 0

    with output_path.open("w", encoding="utf-8", newline="\n") as output_file:
        if output_format == "markdown":
            output_file.write(f"# {pdf_path.stem}\n\n")
            output_file.write(f"Source PDF: `{pdf_path.name}`\n\n")

        for page in pages:
            if not isinstance(page, PageText):
                raise TypeError("OCR page iterator returned an invalid page object.")
            if page.warning:
                warning_count += 1
            if output_format == "markdown":
                _write_markdown_page(output_file, page)
            else:
                _write_text_page(output_file, page)
            output_file.flush()
            page_count += 1

    return page_count, warning_count


def _write_markdown_page(output_file: object, page: PageText) -> None:
    output_file.write(f"## Page {page.page_number}\n")
    if page.warning:
        output_file.write(f"> Warning: {page.warning}\n\n")
    output_file.write(f"{page.text or '[No extractable text]'}\n\n")


def _write_text_page(output_file: object, page: PageText) -> None:
    output_file.write(f"[[PAGE {page.page_number}]]\n")
    if page.warning:
        output_file.write(f"[Warning: {page.warning}]\n")
    output_file.write(f"{page.text or '[No extractable text]'}\n\n")


def _resolve_output_path(pdf_path: Path, output: Path | None, output_format: str) -> Path:
    if output is not None:
        return output.expanduser().resolve()
    suffix = ".md" if output_format == "markdown" else ".txt"
    return pdf_path.with_suffix(suffix)


if __name__ == "__main__":
    raise SystemExit(main())
