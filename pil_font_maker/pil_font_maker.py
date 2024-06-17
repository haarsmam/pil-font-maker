#! /usr/bin/env python3
# coding=utf-8

from inspect import getframeinfo, stack
import os
import logging
import struct
import sys
import requests
import PIL  # python -m pip install Pillow
from PIL import FontFile
from PIL import Image


# raster , bitmap , font

# https://github.com/python-pillow/Pillow/pull/1072

# https://stackoverflow.com/questions/53021488/how-to-use-my-own-bitmap-font-in-pil-imagefont

# https://github.com/python-pillow/Pillow/blob/main/src/PIL/FontFile.py
# https://github.com/python-pillow/Pillow/blob/main/src/PIL/ImageFont.py

# https://stackoverflow.com/questions/30782756/a-better-way-to-add-text-to-ca-cvmat-than-cvputtext

# https://stackoverflow.com/questions/50268092/save-1-bit-deep-binary-image-in-python
# https://stackoverflow.com/questions/44997339/convert-python-image-to-single-channel-from-rgb-using-pil-or-scipy

# find . | grep .pil$
# ./Tests/fonts/ter-x20b-cp1250.pil
# ./Tests/fonts/ter-x20b-iso8859-1.pil
# ./Tests/fonts/ter-x20b-iso8859-2.pil
# ./Tests/fonts/10x20.pil
# ./Tests/images/courB08.pil

# find . | grep .pbm$
# ./Tests/fonts/ter-x20b-cp1250.pbm
# ./Tests/fonts/ter-x20b-iso8859-1.pbm
# ./Tests/fonts/ter-x20b-iso8859-2.pbm
# ./Tests/fonts/10x20.pbm
# ./Tests/images/hopper_1bit_plain.pbm
# ./Tests/images/courB08.pbm
# ./Tests/images/hopper_1bit.pbm


# find . | grep hopper_1bit*.*
# ./Tests/images/hopper_1bit_plain.pbm
# ./Tests/images/hopper_1bit.pbm


# import logging
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)


def main():

    argc = len(sys.argv)
    if argc > 1:

        command = sys.argv[1]

        if command == "path":
            return path()

        if command == "download":
            return download()

        if command == "decode":
            return decode(sys.argv[1:])

        if command == "encode":
            return encode(sys.argv[1:])

        print("test")
        test()

    print("main")


def encode(args=None):

    if args is None:
        args = sys.argv

    argc = len(args)
    if argc == 1:
        print("Usage: pil-font-encode folder [file.pil]")
        return 1

    folder = args[1]

    if not os.path.exists(folder):
        print("the provided folder does not exist : " + folder)
        return 1

    if not os.path.isdir(folder):
        print("the provided folder is not a folder : " + folder)
        return 1

    file_name = os.path.basename(folder)

    if argc == 3:
        file_name = args[2]

    if not file_name.endswith(".pil"):
        file_name += ".pil"

    empty_pil = FontFileMaker()
    empty_pil.create_from_folder(folder)
    empty_pil.save(file_name)

    print(
        "encoded",
        empty_pil.char_count,
        "characters from folder",
        folder,
        "to",
        file_name,
        "and",
        os.path.splitext(file_name)[0] + ".pbm",
    )

    return 0


def decode(args=None):

    if args is None:
        args = sys.argv

    argc = len(args)
    if argc == 1:
        print("Usage: pil-font-decode file.pil [folder]")
        return 1

    file_name = args[1]

    if not file_name.endswith(".pil"):
        print("unexpected : file name does not end with '.pil'")
        return 1

    if not os.path.exists(file_name):
        print("the provided file does not exist : " + file_name)
        return 1

    if not os.path.isfile(file_name):
        print("the provided file is not a file : " + file_name)
        return 1

    folder = None
    # folder too
    if argc == 3:

        folder = args[2]

        if os.path.isfile(folder):
            print("a file with this name exists : " + folder)
            return 1

    xxx = FontFileMaker(file_name)
    xxx.save_glyps_as_png_with_offset(folder)

    print("decoded", xxx.char_count, "characters to folder", xxx.root_path)

    return 0


