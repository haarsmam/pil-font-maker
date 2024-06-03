# pil-font-maker
Extract a png image for each character in a PIL font and store them in a folder.
Contruct a PIL font from a folder containing a png image for each character.

## Installation
`python -m pip install pil-font-maker`

## Supported Commands

On a command line type:

>pil-font-decode

Usage: pil-font-decode file.pil [folder]

Convert a pil font to a folder containing a png for each character present


>pil-font-encode 

Usage: pil-font-encode folder [file.pil]

Convert a folder containing a png for each character to a pil font.
The pngs should be named char_0.png, char_1.png upto char_255.png
Omitted pngs will result in empty characters.

>pil-font-download

Usage: pil-font-download

Download some sample pil fonts from the [pillow](https://github.com/python-pillow/Pillow/tree/main/Tests/fonts) github repository
