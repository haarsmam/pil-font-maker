[![pypi version](https://img.shields.io/pypi/v/pil-font-maker)](https://pypi.org/project/pil-font-maker/)

# pil-font-maker
Extract a PNG image for each character in a PIL ImageFont and store them in a folder.
Construct a PIL ImageFont from a folder containing a PNG image for each character.

This is my answer to [how-to-use-my-own-bitmap-font-in-pil-imagefont](https://stackoverflow.com/questions/53021488/how-to-use-my-own-bitmap-font-in-pil-imagefont)

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
The PNGs should be named char_0.png, char_1.png up to char_255.png
Omitted PNGs will result in empty characters.

`pil-font-download`

Usage: pil-font-download

Download some sample PIL ImageFonts from the [pillow](https://github.com/python-pillow/Pillow/tree/main/Tests/fonts) GitHub repository
