# pdf-analyzer

把 PDF 书籍提取成适合 AI 阅读的 Markdown 或纯文本。

支持两种路线：

- `pdf-extract`：处理"可以选中文字复制"的 PDF。
- `pdf-ocr`：处理扫描版、图片版 PDF，需要本机安装 `pdftoppm`。

## 安装

Windows:

```powershell
.\scripts\install.ps1
```

Linux / macOS:

```bash
./scripts/install.sh
```

一键脚本会自动处理：安装 `uv` → `uv sync`（自动下载 Python + 安装依赖）→ 检查 `pdftoppm`（OCR 需要，缺则自动安装）。

## 使用

### 可复制文字 PDF

提取整本书为 Markdown：

```powershell
uv run pdf-extract "book.pdf"
```

指定输出文件：

```powershell
uv run pdf-extract "book.pdf" -o "output/book.md"
```

只提取部分页码：

```powershell
uv run pdf-extract "book.pdf" --start 1 --end 30 -o "output/sample.md"
```

输出纯文本：

```powershell
uv run pdf-extract "book.pdf" --format text -o "output/book.txt"
```

保留 PDF 原始换行：

```powershell
uv run pdf-extract "book.pdf" --preserve-line-breaks
```

或者先激活虚拟环境再运行：

```powershell
# 激活 .venv 后直接使用命令
pdf-extract "book.pdf"
pdf-ocr "scanned-book.pdf"
```

## 输出格式

Markdown 输出会保留页码边界：

```markdown
# book

Source PDF: `book.pdf`

## Page 1
第一页内容...

## Page 2
第二页内容...
```

这种格式方便后续给 AI 分批输入、定位页码、做引用或摘要。

## 说明

- 默认会合并段落内换行，让长书文本更适合 AI 读取。
- 默认会移除英文行尾断词，例如 `medita-\ntion` 会合并为 `meditation`。
- 如果某页提取到的文字少于 20 个字符，会标记为疑似扫描页或图片页。
- 几百页 PDF 可以直接运行；如需先测试效果，建议先用 `--start` 和 `--end` 取前几十页。

## 扫描版 PDF OCR

扫描版 PDF 使用 `RapidOCR` 识别，通过 `pdftoppm` 把 PDF 页面渲染成图片再交给 OCR 处理。

需要：

- `pdftoppm`：把 PDF 页面渲染成图片。
- `rapidocr` + `onnxruntime`：OCR 后端（由 `uv sync` 自动安装）。

建议先只跑前 3 页测试识别效果：

```powershell
uv run pdf-ocr "scanned-book.pdf" --start 1 --end 3 -o "output/ocr-sample.md"
```

识别整本扫描书：

```powershell
uv run pdf-ocr "scanned-book.pdf" -o "output/scanned-book.md"
```

指定 RapidOCR 置信度阈值，过滤低置信度碎片：

```powershell
uv run pdf-ocr "scanned-book.pdf" --rapid-score-thresh 0.5 -o "output/scanned-book.md"
```

若 `pdftoppm` 不在 PATH，可指定完整路径：

```powershell
uv run pdf-ocr "scanned-book.pdf" --pdftoppm "C:\Program Files\poppler\bin\pdftoppm.exe" -o "output/scanned-book.md"
```

OCR 参数建议：

- `--dpi 200`：默认值，速度和质量较均衡。
- `--dpi 300`：可尝试用于小字号或模糊扫描，但会更慢。
- `--rapid-score-thresh 0.5`：过滤低置信度识别结果。
- `--image-dir output/page-images`：保留中间图像，方便检查 OCR 渲染结果。
- `--preserve-line-breaks`：保留 OCR 原始换行；默认会合并同一段落内的换行。
- `--quiet`：只输出最终结果，不打印逐页 OCR 进度。

扫描版 OCR 会逐页写入输出文件。即使中途停止，也会保留已经识别完成的页面。
