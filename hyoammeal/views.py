# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json, time, datetime
from datetime import date

# GET ~/keyboard/ 요청에 반응
def keyboard(request):
    return JsonResponse({
        'type': 'buttons',
        'buttons': ['조식', '중식', '석식', '내일의 조식', '내일의 중식', '내일의 석식']
    })

# csrf 토큰 에러 방지, POST 요청에 반응
@csrf_exempt
def message(request):
    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    meal = received_json_data['content']

    dayString = ["월", "화", "수", "목", "금", "토", "일"]
    today = datetime.datetime.today().weekday()

    nextdayString = ["화", "수", "목", "금", "토", "일", "월"]
    tomorrow = datetime.datetime.today().weekday()

    today_date = datetime.date.today().strftime("%m월 %d일 ")
    tomorrow_date = date.fromtimestamp(time.time() + 60*60*24).strftime("%m월 %d일 ")

    if meal == '조식' or meal == '중식' or meal == '석식':
        return JsonResponse({
            'message': {
                'text': today_date + str(dayString[today]) + '요일 ' + meal + ' 메뉴입니다. \n \n' + str(crawl(request))
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['조식', '중식', '석식', '내일의 조식', '내일의 중식', '내일의 석식']
            }
     })
    if meal == '내일의 조식' or meal == '내일의 중식' or meal == '내일의 석식':
        return JsonResponse({
            'message': {
                'text': '['+ meal '] \n' + tomorrow_date + str(nextdayString[tomorrow]) + '요일 급식 메뉴입니다. \n \n' + str(crawl(request))
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['내일의 조식', '내일의 중식', '내일의 석식', '조식', '중식', '석식']
            }
     })


# message 요청 받을시 크롤링 실시
def crawl(request):
    from bs4 import BeautifulSoup
    from urllib.request import urlopen

    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    meal = received_json_data['content']

    ScCode = 1

    if meal == '조식' or meal == '내일의 조식':
        ScCode = 1
    if meal == '중식' or meal == '내일의 중식':
        ScCode = 2
    if meal == '석식' or meal == '내일의 석식':
        ScCode = 3

    # NEIS에서 파싱, 타학교는 schulCode 수정 필요
    html = urlopen('http://stu.gne.go.kr/sts_sci_md01_001.do?schulCode=S100000747&schulCrseScCode=4&schulKndScCode=04&schMmealScCode=' + str(ScCode))
    source = html.read()
    html.close()

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
    if meal == '조식' or meal == '중식' or meal == '석식':
        if today == 0:
            menu = td[8]
        elif today == 1:
            menu = td[9]
        elif today == 2:
            menu = td[10]
        elif today == 3:
            menu = td[11]
        elif today == 5:
            menu = td[12]
        elif today == 6:
            menu = td[13]

    elif meal == '내일의 조식' or meal == '내일의 중식' or meal == '내일의 석식':
        if today == 0:
            menu = td[9]
        elif today == 1:
            menu = td[10]
        elif today == 2:
            menu = td[11]
        elif today == 3:
            menu = td[12]
        elif today == 5:
            menu = td[13]
        elif today == 6:
            menu = td[14]

    # 파싱 후 불필요한 태그 잔해물 제거
    menu = str(menu).replace(' ', '').replace('*', '').replace('<td', "").replace('<br/>', "\n").replace('class="textC">', '').replace('</td>', '').replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '').replace('6.', '').replace('7.', '').replace('8.', '').replace('9.', '').replace('10.', '').replace('11.', '').replace('12.', '').replace('13.', '').replace('14.', '').replace('15.', '').replace('1', '')

    return menu