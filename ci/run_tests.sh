#!/usr/bin/env bash
set -euo pipefail

echo "Starting test execution..."

VENV_DIR=".venv"

# -----------------------
# Check virtual environment exists
# -----------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found at $VENV_DIR"
    exit 1
fi

# -----------------------
# Detect OS / shell
# -----------------------
OS_TYPE="$(uname 2>/dev/null || echo Windows_NT)"
IS_POWERSHELL=false

if [ -n "${PSModulePath-}" ]; then
    OS_TYPE="Windows_NT"
    IS_POWERSHELL=true
fi

# -----------------------
# Activate virtual environment
# -----------------------
if [[ "$OS_TYPE" == "Linux" || "$OS_TYPE" == "Darwin" ]]; then
    # Linux / macOS / WSL
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    else
        echo "Cannot find $VENV_DIR/bin/activate"
        exit 1
    fi
elif [[ "$OS_TYPE" == "Windows_NT" ]]; then
    if $IS_POWERSHELL; then
        # PowerShell fallback
        if command -v pwsh >/dev/null 2>&1; then
            PS_CMD="pwsh"
        else
            PS_CMD="powershell.exe"
        fi

        echo "Detected PowerShell. Running pytest inside $PS_CMD..."
        "$PS_CMD" -NoProfile -Command "& {Set-ExecutionPolicy Bypass -Scope Process; . '$VENV_DIR/Scripts/Activate.ps1'; pytest -v -s $*}"
        exit 0
    else
        # Git Bash / MSYS / Cygwin
        if [ -f "$VENV_DIR/Scripts/activate" ]; then
            source "$VENV_DIR/Scripts/activate"
        else
            echo "Cannot find $VENV_DIR/Scripts/activate"
            exit 1
        fi
    fi
else
    echo "Unknown platform: $OS_TYPE"
    exit 1
fi

# -----------------------
# Run pytest (for bash/Linux)
# -----------------------
pytest -v -s "$@"
