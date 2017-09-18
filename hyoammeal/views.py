# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json, time, datetime
from datetime import date

import logging
logger = logging.getLogger(__name__)

# GET ~/keyboard/ 요청에 반응
def keyboard(request):
    return JsonResponse({
        'type': 'buttons',
        'buttons': ['오늘 식단표', '내일 식단표', '다른 요일 식단표']
    })

# csrf 토큰 에러 방지, POST 요청에 message response
@csrf_exempt
def message(request):
    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    meal = received_json_data['content']

    daystring = ["월", "화", "수", "목", "금", "토", "일"]
    today = datetime.datetime.today().weekday()

    nextdaystring = ["화", "수", "목", "금", "토", "일", "월"]

    today_date = datetime.date.today().strftime("%m월 %d일 ")
    tomorrow_date = date.fromtimestamp(time.time() + 60 * 60 * 24).strftime("%m월 %d일 ")

    if meal == '오늘 식단표':
        return JsonResponse({
            'message': {
                'text': '[' + meal + '] \n' + today_date + daystring[today] + '요일 식단표입니다. \n \n' + read_txt(request)
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['오늘 식단표', '내일 식단표', '다른 요일 식단표']
            }
        })
    elif meal == '내일 식단표':
        return JsonResponse({
            'message': {
                'text': '[' + meal + '] \n' + tomorrow_date + nextdaystring[today] + '요일 식단표입니다. \n \n' + read_txt(request)
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['오늘 식단표', '내일 식단표', '다른 요일 식단표']
            }
        })
    elif meal == '다른 요일 식단표':
        return JsonResponse({
            'message': {
                'text': '식단 정보가 필요한 요일을 입력해주세요\n입력 가능 요일 : 월 화 수 목 금 토'
            },
            'keyboard': {
                'type': 'text'
            }
        })
    elif meal == '월' or meal == '화' or meal == '수' or meal == '목' or meal == '금' or meal == '토':
        return JsonResponse({
            'message': {
                'text': meal + '요일 식단표입니다. \n \n' + read_txt(request)
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['오늘 식단표', '내일 식단표', '다른 요일 식단표']
            }
        })
    else:
        return JsonResponse({
            'message': {
                'text': '잘못된 명령어입니다.\n입력 가능 명령어 : 월 화 수 목 금 토'
            },
            'keyboard': {
                'type': 'text'
            }
        })

def read_txt(request):
    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    meal = received_json_data['content']

    # 요일 import, 월요일 ~ 일요일 = 0~6
    today = datetime.datetime.today().weekday()

    # 0(월요일) ~ 6(일요일).txt read
    if meal == '오늘 식단표':
        if today == 6:
            menu = '일요일은 급식이 제공되지 않습니다.'
        else:
            f = open(str(today) + ".txt", 'r')
            menu = f.read()
            f.close()

    if meal == '내일 식단표':
        if today == 5:
            menu = '일요일은 급식이 제공되지 않습니다.'
        elif today == 6:
            f = open("0.txt", 'r')
            menu = f.read()
            f.close()
        else:
            today = today + 1
            f = open(str(today) + ".txt", 'r')
            menu = f.read()
            f.close()

    if meal == '월':
        f = open("0.txt", 'r')
        menu = f.read()
        f.close()

    if meal == '화':
        f = open("1.txt", 'r')
        menu = f.read()
        f.close()

    if meal == '수':
        f = open("2.txt", 'r')
        menu = f.read()
        f.close()

    if meal == '목':
        f = open("3.txt", 'r')
        menu = f.read()
        f.close()

    if meal == '금':
        f = open("4.txt", 'r')
        menu = f.read()
        f.close()

    if meal == '토':
        f = open("5.txt", 'r')
        menu = f.read()
        f.close()

    return menu

# message 요청 받을시 크롤링 실시
def crawl(request):
    import urllib.request
    from bs4 import BeautifulSoup

    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    meal = received_json_data['content']

    # 타학교에서 이용시 수정
    regioncode = 'gne.go.kr'
    schulcode = 'S100000747'

    # NEIS에서 파싱
    url = ('http://stu.' + regioncode + '/sts_sci_md01_001.do?schulCode=' + schulcode + '&schulCrseScCode=4&schulKndScCode=04&schMmealScCode=1')

    try:
        source = urllib.request.urlopen(url, timeout=3)
    except Exception as e:
        logger.error(e)
        menu = '급식 정보를 가져오는 중 문제가 발생하였습니다.\n관리자에게 연락바랍니다.'
    else:
        # beautifulsoup4를 이용해 utf-8, lxml으로 파싱
        soup = BeautifulSoup(source, "lxml", from_encoding='utf-8')

        # div_id="contents"안의 table을 모두 검색 후 td태그만 추출
        table_div = soup.find(id="contents")
        tables = table_div.find_all("table")
        menu_table = tables[0]
        td = menu_table.find_all('td')

        # 요일 import, 월요일 ~ 일요일 = 0~6
        today = datetime.datetime.today().weekday()

        # 월요일 ~ 일요일 = td[8] ~ td[14]
        if meal == '오늘 식단표':
            if today == 6:
                menu = '일요일'
            else:
                menu = td[today + 8]

        if meal == '내일 식단표':
            if today == 5:
                menu = '일요일'
            elif today == 6:
                menu = td[8]
            else:
                menu = td[today + 9]

        # 파싱 후 불필요한 태그 잔해물 제거
        menu = str(menu).replace('*', '').replace('<td', '').replace('<br/></td>', '').replace('</td>', '').replace('class="textC last">', '').replace('class="textC">', '').replace('<br/>', '\n').replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '').replace('6.', '').replace('7.', '').replace('8.', '').replace('9.', '').replace('10.', '').replace('11.', '').replace('12.', '').replace('13.', '').replace('14.', '').replace('15.', '').replace('1', '').replace(' ', '')

        if menu == '':
            menu = '급식 정보가 존재하지 않습니다.\n급식이 없는 날일 수 있으니 확인 바랍니다.'

        if menu == '일요일':
            menu = '일요일은 급식이 제공되지 않습니다.'

    return menu