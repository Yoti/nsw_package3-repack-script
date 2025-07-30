#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import sys
import shutil
import requests
from zipfile import ZipFile

def bs_int32(src, start, reverse=0):
    ret = src[start:start+4]
    if not reverse:
        return(int.from_bytes(ret, 'little'))
    else:
        return(int.from_bytes(ret, 'big'))

def bs_ver32(src, start, reverse=0):
    ret = bs_int32(src, start, reverse)
    ret = hex(ret)[2:]
    ret = str(ret).zfill(8)
    return(f'{int(ret[:2], 16)}.{int(ret[2:4], 16)}.{int(ret[4:6], 16)}.{int(ret[6:8], 16)}')

def getGitHubDirectLink(baseLink, redirLink, baseDir):
    redirLink = redirLink.replace('/tag/', '/expanded_assets/')
    try:
        response = requests.get(redirLink, timeout=10)
    except:
        pass
    else:
        if response.status_code == 200:
            pageText = response.text
            try:
                # в тексте фрэйма нет текста github.com
                redirLink = redirLink.replace('https://github.com', '')
                # ссылка на файл отличается от ссылки на фрэйм
                redirLink = redirLink.replace('/expanded_assets/', '/download/')
                # для точности поиска добавляем начало имени файла
                redirLink = f'{redirLink}/{baseDir}'
                # ищем позицию начала подстроки ссылки и куска имени файла
                retLinkStart = pageText.index(redirLink)
                # отрезаем из текста страницы всё до этого
                pageText = pageText[retLinkStart:]
                # ищем в обрезанном тексте страницы конец строки по расширению
                retLinkFinish = pageText.index('.zip') + len('.zip')
                # вот наша итоговая ссылка без домена (текста github.com)
                pageText = pageText[:retLinkFinish]
                # собираем прямую ссылку из домена и конечного имени файла
                return(f'https://github.com{pageText}')
            except:
                pass
        else:
            pass

    return(None)

def sys_exit(msg):
    if sys.argv[0].endswith('.exe'):
        print(msg)
        input('Press Enter to continue...')
        sys.exit()
    else:
        sys.exit(msg)

def catchGitHubRedirect(baseLink):
    latestLink = f'{baseLink}/releases/latest'
    try:
        response = requests.get(latestLink, timeout=10, allow_redirects=False)
        if response.status_code == 302:
            return response.headers['location']
        else:
            return(None)
    except:
        return(None)

def unpackZip(inData, outPath):
    if os.path.exists(outPath):
        shutil.rmtree(outPath)
    os.makedirs(outPath, exist_ok=True)
    with ZipFile(io.BytesIO(inData)) as z:
        z.extractall(os.path.join(os.getcwd(), outPath))

def downloadAndUnpack(link):
    # откусываем первые три буквы из имени репозитория
    baseDir = os.path.basename(link)[:3].lower()

    # получаем ссылку на релиз из ссылки на репозиторий
    latest = catchGitHubRedirect(link)
    # получаем прямую ссылку на файл из ссылки на релиз
    direct = getGitHubDirectLink(link, latest, baseDir)
    # просто имя архива для последующего использования
    zipName = os.path.basename(direct)
    print(f'Load: {zipName}')

    try:
        response = requests.get(direct, timeout=10)
        if response.status_code == 200:
            unpackZip(response.content, baseDir)
        else:
            sys_exit("Error: can't download file!")
    except:
        pass
    return os.path.splitext(zipName)[0]

