from datetime import *
from dateutil.relativedelta import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json
import sqlite3

@csrf_exempt
def hyoammeal(request):
    json_data = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_data)
    select_date = int(received_json_data['action']['params']['date'])

    daystring = ["월", "화", "수", "목", "금", "토", "일"]

    today = date.today().weekday()
    today_date = date.today()

    if today == 6:
        day = today_date + relativedelta(weekday=select_date)
    else:
        day = today_date + relativedelta(days=-today, weekday=select_date)

    return JsonResponse({
        'text': day.strftime("%m월 %d일 ") + daystring[select_date] + ' 식단표입니다. \n \n' + data_from_db(select_date)
    })

def data_from_db(select_day):
    daystring_eng = ["mon", "tue", "wed", "thu", "fri", "sat"]

    con = sqlite3.connect("meal.db")
    cur = con.cursor()
    query = ("SELECT " + (daystring_eng[select_day]) + " FROM meal")
    cur.execute(query)
    data = cur.fetchone()
    con.close()

    return data[0]