def path():
    exe = sys.executable

    print(sys.executable)
    print(os.path.dirname(exe))

    scripts = os.path.join(os.path.dirname(exe), "Scripts")
    print("set  path=%path%;" + scripts)
    print('setx path "%path%;' + scripts + '"')

    return 0


def download():

    pil_urls = [
        "https://raw.githubusercontent.com/python-pillow/Pillow/main/Tests/fonts/10x20.pil",
        "https://raw.githubusercontent.com/python-pillow/Pillow/main/Tests/fonts/ter-x20b-cp1250.pil",
        "https://raw.githubusercontent.com/python-pillow/Pillow/main/Tests/fonts/ter-x20b-iso8859-1.pil",
        "https://raw.githubusercontent.com/python-pillow/Pillow/main/Tests/fonts/ter-x20b-iso8859-2.pil",
        "https://raw.githubusercontent.com/python-pillow/Pillow/main/Tests/images/courB08.pil",
        "https://raw.githubusercontent.com/haarsmam/pil-font-maker/main/pil_font_maker/fonts/example.pil",
    ]

    for pil_url in pil_urls:

        download_url(pil_url)

        # Replace .pil with .pbm in the URL to download the .pbm file
        pbm_url = pil_url.replace(".pil", ".pbm")

        download_url(pbm_url)

    return 0


def download_url(url):
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Get the font name from the URL
        file_name = url.split("/")[-1]

        print(file_name)

        # Write the content of the response to a file
        with open(file_name, "wb") as font_file:
            font_file.write(response.content)
    else:
        print("wrong url", url)
        return


def test():

    logging.debug(PIL.__version__)

    print("pil version", PIL.__version__)
    print("package path", PIL.__file__)
    print(os.path.dirname(PIL.__file__))

    pil_10x20 = FontFileMaker("fonts/10x20.pil")
    pil_10x20.save_glyps_as_png("test_10x20")
    pil_10x20.save_glyps_as_png_with_offset("test_10x20_offset")
    empty_pil = FontFileMaker("does not exist")
    empty_pil.create_from_folder("test_10x20_offset")
    empty_pil.save("test_10x20_offset")

    marc_pil = FontFileMaker("fonts/example.pil")
    marc_pil.save_glyps_as_png("test_example")
    dst = "test_example_with_offset"
    marc_pil.save_glyps_as_png_with_offset(dst)
    marc_pil.save(dst)  # glyps still have offset info.
    # make_proporational(dst)

    empty_pil = FontFileMaker("does not exist")
    empty_pil.create_from_folder(dst)
    empty_pil.save("empty")
    # print(empty_pil.max_dims())

    full_pil = FontFileMaker("empty.pil")
    full_pil.save_glyps_as_png_with_offset("test_full")

    # marc_pil.save_glyps_as_png()
    # marc_new_pil = PILfont('marc_new.pil')
    # courB08_pil = PILfont('courB08.pil')
    # need to download pil fronts from