def main():
    print('PK31 BPatcher v0.4 by Yoti')

    # пути до файлов с учётом заявленных в ранних версиях программы
    in_files = [os.path.join('atmo', 'package3'), os.path.join('kefir', 'package3')]
    # файлы не найдены, применяем фишку по загрузке их из сети Интернет
    if not os.path.exists(in_files[0]):
        downloadAndUnpack('https://github.com/Atmosphere-NX/Atmosphere')
        in_files[0] = os.path.join('atm', 'atmosphere', 'package3')
    if not os.path.exists(in_files[1]):
        zipName = downloadAndUnpack('https://github.com/rashevskyv/kefir')
        in_files[1] = os.path.join('kef', 'atmosphere', 'package3')
    # проверяем ещё раз, на всякий, что все нужные файлы есть на месте
    for in_file in in_files:
        if not os.path.exists(in_file):
            sys_exit(f'Error: {in_file} is missing')

    with open(in_files[0], 'rb') as a:  # Atmosphere
        a_data = a.read()
        if not len(a_data) == 0x800000:  # размер файла должен строго совпадать
            sys_exit(f'Error: {in_files[0]} is broken')
        a_head = a_data[:4]
        if not a_head == b'PK31':  # проверка на соответствие формата в заголовке
            sys_exit(f'Error: {in_files[0]} is broken')

        # статичное значение смещения взято из упаковщика
        a_atmo_vernum = a_data[0x38:0x3C]
        # смещения взяты из рассчёта, что boot упакован 3 с конца
        a_boot_offset = bs_int32(a_data, 0x1C0)
        a_boot_f_size = bs_int32(a_data, 0x1C4)
        a_boot_offse2 = bs_int32(a_data, 0x4F8)
        a_boot_f_siz2 = bs_int32(a_data, 0x4FC)
        # необязательные проверки для дополнительной перестраховки
        if not a_boot_f_size == a_boot_f_siz2:
            sys_exit(f'Error: {in_files[0]} is broken')
        if not a_boot_offset == a_boot_offse2 + 0x100000:
            sys_exit(f'Error: {in_files[0]} is broken')

    with open(in_files[1], 'rb') as k:  # Kefir
        k_data = bytearray(k.read())
        if not len(k_data) == 0x800000:  # размер файла должен строго совпадать
            sys_exit(f'Error: {in_files[1]} is broken')
        k_head = k_data[:4]
        if not k_head == b'PK31':  # проверка на соответствие формата в заголовке
            sys_exit(f'Error: {in_files[1]} is broken')

        # статичное значение смещения взято из упаковщика
        k_atmo_vernum = k_data[0x38:0x3C]
        # смещения взяты из рассчёта, что boot упакован 3 с конца
        k_boot_offset = bs_int32(k_data, 0x1C0)
        k_boot_f_size = bs_int32(k_data, 0x1C4)
        k_boot_offse2 = bs_int32(k_data, 0x4F8)
        k_boot_f_siz2 = bs_int32(k_data, 0x4FC)
        # необязательные проверки для дополнительной перестраховки
        if not k_boot_f_size == k_boot_f_siz2:
            sys_exit(f'Error: {in_files[1]} is broken')
        if not k_boot_offset == k_boot_offse2 + 0x100000:
            sys_exit(f'Error: {in_files[1]} is broken')

    # неизвестно что будет, если версия Атмосферы не совпадёт
    if not a_atmo_vernum == k_atmo_vernum:
        sys_exit(f'Error: incompatible versions ({bs_ver32(a_data, 0x38)} vs {bs_ver32(k_data, 0x38)})')

    # новый файл должен быть меньше или равен старому, чтобы влезть
    if not a_boot_f_size > k_boot_f_size:
        k_data[0x1C4:0x1C8] = a_data[0x1C4:0x1C8]  # записываем новый размер файла
        k_data[0x4FC:0x500] = a_data[0x4FC:0x500]  # записываем новый размер файла
        k_data[0x500:0x520] = a_data[0x500:0x520]  # записываем новую сумму sha256

        # очищаем место под файл байтом-заполнителем (выравниватель)
        k_data[k_boot_offset:k_boot_offset+k_boot_f_size] = b'\xCC' * k_boot_f_size
        # записываем данные нового файла по старому адресу
        k_data[k_boot_offset:k_boot_offset+a_boot_f_size] = a_data[a_boot_offset:a_boot_offset+a_boot_f_size]

        # сохраняем изменённый файл на диск...
        if os.path.exists(in_files[1]):  # присутствует папка "kef"
            # ...как package3 внутри сборки Kefir
            if os.path.exists(in_files[1]):
                os.remove(in_files[1])
                with open(in_files[1], 'wb') as p:
                    p.write(k_data)

                # а также делаем архив с исправленным Kefir
                print(f'Done: output archive is {zipName}-fix.zip')
                shutil.make_archive(f'{zipName}-fix', 'zip', 'kef')

                sys_exit(f'Done: file saved as {in_files[1]}')
        else:
            # ...как package3 рядом со скриптом
            with open('package3', 'wb') as p:
                p.write(k_data)
            sys_exit('Done: file saved as package3')

    else:
        sys_exit('Error: not enough free space')

if __name__ == "__main__":
    main()
