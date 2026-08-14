#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# ---- 1. 安装 / 检查 uv ----
if ! command -v uv >/dev/null 2>&1; then
  echo "正在安装 uv（Python 包管理器）..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # 刷新 PATH
  export PATH="$HOME/.local/bin:$PATH"
  if ! command -v uv >/dev/null 2>&1; then
    echo "uv 安装失败，请手动安装：curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
  fi
  echo "uv 安装完成: $(command -v uv)"
else
  echo "uv 已安装: $(command -v uv)"
fi

# ---- 2. uv self update（可选） ----
echo "检查 uv 更新..."
uv self update 2>/dev/null || true

# ---- 3. 用 uv 安装 Python 和项目依赖 ----
echo "安装 Python 依赖（uv sync）..."
uv sync
echo "Python 依赖安装完成。"

# ---- 4. 检查 pdftoppm ----
echo "检查 pdftoppm..."
if command -v pdftoppm >/dev/null 2>&1; then
  echo "pdftoppm 已安装: $(command -v pdftoppm)"
  pdftoppm -v | head -n 1
  exit 0
fi

if command -v apt-get >/dev/null 2>&1; then
  echo "通过 apt-get 安装 Poppler..."
  sudo apt-get update
  sudo apt-get install -y poppler-utils
  exit 0
fi

if command -v yum >/dev/null 2>&1; then
  echo "通过 yum 安装 Poppler..."
  sudo yum install -y poppler-utils
  exit 0
fi

if command -v dnf >/dev/null 2>&1; then
  echo "通过 dnf 安装 Poppler..."
  sudo dnf install -y poppler-utils
  exit 0
fi

if command -v pacman >/dev/null 2>&1; then
  echo "通过 pacman 安装 Poppler..."
  sudo pacman -Syu --noconfirm poppler
  exit 0
fi

echo "未检测到受支持的 Linux 包管理器，请手动安装 pdftoppm。"
echo "你可以使用系统包管理器安装 poppler-utils，或访问 https://poppler.freedesktop.org/ 进行下载。"
exit 1
