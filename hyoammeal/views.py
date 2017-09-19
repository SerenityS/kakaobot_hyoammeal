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
    elif meal in daystring and meal != "일":
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
                'text': '잘못된 명령어입니다 ' + '[' + meal + ']' + '\n입력 가능 명령어 : 월 화 수 목 금 토'
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
    daystring = ["월", "화", "수", "목", "금", "토"]

    # 0(월요일) ~ 5(토요일).txt read
    if meal == '오늘 식단표':
        f = open(str(today) + ".txt", 'r')
    if meal == '내일 식단표':
        if today == 6:
            f = open("0.txt", 'r')
        else:
            today = today + 1
            f = open(str(today) + ".txt", 'r')
    if meal in daystring:
        f = open(str(daystring.index(meal)) + ".txt", 'r')
    menu = f.read()
    f.close()

    return menu
