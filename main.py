import telegram
import os
import numpy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
import wordRank
import naverCrawler
from datetime import datetime

from gensim.models import word2vec



def get_bot(token):
    """
    Need to get API ready to use bot. Verify token and send message to bot!

    :param token: API token for telegram bot
    :return: telegram Bot
    """

    # ImportError: cannot import name 'Bot' from 'telegram' (unknown location)
    #   pip unsinstall telegram python-telegram-bot
    #   pip install python-telegram-bot --upgrade

    bot = telegram.Bot(token=token)

    updates = bot.getUpdates()

    # 가장 최근에 온 메세지의 chat id를 가져옵니다
    chat_ids = bot.getUpdates()[-1].message.chat.id
    # 확인 메세지
    # bot.sendMessage(chat_id=chat_id, text="hello user")

    return bot, chat_ids


def check_tmi(uri):
    """
    Detects text in the image file.

    :param uri: url of image
    :return: boolean. Too much information in image
    """
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    from google.cloud.vision import types
    image = types.Image()
    image.source.image_uri = uri

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        return False

    import sys
    try:
        # [rint(texts[0].description)
        # print(len(texts[0].description))
        if len(texts[0].description) > 20:
            return True
        else:
            return False
    except IndexError as e:
        return False


# set stop words
stopword_list = ['수', '일', '있다', '고', '및', '등', '있는', '기자', '년', '것으로', '대한' '이', '통해', '월', '전', '며', '한', '재배포', '것',
                 '위해', '더', '이날', '위한', '네이버',
                 '무단전재', '네이버에서', '대해', '이라고', '함께', 'YTN', '했다', '는', '구독하기', '등을', '구독', '채널', '밝혔다', '무단', '그', '한다',
                 '이번', '또', '연합뉴스',
                 '.', 'com', 'TV', 'SBS', 'KBS', '뉴시스', '뉴스', '1', 'MoneyToday', 'YTN', '세계닷컴', '서울경제', 'Joins',
                 '아시아경제신문', '서울신문', '강원일보', 'edaily',
                 'MBC', '조선일보', '조선비즈', '부산일보', '한경닷컴', '매경닷컴', '스포츠경향', '국민일보', 'MBN', 'financial', 'news',
                 '머니', 'S', '&', 'SBSi', '한국경제', '한국일보', 'donga', '헤럴드경제', '노컷뉴스', 'eTimes', 'internet', 'Co',
                 'OhmyNews', '더팩트', '미디어오늘',
                 '매일신문', '디지털타임스', 'inews', '24', 'media', 'KHAN', 'OSEN', '데일리안', '스포츠서울', 'The', 'Hankyoreh', 'CNBC',
                 '헬스조선', 'JTBC', '여성신문',
                 '스포츠동아', '코메디닷컴', 'Reserved', '동아사이언스', 'ZDNet', '블로터', '디지털데일리', '포모스', '스포츠조선']




# TODO: erase Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/KimJungHwan/Desktop/m-Robo/photobot/test-290712-5c567c6b6d23.json"

# TODO: erase token
token = '1488873575:AAEHBPd8J0duq_mIkUIAECl9N05o3Pht58I'
bot, chat_ids = get_bot(token)

model = word2vec.Word2Vec.load("1minwords")  # 기본 모델
# model = word2vec.Word2Vec.load(" News_Article_Word2Vec") # : 1minwords , 수완님 : News_Article_Word2Vec


# 원하는 기사 유형을 가지고 온다.
# econ_pd = pd.read_csv("New_Article_econ.csv")
# politics_df = pd.read_csv("New_Article_politics.csv")
df = pd.read_csv("New_Article_culture.csv")

for i in range(len(df)):
    start_time = datetime.now()

    title = df['title'][i]
    content = df['contents'][i]

    print("target_title " + title)
    maxpage = 2

    # 크롤링 잘 안된 내용은 버린다
    if (len(df['title'][i]) < 10):
        continue
    if (len(df['contents'][i]) < 400):
        continue
    # 검색 키워드 페이지 크롤링 수
    maxpage = 2

    target_keyword_list = wordRank.get_keywords(title, content)[:4]
    target_keyword = " ".join(target_keyword_list)
    query = target_keyword

    print("target keyword", query)
    s_date = '2000.01.01'
    e_date = '2020.10.11'
    news_list = naverCrawler.crawler(maxpage, query, s_date, e_date)  # 검색된 네이버뉴스의 기사내용을 크롤링합니다.
    # news_list 1 - title 2 - date 3 - text 4 - photo url

    # get keyword
    keyword_list = []
    for news in news_list:
        if (len(news[0]) > 0 and len(news[2]) > 0):
            keyword_list.append(wordRank.get_keywords(news[0], news[2]))

    print("유사 기사의 키워드들 : ")
    for l in keyword_list:
        print(l)

    # get best keyword with cosime similarity ( summation (cosine similarity * 100) <- avg
    point_list = []
    i = 0
    f = 0

    # init 해주어야.. , article_chosen이 아무 뉴스도 못 가져오면
    article_chosen = ['0', '0', '0', '0', '0']
    for keyword in keyword_list:
        point = 0
        for gword in keyword:
            for tword in target_keyword_list:
                try:
                    # 단어에 글자 하나 이상
                    if (len(gword) > 1 and len(tword) > 1):
                        point += model.wv.similarity(gword, tword) * 100
                except KeyError:
                    continue

        if ((len(keyword) * len(target_keyword)) != 0):
            point = point / (len(keyword) * len(target_keyword))
        point_list.append(point)

        print(point)
        if (i < point):
            if (not check_tmi(news_list[f][3])):
                article_chosen = news_list[f]
        f += 1

    print("article chosen: " + article_chosen[0])
    if (not (len(article_chosen[3]) == 1 or len(title) == 0 or len(target_keyword) == 0)):
        bot.sendPhoto(chat_id=chat_ids, photo=article_chosen[3], caption="기사 제목 : " + title)
        bot.sendMessage(chat_id=chat_ids, text="기사 내용: " + content)
        bot.sendMessage(chat_id=chat_ids, text="검색 키워드: " + target_keyword)
        bot.sendMessage(chat_id=chat_ids, text="이미지 출처 기사 제목 : " + article_chosen[0])
        bot.sendMessage(chat_id=chat_ids, text="이미지 출처 : " + article_chosen[4])
