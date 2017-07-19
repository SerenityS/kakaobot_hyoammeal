# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse

import json, datetime


def keyboard(request):
    return JsonResponse({
        'type': 'buttons',
        'buttons': ['조식', '중식', '석식']
    })


@csrf_exempt
def message(request):
    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    day = received_json_data['content']

    dayString = ["월", "화", "수", "목", "금", "토", "일"]
    today = datetime.datetime.today().weekday()

    today_date = datetime.date.today().strftime("%m월 %d일 ")

    return JsonResponse({
        'message': {
            'text': today_date + str(dayString[today]) + '요일 ' + day + ' 메뉴입니다. \n \n' + str(crawl(request))
        },
        'keyboard': {
            'type': 'buttons',
            'buttons': ['조식', '중식', '석식']
        }
    })


def crawl(request):
    from bs4 import BeautifulSoup

    from urllib.request import urlopen

    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    day = received_json_data['content']

    ScCode = 1

    if day == '조식':
        ScCode = 1
    if day == '중식':
        ScCode = 2
    if day == '석식':
        ScCode = 3

    html = urlopen(
        'http://stu.gne.go.kr/sts_sci_md01_001.do?schulCode=S100000747&schulCrseScCode=4&schulKndScCode=04&schMmealScCode=' + str(
            ScCode))
    source = html.read()
    html.close()

    soup = BeautifulSoup(source, "lxml", from_encoding='utf-8')
    received_json_data = json.loads(json_str)
    day = received_json_data['content']

    table_div = soup.find(id="contents")
    tables = table_div.find_all("table")
    menu_table = tables[0]
    td = menu_table.find_all('td')

    today = datetime.datetime.today().weekday()

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

    menu = str(menu).replace(' ', '').replace('*', '').replace('<td', "").replace('<br/>', "\n").replace('class="textC">', '').replace('</td>', '').replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '').replace('6.', '').replace('7.', '').replace('8.', '').replace('9.', '').replace('10.', '').replace('11.', '').replace('12.', '').replace('13.', '').replace('14.', '').replace('15.', '').replace('1', '')

    return menu

    # curl -XPOST 'http://127.0.0.1:8000/message' -d '{"user_key": "encryptedUserKey","type": "text","content": "조식"}'
