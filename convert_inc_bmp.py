#!/usr/bin/env python3

import os
import sys
import requests
from PIL import Image

def rehex(number):
    # если длина входящего числа не кратна двум, то добавить ноль
    # преобразовать число в цикле парами
    return(number[6:8] + number[4:6] + number[2:4] + number[0:2])

def tohex(number, align=0, reverse=False):
    number = int(number)
    number = hex(number)
    number = number[2:].upper()
    number = number.zfill(align)
    if reverse and len(number) == 8:
        number = rehex(number)
    return number

def bmp32b(path, data, w=1, h=1):
    w_hdr = tohex(w, 8, True)
    h_hdr = tohex(h, 8, True)
    with open(path, 'wb') as outf:
        # заголовок для 32 битного bmp
        head32b = bytearray.fromhex('424D38403800000000003600000028000000'+w_hdr+h_hdr+'010020000000000002403800120B0000120B00000000000000000000')
        outf.write(head32b)

        outdata = bytearray()

        temp = bytearray.fromhex(data)
        for i in range(len(temp), 0, -4):  # картинка перевёрнута по горизонтали
            temp32b = bytearray(4)
            temp32b[0] = temp[i-1]
            temp32b[1] = temp[i-2]
            temp32b[2] = temp[i-3]
            temp32b[3] = temp[i-4]
            outdata += temp32b

        outf.write(outdata)

        # временный костыль для отражения изображения по горизонтали
        with Image.open(path) as r:
            ret = r.transpose(Image.FLIP_LEFT_RIGHT)
            ret.save(path)

def main():
    if len(sys.argv) < 2:
        print('missing input file; blank file under black.inc name was made')

        with open('black.inc', 'wt') as outf:
            w = 1280
            h = 720
            head = f'constexpr size_t SplashScreenX = 0;\nconstexpr size_t SplashScreenY = 0;\nconstexpr size_t SplashScreenW = {w};\nconstexpr size_t SplashScreenH = {h};\n\nconstexpr u32 SplashScreen[] = {{'
            outf.write(head)
            data = '0xFF000000, ' * (int((w * h) / 4) - 1)
            data += '0xFF000000'
            outf.write(data)
            foot = '};\n\nstatic_assert(sizeof(SplashScreen) == sizeof(u32) * SplashScreenW * SplashScreenH, "Incorrect SplashScreen definition!");'
            outf.write(foot)
    else:
        print(f'Input file name is {sys.argv[1]}')

        with open(sys.argv[1], 'rt') as inf:
            inf_text = inf.read()

            img_w_start_txt = 'constexpr size_t SplashScreenW = '
            img_w_start_pos = inf_text.index(img_w_start_txt) + len(img_w_start_txt)
            img_w = inf_text[img_w_start_pos:img_w_start_pos+4].replace(';', '')
            print('Image width size is', img_w)

            img_h_start_txt = 'constexpr size_t SplashScreenH = '
            img_h_start_pos = inf_text.index(img_h_start_txt) + len(img_h_start_txt)
            img_h = inf_text[img_h_start_pos:img_h_start_pos+4].replace(';', '')
            print('Image height size is', img_h)

            inf_text = inf_text[inf_text.index('{')+1:inf_text.index('}')]
            inf_text = inf_text.replace('0x', '')
            inf_text = inf_text.replace(', ', '')
            '''
            with open(os.path.splitext(sys.argv[1])[0]+'.raw', 'wb') as outf:
                data = bytearray.fromhex(inf_text)
                for i in range(0, len(data), 4):
                    temp = data[i:i+4]
                    data[i+0] = temp[1]
                    data[i+1] = temp[2]
                    data[i+2] = temp[3]
                    data[i+3] = temp[0]  # прозрачность последним каналом
                outf.write(data)
            '''
            bmp32b(os.path.splitext(sys.argv[1])[0]+'.bmp', inf_text, img_w, img_h)

if __name__ == "__main__":
    main()
