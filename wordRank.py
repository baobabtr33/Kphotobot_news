from krwordrank.hangle import normalize
from krwordrank.word import KRWordRank
from konlpy.tag import Komoran
from konlpy.tag import Mecab


def get_keywords(title, text):
    """

    :param title: title of article
    :param text: body of article
    :return: key_words
    """
    texts = text
    texts = [texts]
    texts = [normalize(text, english=True, number=True) for text in texts]

    wordrank_extractor = KRWordRank(
        min_count=2,  # 단어의 최소 출현 빈도수 (그래프 생성 시)
        max_length=10,  # 단어의 최대 길이
        verbose=True
    )

    beta = 0.85  # PageRank의 decaying factor beta
    max_iter = 10

    keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter)

    # rank 이용 분류
    tagger = Komoran()
    stopword = set([('있', 'VV'), ('하', 'VV'), ('되', 'VV')])
    keyword_list = []
    for i in keywords:
        noun = tagger.nouns(i)
        if noun != []:
            keyword_list.append([noun[0], keywords[i]])

    keywords = []
    for i in keyword_list[:5]:
        keywords.append(i[0])

    title_keywords = []

    for j in keywords:
        if j in title:
            title_keywords.append(j)

    for i in title_keywords:
        if i in stopword_list:
            title_keywords.remove(i)

    return title_keywords


def get_nouns(text):
    tagger = Mecab()
    keyword_list = []
    noun = tagger.nouns(text)
    noun = [i for i in noun if len(i) > 1]
    noun = str(noun).replace('[', '').replace(']', '').replace(',', ' ').replace("'", '')

    return noun


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
