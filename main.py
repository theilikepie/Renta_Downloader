﻿# Download renta manga, version 2019-10-31, program tested, XU Zhengyi
import gzip
import math
import os
import re
from io import BytesIO

import PIL.Image as image
from threadpool import ThreadPool, makeRequests

from getHtml import GetHtml

header = {}
# ********SETTINGS********
# Your cookie here, notice that one cookie for one manga
header['Cookie'] = "rbc=1002; _gcl_au=1.1.1934190885.1609633164; _atrk_siteuid=WTvLOMDSyC03L8ag; bCode=0; appier_utmz=%7B%22csr%22%3A%22google%22%2C%22timestamp%22%3A1609633164%2C%22lcsr%22%3A%22google%22%7D; _atrk_xuid=85b5bd5c932995901dd8c64faae863e1cfd3e8d31743c30f4b0b778970d78bea; cart_cnt=1609633178-0; uc_wh=renta_rent:sort=d%2Ctype=desc%2Cdisp_series=0|; RFP=91321%2C; recent=hq; rct=1; allow_adlt=1; adlt_code=1; adlt_disp=1; _atrk_ssid=jqV8zDqDzmCLkZPEqykpgB; _gid=GA1.2.1207169619.1609731751; _fbp=fb.2.1609731751103.1332253482; renta_ser=0; pay=0; renta_period=0; time_measure=bookshelf-1609731763-9-341481-4461198; mds=2021010412421f219f09f5ba10787f%2A4461198%2A4461198%2A99991231%2A1609731763-a19943d894a03b8e99; USC1=aJDFYAQuyMr1RCxuzfRwd9NH4461198; _gat_UA-25029787-1=1; uriagePage=https://www.ebookrenta.com/renta/sc/frm/rent/; _ga_DRN8R411KY=GS1.1.1609731751.2.1.1609732520.0; _ga=GA1.2.66792337.1609633164; _atrk_sessidx=12; hq=8; _uetsid=df9291504e3e11ebb352f1892b8c7d7f; _uetvid=55195e404d5911eb9b754735e61838ad"
# URL of the manga
url = 'http://us-dre4.ebookrenta.com/sc/view_jsimg2_en/a19943d894a03b8e99/9-341481-84/rbc1002/index.view'
# Where to put download manga
imgdir = "C:\Users\shazi\OneDrive\Desktop\aaaaaaa"

# Threadpool size, how many thread to use for download then images
poolsize = 5
# Max retry, no need to change
max_loop = 20
# ********SETTINGS********


if not os.path.isdir(imgdir):
    os.mkdir(imgdir)


def f_shuffle_r(ar_number, snum, x_idx, y):
    gn = kn = int(y / 2)
    if(y % 2 != 0):
        gn += 1
        kn += 1
    ar_g = [-1 for i in range(gn)]
    ar_k = [-1 for i in range(kn)]
    g_cnt = k_cnt = 0

    ar_tmp = [-1 for i in range(y)]
    cnt = 0
    if(snum % 2 == 0):
        for i in range(y):
            if (i % 2 == 0):
                ar_g[g_cnt] = ar_number[i][x_idx]
                g_cnt += 1
            else:
                ar_k[k_cnt] = ar_number[i][x_idx]
                k_cnt += 1
        for i in range(gn):
            if(ar_k[i] != -1):
                ar_tmp[cnt] = ar_k[i]
                cnt += 1
            if(ar_g[i] != -1):
                ar_tmp[cnt] = ar_g[i]
                cnt += 1
    else:
        for i in range(y):
            if(i < gn):
                ar_g[g_cnt] = ar_number[i][x_idx]
                g_cnt += 1
            else:
                ar_k[k_cnt] = ar_number[i][x_idx]
                k_cnt += 1
        for i in range(gn):
            if(ar_g[i] != -1):
                ar_tmp[cnt] = ar_g[i]
                cnt += 1
            if(ar_k[i] != -1):
                ar_tmp[cnt] = ar_k[i]
                cnt += 1

    for i in range(y):
        ar_number[i][x_idx] = ar_tmp[i]

    del ar_tmp
    del ar_g
    del ar_k
    return ar_number


