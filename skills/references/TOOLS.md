# 工具使用说明

## PDF 材料

处理用户提供的 PDF 时，必须使用本 workspace 自带的 `../scripts/pdf-analyzer/`，不得改用模型内置 PDF 阅读能力或其他 PDF skill。

执行前检查：

```powershell
Get-Command uv
Test-Path "..\scripts\pdf-analyzer\.venv"
Get-Command pdftoppm
```

环境未就绪时：

- Windows：`..\scripts\pdf-analyzer\scripts\install.ps1`
- Linux/macOS：`../scripts/pdf-analyzer/scripts/install.sh`

在 `../scripts/pdf-analyzer/` 工作目录中执行，并优先使用绝对路径：

- 可复制文字 PDF：`uv run pdf-extract "<绝对输入路径>" -o "../scripts/pdf-analyzer/tmp/extracted.md"`
- 扫描版 PDF：`uv run pdf-ocr "<绝对输入路径>" -o "../scripts/pdf-analyzer/tmp/extracted.md"`

提取结果默认写入 `../scripts/pdf-analyzer/tmp/`。只有确需归档时才移到长期位置；任务结束后清理不再需要的临时产物。

详细材料处理规则见 `guides/临床工作流程.md`。
