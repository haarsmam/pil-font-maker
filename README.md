[![pypi version](https://img.shields.io/pypi/v/pil-font-maker)](https://pypi.org/project/pil-font-maker/)

# pil-font-maker
Extract a png image for each character in a PIL ImageFont and store them in a folder.
Contruct a PIL ImageFont from a folder containing a png image for each character.

![example.png](https://raw.githubusercontent.com/haarsmam/pil-font-maker/main/pil_font_maker/example/example.png)

## Installation
`python -m pip install pil-font-maker`

## Supported Commands

On a command line type:

`pil-font-decode`

Usage: pil-font-decode &lt;file.pil&gt; [folder]

To convert a .pil/.pbm ImageFont to a folder containing a .png for each character present

`pil-font-encode`

Usage: pil-font-encode &lt;folder&gt; [file.pil]

Convert a folder containing a .png for each character to a .pil/.pbm ImageFont.
The pngs should be named char_0.png, char_1.png upto char_255.png
Omitted pngs will result in empty characters.

`pil-font-download`

Usage: pil-font-download

Download some sample pil fonts from the [pillow](https://github.com/python-pillow/Pillow/tree/main/Tests/fonts) github repository
