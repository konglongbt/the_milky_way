import os
import math
import random
import requests

from datetime import date, datetime
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate

today = datetime.now()

# 微信公众测试号ID和SECRET
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

# 可把os.environ结果替换成字符串在本地调试
user_ids = os.environ["USER_ID"].split(',')
template_ids = os.environ["TEMPLATE_ID"].split(',')
citys = os.environ["CITY"].split(',')
start_dates = os.environ["START_DATE"].split(',')
birthdays = os.environ["BIRTHDAY"].split(',')


# 获取天气和温度
def get_weather(city_id):   
    # 毫秒级时间戳
    t = (int(round(time() * 1000)))
    headers = {
        "Referer": "http://www.weather.com.cn/weather1d/{}.shtml".format(city_id),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    url = "http://d1.weather.com.cn/dingzhi/{}.html?_={}".format(city_id, t)
    response = get(url, headers=headers)
    response.encoding = "utf-8"
    response_data = response.text.split(";")[0].split("=")[-1]
    response_json = eval(response_data)
    # print(response_json)
    weatherinfo = response_json["weatherinfo"]
    # 天气
    weather = weatherinfo["weather"]
    # 最高气温
    temp = weatherinfo["temp"]
    # 最低气温
    tempn = weatherinfo["tempn"]
    return weather, temp, tempn


# 当前城市、日期
def get_city_date(city):
    return city, today.date().strftime("%Y-%m-%d")


# 距离设置的日期过了多少天
def get_count(start_date):
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days


# 距离发工资还有多少天
def get_solary(solary):
    next = datetime.strptime(str(date.today().year) + "-" + str(date.today().month) + "-" + solary, "%Y-%m-%d")
    if next < datetime.now():
        if next.month == 12:
            next = next.replace(year=next.year + 1)
        next = next.replace(month=(next.month + 1) % 12)
    return (next - today).days


# 距离过生日还有多少天
def get_birthday(birthday):
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    return (next - today).days


# 每日一句
def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


# 字体随机颜色
def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)

for i in range(len(user_ids)):
    wea, tem, temh = get_weather(citys[i])
    cit, dat = get_city_date(citys[i])
    data = {
        "date": {"value": "今日日期：{}".format(dat), "color": get_random_color()},
        "city": {"value": "当前城市：{}".format(cit), "color": get_random_color()},
        "weather": {"value": "今日天气：{}".format(wea), "color": get_random_color()},
        "temperature": {"value": "最低温度：{}".format(tem), "color": get_random_color()},
        "temperatureh": {"value": "最高温度：{}".format(temh), "color": get_random_color()},
        "love_days": {"value": "今天是你们在一起的第{}天".format(get_count(start_dates[i])), "color": get_random_color()},
        "birthday_left": {"value": "距离她的生日还有{}天".format(get_birthday(birthdays[i])), "color": get_random_color()},
        "words": {"value": get_words(), "color": get_random_color()}
    }
    if get_birthday(birthdays[i]) == 0:
        data["birthday_left"]['value'] = "今天是她的生日哦，快去一起甜蜜吧"
    res = wm.send_template(user_ids[i], template_ids[i], data)
    print(res)
