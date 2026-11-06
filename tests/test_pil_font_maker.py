"""Tests for pil_font_maker"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import requests
from PIL import Image, ImageChops, ImageDraw, ImageFont

from pil_font_maker import __version__
from pil_font_maker import pil_font_maker as pfm
from pil_font_maker.pil_font_maker import FontFileMaker, confirm, decode, encode, get_char

EXAMPLE_PIL = Path(pfm.__file__).parent / "fonts" / "example.pil"
EXAMPLE_GLYPHS = 95  # printable ASCII 32..126


@pytest.fixture(autouse=True)
def _in_tmp_path(tmp_path, monkeypatch):
    # the CLI functions write next to the current directory; keep that out of the repo
    monkeypatch.chdir(tmp_path)


def pngs(folder):
    return sorted(p.name for p in Path(folder).glob("char_*.png"))


def render(font, text):
    im = Image.new("1", (200, 20))
    ImageDraw.Draw(im).text((0, 0), text, font=font, fill=1)
    return im


# --- package ---------------------------------------------------------------


def test_version():
    assert __version__.count(".") == 2


@pytest.mark.parametrize("name", ["pil-font-maker", "pil-font-decode", "pil-font-encode", "pil-font-download"])
def test_entry_point_installed(name):
    if shutil.which(name) is None:
        if os.environ.get("CI"):
            pytest.fail(f"{name} not on PATH")
        pytest.skip(f"{name} not installed (pip install -e .)")


# --- CLI argument handling -------------------------------------------------


@pytest.mark.parametrize(
    "func, args",
    [
        (decode, ["decode"]),
        (decode, ["decode", "nonexistent.pil"]),
        (decode, ["decode", "README.md"]),
        (encode, ["encode"]),
        (encode, ["encode", "nonexistent_folder"]),
    ],
)
def test_bad_arguments_return_1(func, args):
    assert func(args) == 1


def test_encode_rejects_file_as_folder(tmp_path):
    (tmp_path / "a_file").write_text("x")
    assert encode(["encode", "a_file"]) == 1


def test_decode_rejects_existing_file_as_output_folder(tmp_path):
    (tmp_path / "taken").write_text("x")
    assert decode(["decode", str(EXAMPLE_PIL), "taken"]) == 1


@pytest.mark.parametrize("argv, expected", [([], "Usage: pil-font-maker"), (["bogus"], "unknown command bogus")])
def test_main_usage(argv, expected):
    result = subprocess.run([sys.executable, "-m", "pil_font_maker.pil_font_maker", *argv], capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert expected in result.stdout


# --- FontFileMaker -----------------------------------------------------------


def test_empty_constructor():
    font = FontFileMaker()
    assert font.char_count == 0
    assert len(font.glyph) == 256


def test_nonexistent_file():
    assert FontFileMaker("does_not_exist.pil").char_count == 0


def test_create_from_missing_folder_returns_self():
    font = FontFileMaker()
    assert font.create_from_folder("nope") is font
    assert font.char_count == 0


def test_round_trip_is_lossless(tmp_path):
    original = FontFileMaker(str(EXAMPLE_PIL))
    original.save_glyps_as_png_with_offset("decoded")
    assert original.char_count == EXAMPLE_GLYPHS
    assert len(pngs("decoded")) == EXAMPLE_GLYPHS

    assert encode(["encode", "decoded", "rebuilt.pil"]) == 0
    assert (tmp_path / "rebuilt.pil").is_file()
    assert (tmp_path / "rebuilt.pbm").is_file()

    assert decode(["decode", "rebuilt.pil", "redecoded"]) == 0
    assert pngs("redecoded") == pngs("decoded")
    for name in pngs("decoded"):
        with Image.open(tmp_path / "decoded" / name) as a, Image.open(tmp_path / "redecoded" / name) as b:
            assert a.size == b.size, name
            assert ImageChops.difference(a.convert("1"), b.convert("1")).getbbox() is None, name


@pytest.mark.parametrize("text", ["Hello, World!", "jgpqy", "0123456789"])
def test_rebuilt_font_renders_like_original(text):
    FontFileMaker(str(EXAMPLE_PIL)).save_glyps_as_png_with_offset("decoded")
    assert encode(["encode", "decoded", "rebuilt.pil"]) == 0

    original = render(ImageFont.load(str(EXAMPLE_PIL)), text)
    rebuilt = render(ImageFont.load("rebuilt.pil"), text)
    assert original.getbbox() is not None
    assert ImageChops.difference(original, rebuilt).getbbox() is None


# --- helpers -----------------------------------------------------------------


@pytest.mark.parametrize("code, char", [(65, "A"), (97, "a"), (48, "0"), (0, "."), (10, "."), (132, "")])
def test_get_char(code, char):
    assert get_char(code) == char


def test_confirm_silent_on_match(capsys):
    confirm(1, 1)
    confirm("abc", "abc")
    assert capsys.readouterr().out == ""


def test_confirm_reports_mismatch(capsys):
    confirm(1, 2)
    out = capsys.readouterr().out
    assert "expected :  2" in out
    assert "actual :  1" in out


# --- download (network mocked) -----------------------------------------------


class FakeResponse:  # pylint: disable=too-few-public-methods
    """Stand-in for requests.Response"""

    def __init__(self, status_code, content=b""):
        self.status_code = status_code
        self.content = content


def test_download_url_saves_file(tmp_path, monkeypatch):
    monkeypatch.setattr(pfm.requests, "get", lambda url, timeout: FakeResponse(200, b"data"))
    assert pfm.download_url("https://example.invalid/fonts/x.pil") is True
    assert (tmp_path / "x.pil").read_bytes() == b"data"


def test_download_url_bad_status(monkeypatch):
    monkeypatch.setattr(pfm.requests, "get", lambda url, timeout: FakeResponse(404))
    assert pfm.download_url("https://example.invalid/x.pil") is False


@pytest.mark.parametrize("exc", [requests.exceptions.Timeout, requests.exceptions.ConnectionError])
def test_download_url_network_error(monkeypatch, exc):
    def boom(url, timeout):
        raise exc("nope")

    monkeypatch.setattr(pfm.requests, "get", boom)
    assert pfm.download_url("https://example.invalid/x.pil") is False


def test_download_reports_failures(monkeypatch):
    calls = []
    monkeypatch.setattr(pfm, "download_url", lambda url: calls.append(url) or url.endswith(".pil"))
    assert pfm.download() == 1
    assert len(calls) == 10  # 5 fonts x (.pil + .pbm)


def test_download_all_ok(monkeypatch):
    monkeypatch.setattr(pfm, "download_url", lambda url: True)
    assert pfm.download() == 0
