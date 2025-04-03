import requests
from bs4 import BeautifulSoup
import re
import time
from threading import Thread, Lock

def parameters(pro_='', pro_1='', pro_2='', year=''):
    """参数生成"""
    return [pro_, pro_1, pro_2, year]

def threadingUp(count, infoList, pages, url):
    """启动多线程"""
    threads = []
    for _ in range(count):
        t = Thread(target=getDataInfo, args=(infoList, pages, url))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

def getHTMLText(url):
    """获取网页内容"""
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ''

def getPages(url, pre_params, *args):
    """获取分页信息"""
    params = []
    count = -1
    for i in args:
        count += 1
        par_ = pre_params[count] + i
        params.append(par_)

    for param in params:
        url += param + '&'

    html = getHTMLText(url)
    soup = BeautifulSoup(html, 'html.parser')

    try:
        pages_tag = soup.find_all('td', 'header')[1].string
        pages = int(re.split('/', pages_tag)[1])
    except:
        pages = 0

    return pages if pages != 0 else 1, url

page = 0
lock = Lock()

def getDataInfo(infoList, pages, url):
    """多线程获取调剂信息"""
    global page
    while True:
        with lock:
            page += 1
            current_page = page
        if current_page > pages:
            break

        page_url = url + '&page=' + str(current_page)
        time.sleep(1)
        html = getHTMLText(page_url)
        if not html:
            continue

        soup = BeautifulSoup(html, 'html.parser')
        tbody = soup.find_all('tbody', 'forum_body_manage')
        if not tbody:
            continue

        for tr in tbody[0].find_all('tr'):
            try:
                dicts = {
                    0: tr.find_all('a')[0].string.strip(),        # 标题
                    1: tr.find_all('td')[1].string.strip(),       # 学校
                    2: tr.find_all('td')[2].string.strip(),       # 门类/专业
                    3: tr.find_all('td')[3].string.strip(),       # 招生人数
                    4: tr.find_all('td')[4].string.strip(),       # 发布时间
                    'href': tr.find_all('a')[0].get('href', '')   # 链接
                }
                infoList.append(dicts)
            except Exception as e:
                pass
                # print(f"Error parsing muchong data: {e}")
        # print(infoList)