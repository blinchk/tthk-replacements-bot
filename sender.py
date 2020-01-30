from bs4 import BeautifulSoup
import time
import requests
import pymysql
import os
import random
from pymysql.cursors import DictCursor
print("Sender launched")

mysql_l = os.environ['MYSQL_LOGIN']
mysql_p = os.environ["MYSQL_PASS"]
access_token = os.environ["ACCESS_TOKEN"]

r = requests.get('http://www.tthk.ee/tunniplaani-muudatused/')
html_content = r.text
soup = BeautifulSoup(html_content, 'html.parser')
table = soup.findChildren('table')

def write_msg(user_id, random_id, message):
    vk.method('messages.send', {'user_id': user_id, 'random_id': random_id, 'message': message})

def parsepage(table):
    muudatused = []
    for i in range(len(table)):
        my_table = table[i]
        rows = my_table.find_all('tr')
        for row in rows:
            muudatus = []
            cells = row.find_all('td')
            for cell in cells:
                if cell.text not in ["\xa0", "Kuupäev", "Rühm", "Tund", "Õpetaja", "Ruum"]:
                    data = cell.text
                    muudatus.append(data)
            # здесь есть полноценный список muudatus
            if muudatus != []:
                muudatused.append(muudatus)
        else:
            continue
    return muudatused

def openfromfile(usergroup):
    connection = pymysql.connect(
        host='eu-cdbr-west-02.cleardb.net',
        user=mysql_l,
        password=mysql_p,
        db='heroku_0ccfbccd1823b55',
        cursorclass=DictCursor)
    with connection.cursor() as cursor:
        cursor.execute("""SELECT * FROM USERS""")
        row = cursor.fetchall()
#        print(row)
        for i in row:
#            print(i)
            usergroup[i['vkid']] = i['thkruhm']
    cursor.close()
    connection.close()
    return usergroup

def makemuudatused(i, forshow):
    if len(i) == 6:
        forshow.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]} \n👨‍🏫 Преподаватель: {i[4]}\nКабинет: {i[5]}\n")
    elif len(i) > 2 and i[3].lower() in "jääb ära":
        forshow.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 {i[2]}\n❌ Не состоится\n")
    elif len(i) > 4 and i[4].lower() in "jääb ära":
        forshow.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n❌ Не состоится\n")
    elif len(i) > 4 and i[4].lower() in "söögivahetund":
        forshow.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]}\n ⏰ Урок: {i[3]}\n🆒 Обеденный перерыв\n")
    elif len(i) > 5 and i[5].lower() in "iseseisev töö kodus":
        forshow.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n🏠 Самостоятельная работа дома\n")
    elif len(i) > 5 and i[5].lower() in "iseseisev töö":
        forshow.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n📋 Самостоятельная работа\n")
    elif len(i) > 5 and (i[5].lower() == "" or i[5].lower() == " "):
        forshow.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n👨‍🏫 Преподаватель: {i[4]}\n")
    else:
        forshow.append(f"🗓 В {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n")
    return forshow

def getmuudatused(setgroup, user):
    forshow = []
    muudatused = parsepage(table)
    for i in muudatused:
        if setgroup.lower() in i[2].lower():
            makemuudatused(i, forshow)
    if len(forshow) > 0:
        kogutunniplaan = f"Для группы 🦆 {setgroup} на данный момент следующие изменения в расписании:\n"
        for w in forshow:
            kogutunniplaan += f"{w}\n"
        write_msg(user, (random.getrandbits(31) * random.choice([-1, 1])), kogutunniplaan)
    elif len(forshow) == 0:
        write_msg(user, (random.getrandbits(31) * random.choice([-1, 1])), "Для группы, которую вы указали изменений в расписании нет.")

def sendeveryday():
    usergroup = {}
    usergroup = openfromfile(usergroup)
    print("Запускаю рассылку:")
    print(time.strftime("%H:%M:%S"))
    for i in usergroup.keys():
        getmuudatused(usergroup[i], i)


while True:
    if time.strftime("%H:%M:%S", time.localtime()) == '23:30:00':
        sendeveryday()
    time.sleep(1.1)
    continue
