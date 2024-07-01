#! /usr/bin/env python3
# coding=utf-8

""" Setup file for the pil-font-maker package """

from setuptools import setup
from pil_font_maker import __version__

setup(
    name="pil-font-maker",
    version=__version__,
    description="A tool to make a PILfont from png images",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Marc Haarsma",
    author_email="marc.haarsma@gmail.com",
    url="https://github.com/haarsmam/pil-font-maker",
    packages=["pil_font_maker"],
    install_requires=["Pillow"],
    entry_points={
        "console_scripts": [
            "pil-font-maker    = pil_font_maker.pil_font_maker:main",
            "pil-font-decode   = pil_font_maker.pil_font_maker:decode",
            "pil-font-encode   = pil_font_maker.pil_font_maker:encode",
            "pil-font-download = pil_font_maker.pil_font_maker:download",
        ]
    },
)