header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
header['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
header['Accept-Encoding'] = 'gzip'
header['Referer'] = url
header['Origin'] = 'https://dre-viewer.papy.co.jp'
header['DNT'] = '1'
header['Sec-Fetch-Mode'] = 'cors'
header['Sec-Fetch-Site'] = 'same-site'
header['Connection'] = 'keep-alive'
header['Upgrade-Insecure-Requests'] = '1'
header['Accept-Language'] = 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'


def start_download(url):
    download_info = get_download_info(url)
    print(download_info)
    download_images(**download_info)


def get_download_info(url):
    is_us = True if url.find('us-dre') != -1 else False
    re_max_page = re.compile(r'var max_page = ([0-9]+?);')
    if is_us:
        re_base_url = re.compile(r'var url_base = \"(.+?)\"')
        manga_base_url = url.split('.com')[0]
    else:
        re_base_url = re.compile(r'var url_base2 = \"(.+?)\"')
        manga_base_url = ''

    re_cache_update = re.compile(r'var cache_update = \"([0-9]+?)\";')
    re_prd_ser = re.compile(r'var prd_ser = "([0-9]+?)";')
    re_auth_key = re.compile(r'var auth_key = "(.+?)";')

    getter = GetHtml()
    getter.set(url, header=header, retryTimes=5)
    org_data = getter.get()
    try:
        data = gzip.decompress(org_data)
    except:
        data = org_data

    try:
        data = org_data.decode('utf-8')
    except:
        try:
            data = org_data.decode('EUC-JP')
        except:
            raise Exception('Unknow encoding.')

    try:
        prd_ser = int(re_prd_ser.findall(data)[0])
    except:
        raise Exception('Can not find prd_ser on the page')

    try:
        base_url = re_base_url.findall(data)[0] + "%d"
    except:
        raise Exception('Can not find base_url on the page')

    try:
        cache_update = re_cache_update.findall(data)[0]
        if cache_update == '0':
            cache_update = None
    except:
        cache_update = None

    if not is_us:
        try:
            auth_key_papy = re_auth_key.findall(data)[0]
        except:
            raise Exception('Can not find auth_key_papy on the page')
    else:
        auth_key_papy = ''

    try:
        sum_page = int(re_max_page.findall(data)[0])
    except:
        raise Exception('Can not find sum_page on the page')

    return {
        'prd_ser': prd_ser,
        'base_url': base_url,
        'cache_update': cache_update,
        'auth_key_papy': auth_key_papy,
        'sum_page': sum_page,
        'is_us': is_us,
        'manga_base_url': manga_base_url
    }


def download_images(prd_ser, base_url, cache_update, auth_key_papy, sum_page, is_us, manga_base_url):
    pool = ThreadPool(poolsize)
    args_list = []
    for page in range(1, sum_page + 1):

        if is_us:
            url = manga_base_url + '.com'
            url += base_url % page + "?"
            url += 'type=6'
        else:
            url = base_url % page + "?"
            if cache_update:
                url += "date=" + cache_update + '&'
            url += auth_key_papy + "&origin=s_dre-viewer.papy.co.jp"
        args_list.append(((url, page, prd_ser), None))

    requests = makeRequests(download_one_page, args_list)
    [pool.putRequest(i) for i in requests]
    pool.wait()


def download_one_page(url, page, prd_ser):
    x = 7
    y = 7
    getter = GetHtml()
    getter.set(url, header=header, retryTimes=5)
    org_data = getter.get()
    try:
        data = bytearray(gzip.decompress(org_data))
    except:
        data = bytearray(org_data)

    head_length = int(data[:9])

    s_data = str(data[9:9 + head_length].decode("ascii")).split("|")
    img_data = data[head_length + 9:]

    width = int(s_data[0])
    height = int(s_data[1])

    diff_w_idx = s_data[2]
    diff_h_idx = s_data[3]

    s_data = s_data[4:]

    after_width = int(width / x)
    after_height = int(height / y)
    diff_w = (width % x)
    diff_h = (height % y)

    FinalImage = image.new('RGB', (width, height))
    if(diff_w != 0 or diff_h != 0):
        if(diff_w != 0 and diff_h == 0):
            location, length = diff_w_idx.split(',')
            src_img = img_data[int(location):int(location) + int(length)]
            file_data = BytesIO(src_img)
            og_img = image.open(file_data)
            FinalImage.paste(og_img, (0, 0))
        elif(diff_w == 0 and diff_h != 0):
            location, length = diff_h_idx.split(',')
            src_img = img_data[int(location):int(location) + int(length)]
            file_data = BytesIO(src_img)
            og_img = image.open(file_data)
            FinalImage.paste(og_img, (0, 0))
        else:
            location, length = diff_w_idx.split(',')
            src_img = img_data[int(location):int(location) + int(length)]
            file_data = BytesIO(src_img)
            og_img = image.open(file_data)
            FinalImage.paste(og_img, (0, 0))

            location, length = diff_h_idx.split(',')
            src_img = img_data[int(location):int(location) + int(length)]
            file_data = BytesIO(src_img)
            og_img = image.open(file_data)
            FinalImage.paste(og_img, (0, 0))

    ar_number = [[i * x + j for j in range(y)] for i in range(x)]
    for i in range(y):
        ar_tmp = [0 for i in range(x)]
        st = x - i % x
        for j in range(x):
            if(st >= x):
                st = 0
            ar_tmp[j] = ar_number[i][st]
            st += 1
        for j in range(x):
            ar_number[i][j] = ar_tmp[j]

    for i in range(x):
        ar_tmp = [0 for i in range(y)]
        st = y - i % y
        for j in range(y):
            if(st >= y):
                st = 0
            ar_tmp[j] = ar_number[st][i]
            st += 1
        for j in range(y):
            ar_number[j][i] = ar_tmp[j]

    for i in range(x):
        num = i + 1
        seed = page + prd_ser
        if (seed % max_loop == 0):
            seed = math.fabs(page - prd_ser) + (max_loop + 1)
        k = int(((num * seed) + (page / max_loop)) % max_loop)
        for j in range(k - 1, -1, -1):
            ar_number = f_shuffle_r(ar_number, j, i, y)

    total = x * y
    ar_didx = [0 for i in range(total)]
    for i in range(y):
        for j in range(x):
            d_stx = diff_w + (j * after_width)
            d_sty = diff_h + (i * after_height)
            number = ar_number[i][j]
            ar_didx[number] = (d_stx, d_sty)

    img_arr = []
    for i in s_data:
        location, length = i.split(',')
        img_arr.append(img_data[int(location):int(location) + int(length)])

    for i in range(total):
        x, y = ar_didx[i]
        file_data = BytesIO(img_arr[i])
        og_img = image.open(file_data)
        FinalImage.paste(og_img, (x, y))
    with open(imgdir + '/%03d.jpg' % page, "wb") as f:
        FinalImage.save(f)
        print('Saved page %d' % page)


if __name__ == '__main__':
    start_download(url)
