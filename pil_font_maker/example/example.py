#! /usr/bin/env python3
# coding=utf-8

""" Example usage of PIL ImageFont """

import os
from PIL import Image, ImageFont, ImageDraw


def example():
    """Creates an example.png with some PIL ImageFont"""

    if not os.path.isfile("../fonts/10x20.pil"):

        print("Please run pil-font-download in the fonts folder first")

        return 1

    img = Image.new("RGB", (320, 240), (0, 0, 0))

    draw = ImageDraw.Draw(img)

    text = "abcdefghijklmnopqrstuvwxyz 0123456789"

    font = ImageFont.load("../fonts/example.pil")

    draw.text((10, 10), text, font=font)

    font = ImageFont.load("../fonts/10x20.pil")

    draw.text((10, 40), text, font=font)

    font = ImageFont.load("../fonts/courB08.pil")

    draw.text((10, 70), text, font=font)

    img.save("example.png", "png")

    return 0


if __name__ == "__main__":

    example()
