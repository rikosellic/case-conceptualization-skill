# pdf-analyzer 安装脚本 (Windows)
# 用法: .\scripts\install.ps1

$ErrorActionPreference = "Stop"
Write-Host "=== pdf-analyzer 安装脚本 ===" -ForegroundColor Cyan

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptRoot "..")
Set-Location $repoRoot

# ---- 1. 安装 / 检查 uv ----
$uvCmd = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uvCmd) {
    Write-Host "正在安装 uv（Python 包管理器）..." -ForegroundColor Yellow
    # 优先用 winget，否则用独立安装程序
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        winget install --id=astral-sh.uv -e --accept-source-agreements --accept-package-agreements
        # winget 安装后需要刷新 PATH
        $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "User") + ";$env:PATH"
        $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";$env:PATH"
    } else {
        # 用独立安装程序
        PowerShell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        $env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
    }
    $uvCmd = Get-Command uv -ErrorAction SilentlyContinue
    if (-not $uvCmd) {
        Write-Error "uv 安装失败，请手动安装：winget install --id=astral-sh.uv -e"
        exit 1
    }
    Write-Host "uv 安装完成: $($uvCmd.Source)" -ForegroundColor Green
} else {
    Write-Host "uv 已安装: $($uvCmd.Source)" -ForegroundColor Green
}

# ---- 2. uv self update（可选） ----
Write-Host "检查 uv 更新..." -ForegroundColor Cyan
uv self update 2>$null

# ---- 3. 用 uv 安装 Python 和项目依赖 ----
Write-Host "安装 Python 依赖（uv sync）..." -ForegroundColor Cyan
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Error "uv sync 失败"
    exit 1
}
Write-Host "Python 依赖安装完成。" -ForegroundColor Green

# ---- 4. 检查 pdftoppm ----
Write-Host "检查 pdftoppm..." -ForegroundColor Cyan
$existing = Get-Command pdftoppm -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "pdftoppm 已安装: $($existing.Source)" -ForegroundColor Green
    pdftoppm -v 2>&1 | Select-Object -First 1
    exit 0
}

$winget = Get-Command winget -ErrorAction SilentlyContinue
if ($winget) {
    Write-Host "通过 winget 安装 Poppler..." -ForegroundColor Yellow
    winget install oschwartz10612.Poppler --accept-source-agreements --accept-package-agreements
    Write-Host "安装完成！请重新打开终端使 PATH 生效。" -ForegroundColor Green
    Write-Host "或者将以下路径加入 PATH: `$env:LOCALAPPDATA\Microsoft\WinGet\Packages\oschwartz10612.Poppler_*\Library\bin" -ForegroundColor Gray
    exit 0
}

Write-Host "未找到 winget，尝试通过 GitHub 下载..." -ForegroundColor Yellow

$popplerUrl = "https://github.com/oschwartz10612/poppler-windows/releases/latest"
$installDir = "$env:USERPROFILE\poppler"

Write-Host ""
Write-Host "pdftoppm 未安装，自动安装失败，请手动安装：" -ForegroundColor Red
Write-Host "  1. 打开: $popplerUrl" -ForegroundColor White
Write-Host "  2. 下载最新 Release-xx.xx.zip" -ForegroundColor White
Write-Host "  3. 解压到: $installDir" -ForegroundColor White
Write-Host "  4. 将以下路径加入 PATH:" -ForegroundColor White
Write-Host "     $installDir\Library\bin" -ForegroundColor Cyan
Write-Host ""
Write-Host "或安装包管理器后重试:" -ForegroundColor Gray
Write-Host "  winget: 系统自带 (Win10 1809+)" -ForegroundColor Gray
Write-Host "  scoop:  Set-ExecutionPolicy RemoteSigned -Scope CurrentUser; irm get.scoop.sh | iex" -ForegroundColor Gray
