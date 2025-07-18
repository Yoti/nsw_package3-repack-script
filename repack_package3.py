#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def bs_int32(src, start, reverse=0):
    ret = src[start:start+4]
    if not reverse:
        return(int.from_bytes(ret, 'little'))
    else:
        return(int.from_bytes(ret, 'big'))

def main():
    print('PK31 BPatcher v0.1 by Yoti')

    in_files = [os.path.join('atmo', 'package3'), os.path.join('kefir', 'package3')]
    for i in range(len(in_files)):
        if not os.path.exists(in_files[i]):
            os.makedirs('atmo', exist_ok=True)
            os.makedirs('kefir', exist_ok=True)
            sys.exit(f'File {in_files[i]} not found!')

    with open(in_files[0], 'rb') as a:  # 'atmo -> package3'
        a_data = a.read()
        if not len(a_data) == 0x800000:  # размер файла должен строго совпадать
            sys.exit(f'{in_files[0]} is broken')
        a_head = a_data[:4]
        if not a_head == b'PK31':  # проверка на соответствие формата в заголовке
            sys.exit(f'{in_files[0]} is broken')

        a_boot_offset = bs_int32(a_data, 0x1C0)
        a_boot_f_size = bs_int32(a_data, 0x1C4)
        a_boot_offse2 = bs_int32(a_data, 0x4F8)
        a_boot_f_siz2 = bs_int32(a_data, 0x4FC)
        if not a_boot_f_size == a_boot_f_siz2:
            sys.exit(f'{in_files[0]} is broken')
        if not a_boot_offset == a_boot_offse2 + 0x100000:
            sys.exit(f'{in_files[0]} is broken')

        a_boot_f_data = a_data[a_boot_offset:a_boot_offset+a_boot_f_size]
        a_boot_sha256 = a_data[0x500:0x520]

    with open(in_files[1], 'rb') as k:  # 'kefir -> package3'
        k_data = bytearray(k.read())
        if not len(k_data) == 0x800000:  # размер файла должен строго совпадать
            sys.exit(f'{in_files[1]} is broken')
        k_head = k_data[:4]
        if not k_head == b'PK31':  # проверка на соответствие формата в заголовке
            sys.exit(f'{in_files[1]} is broken')

        k_boot_offset = bs_int32(k_data, 0x1C0)
        k_boot_f_size = bs_int32(k_data, 0x1C4)
        k_boot_offse2 = bs_int32(k_data, 0x4F8)
        k_boot_f_siz2 = bs_int32(k_data, 0x4FC)
        if not k_boot_f_size == k_boot_f_siz2:
            sys.exit(f'{in_files[1]} is broken')
        if not k_boot_offset == k_boot_offse2 + 0x100000:
            sys.exit(f'{in_files[1]} is broken')

    if not a_boot_f_size > k_boot_f_size:
        k_data[0x1C4:0x1C8] = a_data[0x1C4:0x1C8]  # записываем новый размер файла
        k_data[0x4FC:0x500] = a_data[0x4FC:0x500]  # записываем новый размер файла
        k_data[0x500:0x520] = a_data[0x500:0x520]  # записываем новую сумму sha256

        # очищаем место под файл байтом-заполнителем (выравниватель)
        k_data[k_boot_offset:k_boot_offset+k_boot_f_size] = b'\xCC' * k_boot_f_size
        # записываем данные нового файла по старому адресу
        k_data[k_boot_offset:k_boot_offset+a_boot_f_size] = a_data[a_boot_offset:a_boot_offset+a_boot_f_size]

        with open('package3', 'wb') as p:
            p.write(k_data)
        print('Done: file saved as package3')
    else:
        print('Error: not enough free space')

if __name__ == "__main__":
    main()
