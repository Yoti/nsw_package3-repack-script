#!/usr/bin/env python3

import os
import sys


def to_hex(number, align=0):
    number = hex(number)
    number = number[2:]
    number = number.upper()
    number = number.zfill(align)
    return(f'0x{number}')


def bs_int32(src, start, reverse=0):
    ret = src[start:start+4]
    if not reverse:
        return(int.from_bytes(ret, 'little'))
    else:
        return(int.from_bytes(ret, 'big'))


def bs_hex32(src, start, reverse=0):
    ret = bs_int32(src, start, reverse)
    return(to_hex(ret, 8))


def bs_ver32(src, start, reverse=0):
    ret = bs_int32(src, start, reverse)
    ret = hex(ret)[2:]
    ret = str(ret).zfill(8)
    return(f'{int(ret[:2], 16)}.{int(ret[2:4], 16)}.{int(ret[4:6], 16)}.{int(ret[6:8], 16)}')


def main():
    pk31 = None
    print('PK31 Unpacker by Yoti')

    if len(sys.argv) < 2:
        if not os.path.exists('package3'):
            sys.exit('Please provide input file')
        else:
            pk31 = 'package3'
    elif not os.path.exists(sys.argv[1]):
        sys.exit("Input file can't be read")
    else:
        pk31 = sys.argv[1]

    with open(pk31, 'rb') as f:
        package3 = f.read()

    if not len(package3) == 0x800000:
        sys.exit('Input file size is wrong')

    magic = package3[:4]
    if not magic == b'PK31':
        sys.exit('Input file type is wrong')

    print(f'[ {os.path.basename(pk31)} ]')
    print(f'Magic: {magic.decode()}')
    print(f'Metadata offset: {bs_int32(package3, 4)} ({bs_hex32(package3, 4)})')
    print(f'Flags: {bs_int32(package3, 8)}')
    print(f'Meso size: {bs_int32(package3, 12)} ({bs_hex32(package3, 12)})')
    kips_cnt = bs_int32(package3, 16)
    print(f'KIPs count: {kips_cnt}')
    print(f'Legacy magic: {package3[32:36].decode()}')
    print(f'Total size: {bs_int32(package3, 36)} ({bs_hex32(package3, 36)})')
    ch_off = bs_int32(package3, 44)
    print(f'Content header offset: {ch_off} ({bs_hex32(package3, 44)})')
    ch_cnt = bs_int32(package3, 48)
    print(f'Content headers count: {ch_cnt}')
    print(f'Supported HOS version: {bs_hex32(package3, 52)} ({bs_ver32(package3, 52)})')
    print(f'Release version: {bs_hex32(package3, 56)} ({bs_ver32(package3, 56)})')
    print(f'Git revision: {bs_hex32(package3, 60)[2:9].lower()} ({bs_hex32(package3, 60)})')

    basepath = f'{pk31}_out'
    os.makedirs(basepath, exist_ok=True)

    print('Content metas:')
    for i in range(ch_cnt):
        offset = bs_int32(package3, ch_off)
        f_size = bs_int32(package3, ch_off+4)
        f_name = str(package3[ch_off+16:ch_off+16+16].decode())
        f_name = f_name.rstrip("\x00")
        print(f' {f_name.ljust(16)}{to_hex(offset, 6)} -> {to_hex(offset+f_size, 6)} ({f_size})')

        if i < kips_cnt:
            filepath = os.path.join(basepath, f'{f_name}.bin')
        else:
            filepath = os.path.join(basepath, f'{f_name}.kip')
        with open(filepath, 'wb') as of:
            of.write(package3[offset:offset+f_size])

        ch_off += 0x20

    print('KIPs metas:')
    start = 0x400
    for i in range(1+kips_cnt):  # "emummc"+kips_cnt
        program_id = package3[start:start+8].hex()
        file_offset = bs_hex32(package3, start+8)  # add 0x100000 to get real_offset
        file_size = bs_int32(package3, start+12)
        print(f' {program_id}: {file_offset} ({file_size})')
        file_hash = package3[start+16:start+48].hex()
        print(f' {file_hash}')
        start += 0x30


if __name__ == "__main__":
    main()
