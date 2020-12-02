# news data crawling with specified key word
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

import pandas as pd


def get_news(n_url):
    news_detail = []
    # 크롤링 방지 우회
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
    breq = requests.get(n_url, headers=headers)
    bsoup = BeautifulSoup(breq.content, 'html.parser')

    title = bsoup.select('h3#articleTitle')[0].text  # 대괄호는  h3#articleTitle 인 것중 첫번째 그룹만 가져오겠다.
    news_detail.append(title)

    pdate = bsoup.select('.t11')[0].get_text()[:11]
    news_detail.append(pdate)

    _text = bsoup.select('#articleBodyContents')[0].get_text().replace('\n', " ")
    btext = _text.replace("// flash 오류를 우회하기 위한 함수 추가 function _flash_removeCallback() {}", "")
    news_detail.append(btext.strip())

    for divdata in bsoup.findAll('div', {"id": "articleBodyContents"}):
        for getatag in divdata.findAll('span', {'class': 'end_photo_org'}):
            for getimgtag in getatag.findAll('img', src=True):
                news_detail.append(getimgtag['src'])

    return news_detail


def crawler(maxpage, query, s_date, e_date):
    s_from = s_date.replace(".", "")
    e_to = e_date.replace(".", "")
    page = 1
    maxpage_t = (int(maxpage) - 1) * 10 + 1  # 11= 2페이지 21=3페이지 31=4페이지  ...81=9페이지 , 91=10페이지, 101=11페이지
    news_detail = []
    while page < maxpage_t:
        url = "https://search.naver.com/search.naver?where=news&query=" + query + "&sort=0&ds=" + s_date + "&de=" + e_date + "&nso=so%3Ar%2Cp%3Afrom" + s_from + "to" + e_to + "%2Ca%3A&start=" + str(
            page)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
        req = requests.get(url, headers=headers)

        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')
        for a in soup.find_all('a', href=True):
            try:
                if a["href"].startswith("https://news.naver.com"):
                    temp = get_news(a["href"])
                    if (len(temp) == 4):
                        print("crawled Complete")
                        # 조회 뉴스 기사 링크 첨부
                        temp.append(a["href"])
                        news_detail.append(temp)
                        # pdate, pcompany, title, btext
            except Exception as e:
                continue
        page += 10
    return news_detail
