from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from typing import Callable

from pypdf import PdfReader

from pdf_analyzer.extractor import PageText, normalize_text


@dataclass(frozen=True)
class OcrOptions:
    rapid_score_thresh: float = 0.0
    dpi: int = 200
    page_start: int | None = None
    page_end: int | None = None
    preserve_line_breaks: bool = False
    pdftoppm_cmd: str = "pdftoppm"
    min_chars_per_page: int = 20
    image_dir: Path | None = None


def ocr_pdf_pages(
    pdf_path: Path,
    options: OcrOptions,
    progress_callback: Callable[[int, int, int], None] | None = None,
) -> list[PageText]:
    return list(iter_ocr_pdf_pages(pdf_path, options, progress_callback))


def iter_ocr_pdf_pages(
    pdf_path: Path,
    options: OcrOptions,
    progress_callback: Callable[[int, int, int], None] | None = None,
) -> Iterator[PageText]:
    _require_command(options.pdftoppm_cmd, "pdftoppm")

    reader = PdfReader(pdf_path)
    page_count = len(reader.pages)
    start_page = _normalize_start(options.page_start, page_count)
    end_page = _normalize_end(options.page_end, page_count)

    if start_page > end_page:
        raise ValueError("起始页不能大于结束页。")

    if options.image_dir:
        options.image_dir.mkdir(parents=True, exist_ok=True)
        yield from _ocr_with_image_dir(
            pdf_path,
            options,
            start_page,
            end_page,
            options.image_dir,
            progress_callback,
        )
    else:
        with tempfile.TemporaryDirectory(prefix="pdf-ocr-") as temp_dir:
            yield from _ocr_with_image_dir(
                pdf_path,
                options,
                start_page,
                end_page,
                Path(temp_dir),
                progress_callback,
            )


def _ocr_with_image_dir(
    pdf_path: Path,
    options: OcrOptions,
    start_page: int,
    end_page: int,
    image_dir: Path,
    progress_callback: Callable[[int, int, int], None] | None,
) -> Iterator[PageText]:
    total_pages = end_page - start_page + 1
    rapid_engine = _create_rapid_engine()
    for current_index, page_number in enumerate(range(start_page, end_page + 1), start=1):
        if progress_callback:
            progress_callback(current_index, total_pages, page_number)
        image_path = _render_page(pdf_path, options, page_number, image_dir)
        raw_text = _run_rapidocr(image_path, rapid_engine, options)
        text = normalize_text(raw_text, preserve_line_breaks=options.preserve_line_breaks)
        warning = None
        if len(text.strip()) < options.min_chars_per_page:
            warning = "本页 OCR 识别到的文字很少，可能是空白页、图片质量低或语言包不匹配。"
        yield PageText(page_number=page_number, text=text, warning=warning)


def _render_page(pdf_path: Path, options: OcrOptions, page_number: int, image_dir: Path) -> Path:
    prefix = image_dir / f"page-{page_number:04d}"
    command = [
        options.pdftoppm_cmd,
        "-f",
        str(page_number),
        "-l",
        str(page_number),
        "-r",
        str(options.dpi),
        "-png",
        str(pdf_path),
        str(prefix),
    ]
    _run(command, f"渲染第 {page_number} 页失败")

    candidates = sorted(image_dir.glob(f"{prefix.name}-*.png"))
    if not candidates:
        raise RuntimeError(f"渲染第 {page_number} 页后没有找到图片输出。")
    return candidates[0]


def _create_rapid_engine() -> object:
    try:
        from rapidocr import RapidOCR
    except ImportError as exc:
        raise RuntimeError(
            "未安装 RapidOCR。请先运行：python -m pip install rapidocr onnxruntime，然后重试。"
        ) from exc

    return RapidOCR()


def _run_rapidocr(image_path: Path, engine: object, options: OcrOptions) -> str:
    if engine is None:
        raise RuntimeError("RapidOCR 引擎没有初始化。")

    result = engine(str(image_path), use_det=True, use_cls=True, use_rec=True)
    texts = _extract_rapid_text(result, options.rapid_score_thresh)
    return "\n".join(texts)


def _extract_rapid_text(result: object, score_thresh: float) -> list[str]:
    if hasattr(result, "txts"):
        texts = getattr(result, "txts") or []
        scores = getattr(result, "scores", None) or [1.0] * len(texts)
        return [
            str(text)
            for text, score in zip(texts, scores, strict=False)
            if str(text).strip() and float(score) >= score_thresh
        ]

    if isinstance(result, tuple) and result:
        result = result[0]

    if not isinstance(result, list):
        return []

    texts: list[str] = []
    for item in result:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue
        payload = item[1]
        if isinstance(payload, (list, tuple)) and payload:
            text = payload[0]
            score = float(payload[1]) if len(payload) > 1 else 1.0
            if str(text).strip() and score >= score_thresh:
                texts.append(str(text))
    return texts


def _run(command: list[str], error_prefix: str) -> str:
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"找不到命令：{command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        detail = f": {stderr}" if stderr else ""
        raise RuntimeError(f"{error_prefix}{detail}") from exc
    return completed.stdout


def _require_command(command: str, label: str) -> None:
    if Path(command).exists():
        return
    if shutil.which(command):
        return
    raise RuntimeError(f"找不到 {label} 命令：{command}")


def _normalize_start(page_start: int | None, page_count: int) -> int:
    if page_start is None:
        return 1
    if page_start < 1:
        raise ValueError("起始页必须大于等于 1。")
    if page_start > page_count:
        raise ValueError(f"起始页超过 PDF 总页数：{page_count}。")
    return page_start


def _normalize_end(page_end: int | None, page_count: int) -> int:
    if page_end is None:
        return page_count
    if page_end < 1:
        raise ValueError("结束页必须大于等于 1。")
    if page_end > page_count:
        raise ValueError(f"结束页超过 PDF 总页数：{page_count}。")
    return page_end
