#!/usr/bin/env pwsh

# Test script for pil-font-maker
# Run locally: pwsh test_posh.ps1
# Requires: pip install -e . (and requirements-workflow.txt for lint tests)

param(
    [switch]$SkipLint,
    [switch]$LintOnly
)

$ErrorActionPreference = "Continue"
$script:failed = 0
$script:passed = 0

function Run-Test {
    param([string]$Name, [scriptblock]$Test)
    Write-Host "`n--- $Name ---" -ForegroundColor Cyan
    try {
        & $Test
        if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
            throw "Exit code: $LASTEXITCODE"
        }
        Write-Host "PASS: $Name" -ForegroundColor Green
        $script:passed++
    } catch {
        Write-Host "FAIL: $Name - $_" -ForegroundColor Red
        $script:failed++
    }
}

# --- Environment ---
Write-Host "PowerShell $($PSVersionTable.PSVersion) on $($PSVersionTable.OS)" -ForegroundColor Magenta
Write-Host "Python $(python --version 2>&1)" -ForegroundColor Magenta

# --- Lint tests ---
if (-not $SkipLint) {
    Run-Test "black formatting" {
        black pil_font_maker --check --diff
    }

    Run-Test "flake8" {
        flake8 pil_font_maker
    }

    Run-Test "mypy" {
        mypy pil_font_maker
    }

    Run-Test "pylint" {
        pylint pil_font_maker
    }
}

if ($LintOnly) {
    Write-Host "`n=== Results: $script:passed passed, $script:failed failed ===" -ForegroundColor Magenta
    exit $script:failed
}

# --- Import tests ---
Run-Test "import package" {
    python -c "from pil_font_maker import __version__; print('version:', __version__)"
}

Run-Test "import FontFileMaker" {
    python -c "from pil_font_maker.pil_font_maker import FontFileMaker; print('FontFileMaker imported')"
}

Run-Test "import entry points" {
    python -c "from pil_font_maker.pil_font_maker import encode, decode, download, path; print('All entry points imported')"
}

# --- CLI entry point tests ---
Run-Test "CLI commands installed" {
    $commands = @("pil-font-maker", "pil-font-decode", "pil-font-encode", "pil-font-download")
    foreach ($cmd in $commands) {
        $result = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($result) {
            Write-Host "  OK: $cmd found at $($result.Source)"
        } else {
            throw "$cmd not found in PATH"
        }
    }
}

# --- Argument validation tests ---
Run-Test "decode: no args returns exit code 1" {
    python -c "from pil_font_maker.pil_font_maker import decode; exit(decode(['decode']))"
    if ($LASTEXITCODE -ne 1) { throw "Expected exit code 1, got $LASTEXITCODE" }
    $LASTEXITCODE = 0  # reset so Run-Test doesn't see failure
}

Run-Test "encode: no args returns exit code 1" {
    python -c "from pil_font_maker.pil_font_maker import encode; exit(encode(['encode']))"
    if ($LASTEXITCODE -ne 1) { throw "Expected exit code 1, got $LASTEXITCODE" }
    $LASTEXITCODE = 0
}

Run-Test "encode: nonexistent folder returns exit code 1" {
    python -c "from pil_font_maker.pil_font_maker import encode; exit(encode(['encode', 'nonexistent_folder']))"
    if ($LASTEXITCODE -ne 1) { throw "Expected exit code 1, got $LASTEXITCODE" }
    $LASTEXITCODE = 0
}

Run-Test "decode: nonexistent file returns exit code 1" {
    python -c "from pil_font_maker.pil_font_maker import decode; exit(decode(['decode', 'nonexistent.pil']))"
    if ($LASTEXITCODE -ne 1) { throw "Expected exit code 1, got $LASTEXITCODE" }
    $LASTEXITCODE = 0
}

Run-Test "decode: non-.pil file returns exit code 1" {
    python -c "from pil_font_maker.pil_font_maker import decode; exit(decode(['decode', 'README.md']))"
    if ($LASTEXITCODE -ne 1) { throw "Expected exit code 1, got $LASTEXITCODE" }
    $LASTEXITCODE = 0
}

# --- Unit tests ---
Run-Test "FontFileMaker empty constructor" {
    python -c @"
from pil_font_maker.pil_font_maker import FontFileMaker
f = FontFileMaker()
assert f.char_count == 0, 'Expected 0 chars'
assert len(f.glyph) == 256, 'Expected 256 glyph slots'
print('Empty FontFileMaker: OK')
"@
}

Run-Test "FontFileMaker nonexistent file" {
    python -c @"
from pil_font_maker.pil_font_maker import FontFileMaker
f = FontFileMaker('does_not_exist.pil')
assert f.char_count == 0, 'Expected 0 chars'
print('Nonexistent file FontFileMaker: OK')
"@
}

Run-Test "get_char helper" {
    python -c @"
from pil_font_maker.pil_font_maker import get_char
assert get_char(65) == 'A'
assert get_char(97) == 'a'
assert get_char(48) == '0'
assert get_char(0) == '.'
assert get_char(132) == ''
print('get_char: OK')
"@
}

Run-Test "confirm helper" {
    python -c @"
from pil_font_maker.pil_font_maker import confirm
confirm(1, 1)
confirm('abc', 'abc')
print('confirm: OK')
"@
}

# --- Round-trip test ---
Run-Test "encode/decode round-trip with bundled font" {
    $tempDir = Join-Path ([System.IO.Path]::GetTempPath()) "pil_font_test_$(Get-Random)"
    python -c @"
import os, sys
sys.path.insert(0, '.')
from pil_font_maker.pil_font_maker import FontFileMaker

temp = '$($tempDir -replace "\\", "/")'
font_pil = os.path.join('pil_font_maker', 'fonts', 'example.pil')
if not os.path.exists(font_pil):
    print(f'SKIP: {font_pil} not found')
    sys.exit(0)

f = FontFileMaker(font_pil)
print(f'Loaded font with {f.char_count} characters')

decode_dir = os.path.join(temp, 'decoded')
f.save_glyps_as_png_with_offset(decode_dir)
assert os.path.isdir(decode_dir), 'Output folder not created'

png_files = [x for x in os.listdir(decode_dir) if x.endswith('.png')]
assert len(png_files) > 0, 'No PNG files generated'
print(f'Decoded {len(png_files)} glyphs to PNG')

f2 = FontFileMaker()
f2.create_from_folder(decode_dir)
roundtrip = os.path.join(temp, 'roundtrip')
f2.save(roundtrip)
assert os.path.exists(roundtrip + '.pil'), '.pil not created'
assert os.path.exists(roundtrip + '.pbm'), '.pbm not created'
print('Round-trip: OK')
"@
    if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force }
}

# --- Summary ---
Write-Host "`n=== Results: $script:passed passed, $script:failed failed ===" -ForegroundColor Magenta
exit $script:failed