class FontFileMaker(FontFile.FontFile):

    def __del__(self):

        logging.debug("destructor")

        for glyph in self.glyph:

            if glyph:

                glyph[3].close()

    def __init__(self, filename: str = ""):

        super().__init__()

        # so we init info and glyph
        # self.info = {}
        # self.glyph = [None] * 256

        # metric
        # bitmap
        # ysize

        self.char_count = 0

        if not os.path.exists(filename):  # empty font

            return

        if os.path.isdir(filename):

            self.create_from_folder(filename)

            return

        if not filename.endswith(".pil"):

            print("unexpected : file name does not end with '.pil'")

            return

        self.root_path = os.path.splitext(filename)[0]

        self.filename = filename

        self.bytes_per_glyph = 20
        self.glyph_size = self.bytes_per_glyph * 256
        self.header_size = os.path.getsize(filename) - self.glyph_size

        # from super
        # self.info = {}
        # self.glyph = [None] * 256

        self.read_glyphs()  # needed, reads in glyph data

        h = self.determine_font_height()

        if self.font_height != h:

            logging.debug("updating font_height", self.font_height, "->", h)

            self.font_height = h

    # constructor ???    / factory method / static method
    def create_from_folder(self, folder: str):

        # do not need to allocated, save -> compile does this.
        # just read glyphs

        if not os.path.isdir(folder):
            print(folder + " is not a folder")
            return

        for i in range(256):

            file_path = os.path.join(folder, "char_" + str(i) + ".png")

            if os.path.isfile(file_path):

                self.char_count += 1

                im = Image.open(file_path)

                w, h = im.size

                # (( 6, 0), (1,  -6, 4, -3), (3, 0, 6, 3)
                # d         dst to screen     src from im
                # ((10, 0), (0, -16, 10, 4), ( 0, 0, 10, 20)
                # ((10, 0), (0, -16, 10, 4), (10, 0, 20, 20)
                # ((10, 0), (0, -16, 10, 4), (20, 0, 30, 20)
                #         metrics = [max_w,0, (0, , w , y1)  , (  )

                y = int(h / 5)  # 20 -> 4    11 -> 2

                d = (w, 0)
                dst = (0, y - h, w, y)
                src = (0, 0, w, h)  # individual bitmap not yet mapped to single bitmap

            else:

                im = Image.new("1", (0, 0))

                w, h = im.size

                d = (w, 0)
                dst = (0, 0, w, 0)
                src = (0, 0, w, h)

            self.glyph[i] = d, dst, src, im

        return self

    def get_glyphs_with_height(self, height):

        glyphs_with_height = []

        for i, g in enumerate(self.glyph):

            src = g[2]

            h = src[3] - src[1]

            if h == height:

                glyphs_with_height.append(i)

        return sorted(glyphs_with_height)

    def determine_font_height(self):

        md = self.max_dims()

        h = md[3] - md[1]

        return h

    def save_glyps_as_png_with_offset(self, folder):

        if folder is None:
            folder = self.root_path
        else:
            self.root_path = folder

        os.makedirs(folder, exist_ok=True)

        for i, g in enumerate(self.glyph):

            dst = g[1]
            src = g[2]

            w = src[2] - src[0]
            h = src[3] - src[1]

            h = self.font_height

            #        g[0]      dst = g[1]       src = g[2]
            #   45 - (6, 0) (0, -4, 5, -3) ( 48,  0,  53,  1)    5 wide          10 - 1 = 9
            #   46 . (6, 0) (1, -1, 3,  0) ( 53,  0,  55,  1)    2 wide          10 - 1 = 9
            #  106 j (6, 0) (0, -7, 4,  2) (371,  0, 375,  9)    4 wide offset = 10 - 9 = 1
            #  229 å (6, 0) (0, -9, 6,  0) ( 57, 10,  63, 19)

            im_dst = Image.new("1", (w, h))

            if (w > 0) and (h > 0):

                self.char_count += 1

                full_image = g[3]

                cropped = full_image.crop(src)

                offset = self.font_height - (dst[3] - dst[1])
                offset = max(9 + dst[1], 0)
                # print( i , 9+dst[1])

                im_dst.paste(cropped, (0, offset))

                file_path = os.path.join(folder, "char_" + str(i) + ".png")

                im_dst.save(file_path)

    def save_glyps_as_png(self, folder=None):

        if folder is None:

            folder = self.root_path

        os.makedirs(folder, exist_ok=True)

        for i, g in enumerate(self.glyph):  # index and glyph_list

            src = g[2]

            w = src[2] - src[0]
            h = src[3] - src[1]

            if (w > 0) and (h > 0):

                full_image = g[3]

                cropped = full_image.crop(src)

                file_path = os.path.join(folder, "char_" + str(i) + ".png")

                cropped.save(file_path)

    def save_font_data_as_png(self, filename=None):

        if filename is None:

            filename = self.filename

        self.bitmap.save(
            os.path.splitext(filename)[0] + ".png"
        )  # will also compile so just glyphs need to be okay

    def max_dims(self):

        w_min = 0
        w_max = 0
        h_min = 0
        h_max = 0

        for glyph in self.glyph:
            if glyph:

                dst = glyph[1]

                if dst[0] < w_min:

                    w_min = dst[0]

                if dst[2] > w_max:
                    # print(i,chr(i))
                    w_max = dst[2]

                if dst[1] < h_min:

                    h_min = dst[1]

                if dst[3] > h_max:
                    # print(i,chr(i))
                    h_max = dst[3]

        #        g[0]      dst = g[1]       src = g[2]
        #   45 - (6, 0) (0, -4, 5, -3) ( 48,  0,  53,  1)  w = 5 h = 1     10 - 1 = 9   h
        #   46 . (6, 0) (1, -1, 3,  0) ( 53,  0,  55,  1)  w = 2 h = 1     10 - 1 = 9
        #  106 j (6, 0) (0, -7, 4,  2) (371,  0, 375,  9)  w = 4 h = 9    offset = 10 - 9 = 1
        #  229 å (6, 0) (0, -9, 6,  0) ( 57, 10,  63, 19)  w = 6 h = 9     wide

        return (w_min, h_min, w_max, h_max)

    #     w    -1 0 1 2 3 4 5 6
    #     h -7  . . . . . . . .
    #     h -6  . . . . . . . .
    #     h -5
    #     h -4
    #     h -3
    #     h -2
    #     h -1
    #     h  0
    #     h  1
    #     h  2

    def read_glyphs(self):

        if os.path.isfile(self.root_path + ".png"):

            im = Image.open(self.root_path + ".png")

        if os.path.isfile(self.root_path + ".pbm"):

            im = Image.open(self.root_path + ".pbm")

        with open(self.root_path + ".pil", "rb") as file:

            if file.readline() != b"PILfont\n":
                raise SyntaxError("Not a PILfont file")
            xxx = file.readline().split(b";")

            self.font_height = int(xxx[6].decode("utf-8"))
            confirm(len(xxx), 8)
            confirm(xxx[7], b"\n")
            # print('font_height',self.font_height)

            self.info = []  # FIXME: should be a dictionary
            while True:
                s = file.readline()
                if not s or s == b"DATA\n":
                    break
                self.info.append(s)

            # read PILfont metrics
            data = file.read(256 * 20)

            for i in range(256):

                raw = struct.unpack(">hhhhhhhhhh", data[i * 20 : (i + 1) * 20])

                d = (raw[0], raw[1])
                dst = (raw[2], raw[3], raw[4], raw[5])
                src = (raw[6], raw[7], raw[8], raw[9])

                self.glyph[i] = (d, dst, src, im)

                # c = get_char(i)

                # print(i,c,d,dst,src)

        # im.close() save needs to have an open image

    def compile(self):

        super().compile()

        for i in range(256):
            glyph = self[i]
            if glyph:
                d, dst, src, im = glyph
                xx = src[2] - src[0]
                if xx == 0:
                    self.metrics[i] = d, dst, (0, 0, 0, 0)


#####################################################################
def get_char(i):
    #################################################################

    if i in [132, 133, 155]:

        return ""

    if i in [0, 7, 8, 9, 10, 12, 13, 132, 133]:

        return "."

    return chr(i)


#####################################################################
def confirm(act, exp):
    #################################################################

    if act != exp:

        caller = getframeinfo(stack()[1][0])

        print("%s(%d)" % (caller.filename, caller.lineno))
        print("expected : ", exp)
        print("  actual : ", act)


#####################################################################
if __name__ == "__main__":
    #################################################################

    sys.exit(main())
