import calendar
import datetime
import os
import re
import time

import pymysql
import requests
import vk_api as vkapi
from bs4 import BeautifulSoup
from pymysql.cursors import DictCursor
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

output_rows = []
writeyourgroup = {}
writeyourdate = {}
writeyourweekday = {}
writesearchgroup = {}
mysql_l = os.environ['MYSQL_LOGIN']
mysql_p = os.environ["MYSQL_PASS"]
access_token = os.environ["ACCESS_TOKEN"]
vk = vkapi.VkApi(token=access_token)
KeyboardNumDays = {0: 'E',
                   1: 'T',
                   2: 'K',
                   3: 'N',
                   4: 'R',
                   5: 'L',
                   6: 'P'}
DayOfWeek = {'E': 'Понедельник',
             'T': 'Вторник',
             'K': 'Среда',
             'N': 'Четверг',
             'R': 'Пятница',
             'L': 'Суббота',
             'P': "Воскресенье"}

# клавиатура
keyboard = VkKeyboard(one_time=False, inline=False)
WeekDayskeyboard = VkKeyboard(one_time=False, inline=True)
FiveDayskeyboard = VkKeyboard(one_time=False, inline=True)

keyboard.add_button('Моя группа', color=VkKeyboardColor.PRIMARY)
keyboard.add_line()
keyboard.add_button('По датам', color=VkKeyboardColor.DEFAULT)
keyboard.add_line()
keyboard.add_button('По дню недели', color=VkKeyboardColor.DEFAULT)
keyboard.add_line()  # Переход на вторую строку
keyboard.add_button('По группам', color=VkKeyboardColor.DEFAULT)
keyboard.add_line()  # Переход на вторую строку
keyboard.add_button('В какой я группе?', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('Изменить группу', color=VkKeyboardColor.NEGATIVE)
keyboard.add_line()  # Переход на вторую строку
keyboard.add_button("Поддержать проект", color=VkKeyboardColor.DEFAULT)
keyboard.add_button("Рассылка", color=VkKeyboardColor.NEGATIVE)


def numdayweek():
    result = time.gmtime(7200)
    return calendar.weekday(result.tm_year, result.tm_mon, result.tm_mday)


def keynumdays():
    todaydate = datetime.date.today() + datetime.timedelta(hours=2)
    day2date = datetime.date.today() + datetime.timedelta(hours=2) + datetime.timedelta(days=1)
    day3date = datetime.date.today() + datetime.timedelta(hours=2) + datetime.timedelta(days=2)
    day4date = datetime.date.today() + datetime.timedelta(hours=2) + datetime.timedelta(days=3)
    day5date = datetime.date.today() + datetime.timedelta(hours=2) + datetime.timedelta(days=4)
    todayweek = calendar.weekday(todaydate.year, todaydate.month, todaydate.day)
    day2week = calendar.weekday(day2date.year, day2date.month, day2date.day)
    day3week = calendar.weekday(day3date.year, day3date.month, day3date.day)
    day4week = calendar.weekday(day4date.year, day4date.month, day4date.day)
    day5week = calendar.weekday(day5date.year, day5date.month, day5date.day)
    todaydate = [todaydate.day, todaydate.month, todaydate.year]
    day2date = [day2date.day, day2date.month, day2date.year]
    day3date = [day3date.day, day3date.month, day3date.year]
    day4date = [day4date.day, day4date.month, day4date.year]
    day5date = [day5date.day, day5date.month, day5date.year]
    datelist = [todaydate, day2date, day3date, day4date, day5date]
    for i in datelist:
        if i[0] < 10:
            i[0] = str(i[0])
            i[0] = '0' + i[0]
        if i[1] < 10:
            i[1] = str(i[1])
            i[1] = '0' + i[1]
    today = f"{KeyboardNumDays[todayweek]}: {(datelist[0])[0]}.{(datelist[0])[1]}.{(datelist[0])[2]}"
    day2 = f"{KeyboardNumDays[day2week]}: {(datelist[1])[0]}.{(datelist[1])[1]}.{(datelist[1])[2]}"
    day3 = f"{KeyboardNumDays[day3week]}: {(datelist[2])[0]}.{(datelist[2])[1]}.{(datelist[2])[2]}"
    day4 = f"{KeyboardNumDays[day4week]}: {(datelist[3])[0]}.{(datelist[3])[1]}.{(datelist[3])[2]}"
    day5 = f"{KeyboardNumDays[day5week]}: {(datelist[4])[0]}.{(datelist[4])[1]}.{(datelist[4])[2]}"
    return today, day2, day3, day4, day5


WeekDayskeyboard.add_button("E", color=VkKeyboardColor.DEFAULT)
WeekDayskeyboard.add_button("T", color=VkKeyboardColor.DEFAULT)
WeekDayskeyboard.add_button("K", color=VkKeyboardColor.DEFAULT)
WeekDayskeyboard.add_button("N", color=VkKeyboardColor.DEFAULT)
WeekDayskeyboard.add_line()
WeekDayskeyboard.add_button("R", color=VkKeyboardColor.DEFAULT)
WeekDayskeyboard.add_button("L", color=VkKeyboardColor.NEGATIVE)
WeekDayskeyboard.add_button("P", color=VkKeyboardColor.NEGATIVE)

today, day2, day3, day4, day5 = keynumdays()

FiveDayskeyboard.add_button(today, color=VkKeyboardColor.POSITIVE)
FiveDayskeyboard.add_line()
FiveDayskeyboard.add_button(day2, color=VkKeyboardColor.PRIMARY)
FiveDayskeyboard.add_line()
FiveDayskeyboard.add_button(day3, color=VkKeyboardColor.PRIMARY)
FiveDayskeyboard.add_line()
FiveDayskeyboard.add_button(day4, color=VkKeyboardColor.PRIMARY)
FiveDayskeyboard.add_line()
FiveDayskeyboard.add_button(day5, color=VkKeyboardColor.PRIMARY)



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
        for i in row:
            usergroup[i['vkid']] = i['thkruhm']
    cursor.close()
    connection.close()
    return usergroup


def updatefile(usergroup):
    connection = pymysql.connect(
        host='eu-cdbr-west-02.cleardb.net',
        user=mysql_l,
        password=mysql_p,
        db='heroku_0ccfbccd1823b55',
        cursorclass=DictCursor)
    with connection.cursor() as cursor:
        cursor.execute("""SELECT vkid FROM users""")
        row = cursor.fetchall()
        for i in row:
            otheruser.append(i['vkid'])
        for i in usergroup.keys():
            if i in otheruser:
                cursor.execute("""UPDATE `heroku_0ccfbccd1823b55`.`users` SET `thkruhm`='%s' WHERE (`vkid`='%s');""" % (
                    usergroup[i], i))
            else:
                cursor.execute(
                    """INSERT INTO `heroku_0ccfbccd1823b55`.`users`(`vkid`, `thkruhm`) VALUES ('%s', '%s');""" % (
                        i, usergroup[i]))
        cursor.close()
    connection.commit()
    connection.close()
    return usergroup

def sendStatus(vkid):
    connection = pymysql.connect(
        host='eu-cdbr-west-02.cleardb.net',
        user=mysql_l,
        password=mysql_p,
        db='heroku_0ccfbccd1823b55',
        cursorclass=DictCursor)
    with connection.cursor() as cursor:
        cursor.execute("SELECT sendStatus FROM users WHERE vkid = %s", (vkid,))
        row = cursor.fetchone()
        sendstatus = row['sendStatus']
        if sendstatus == 1:
            cursor.execute("UPDATE `users` SET `sendStatus`=0 WHERE vkid=%s", (vkid,))
            connection.commit()
            cursor.close()
            connection.close()
            return "Рассылка была успешно выключена."
        cursor.execute("UPDATE `users` SET `sendStatus`=1 WHERE `vkid`=%s", (vkid,))
        connection.commit()
        cursor.close()
        connection.close()
        return "Рассылка была успешно включена."


def write_msg(user_id, random_id, message):
    vk.method('messages.send', {'user_id': user_id, 'random_id': random_id, 'message': message})


def send_keyboard(peer_id, random_id, message):
    vk.method('messages.send',
              {'peer_id': peer_id, 'random_id': random_id, 'keyboard': keyboard.get_keyboard(), 'message': message})


def send_weekkeyboard(peer_id, random_id, message):
    vk.method('messages.send', {'peer_id': peer_id, 'random_id': random_id, 'keyboard': WeekDayskeyboard.get_keyboard(),
                                'message': message})


def send_datekeyboard(peer_id, random_id, message):
    vk.method('messages.send', {'peer_id': peer_id, 'random_id': random_id, 'keyboard': FiveDayskeyboard.get_keyboard(),
                                'message': message})


def get_servertime():
    return vk.method('utils.getServerTime')


# Ничего особенного.

print("Время запуска бота:")
print(time.strftime("%D %H:%M", time.localtime()))


def parsepage():
    r = requests.get('http://www.tthk.ee/tunniplaani-muudatused/')
    html_content = r.text
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.findChildren('table')
    muudatused = []
    for item in table:
        my_table = item
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


def makemuudatused(i, forshow, kuupaev):
    if kuupaev == False:
        if len(i) == 6:
            forshow.append(f"🦆 Группа: {i[2]} ⏰ Урок: {i[3]} \n👨‍🏫 Преподаватель: {i[4]}\nКабинет: {i[5]}\n")
        elif len(i) > 2 and i[3].receivedMsgText() in "jääb ära":
            forshow.append(f"🦆 {i[2]}\n❌ Не состоится\n")
        elif len(i) > 4 and i[4].receivedMsgText() in "jääb ära":
            forshow.append(f"🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n❌ Не состоится\n")
        elif len(i) > 4 and i[4].receivedMsgText() in "söögivahetund":
            forshow.append(f"🦆 Группа: {i[2]}\n ⏰ Урок: {i[3]}\n🆒 Обеденный перерыв\n")
        elif len(i) > 5 and i[5].receivedMsgText() in "iseseisev töö kodus":
            forshow.append(f"🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n🏠 Самостоятельная работа дома\n")
        elif len(i) > 5 and i[5].receivedMsgText() in "iseseisev töö":
            forshow.append(f"🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n📋 Самостоятельная работа\n")
        elif len(i) > 5 and i[5].receivedMsgText() in ["", " "]:
            forshow.append(f"🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n👨‍🏫 Преподаватель: {i[4]}\n")
        else:
            forshow.append(f"🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n")
    elif kuupaev == True:
        if len(i) == 6:
            forshow.append(
                f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]} \n👨‍🏫 Преподаватель: {i[4]}\nКабинет: {i[5]}\n")
        elif len(i) > 2 and i[3].receivedMsgText() in "jääb ära":
            forshow.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 {i[2]}\n❌ Не состоится\n")
        elif len(i) > 4 and i[4].receivedMsgText() in "jääb ära":
            forshow.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n❌ Не состоится\n")
        elif len(i) > 4 and i[4].receivedMsgText() in "söögivahetund":
            forshow.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]}\n ⏰ Урок: {i[3]}\n🆒 Обеденный перерыв\n")
        elif len(i) > 5 and i[5].receivedMsgText() in "iseseisev töö kodus":
            forshow.append(
                f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n🏠 Самостоятельная работа дома\n")
        elif len(i) > 5 and i[5].receivedMsgText() in "iseseisev töö":
            forshow.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n📋 Самостоятельная работа\n")
        elif len(i) > 5 and i[5].receivedMsgText() in ["", " "]:
            forshow.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n👨‍🏫 Преподаватель: {i[4]}\n")
        else:
            forshow.append(f"🗓 В {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n")
    return forshow


def getmuudatused(setgroup, user):
    forshow = []
    muudatused = parsepage()
    for i in muudatused:
        if setgroup.receivedMsgText() in i[2].receivedMsgText():
            makemuudatused(i, forshow, True)
    if forshow:
        kogutunniplaan = f"Для группы 🦆 {setgroup} на данный момент следующие изменения в расписании:\n"
        for w in forshow:
            kogutunniplaan += f"{w}\n"
        write_msg(user, event.random_id, kogutunniplaan)
    elif len(forshow) == 0:
        write_msg(user, event.random_id, "Для группы, которую вы указали изменений в расписании нет.")


def getmuudatusedall(user, date):
    forshow = []
    muudatused = parsepage()
    for i in muudatused:
        if i[1] == date:
            makemuudatused(i, forshow, False)
    if forshow:
        kogutunniplaan = f"В учебном заведении на 🗓 {date} следующие изменения в расписании:\n"
        for w in forshow:
            kogutunniplaan += f"{w}\n"
        write_msg(user, event.random_id, kogutunniplaan)
    elif len(forshow) == 0:
        write_msg(user, event.random_id, f"В данный момент изменений в расписании нет на {date}, которую вы ввели.")


def getmuudatusedweekly(user, weekday):
    forshow = []
    muudatused = parsepage()
    for i in muudatused:
        if i[0] == weekday:
            makemuudatused(i, forshow, False)
    if forshow:
        kogutunniplaan = f"В учебном заведении на 🗓 {DayOfWeek[weekday]} следующие изменения в расписании:\n"
        for w in forshow:
            kogutunniplaan += f"{w}\n"
        write_msg(user, event.random_id, kogutunniplaan)
    elif len(forshow) == 0:
        write_msg(user, event.random_id,
                  f"В данный момент изменений в расписании нет на день недели, который вы ввели.")


longpoll = VkLongPoll(vk)
for event in longpoll.listen():
    usergroup = {}
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        uid = str(event.user_id)
        receivedMsgText = event.text.receivedMsgText()
        if receivedMsgText in ["начать", 'start']:
            usergroup = openfromfile(usergroup)
            send_keyboard(event.peer_id, event.random_id, "Выберите вариант из клаиватуры ниже.")
            if uid not in usergroup.keys():
                write_msg(event.user_id, event.random_id,
                          "У вас не указан код группы, напишите его сообщением снизу без подгруппы. Пример: вместо MEHpv19-2 или LOGApv19-1 - напишите MEHpv19 или LOGApv19.")
                writeyourgroup[uid] = 1
        elif receivedMsgText in ["указать группу", "изменить группу"]:
            usergroup = openfromfile(usergroup)
            write_msg(event.user_id, event.random_id,
                      "В какой группе вы находитесь?Для групп, которые делятся на подгруппы указывается только группа: MEHpv19 вместо MEHpv19-2.\nУкажите код вашей группы: ")
            writeyourgroup[uid] = 1
            writesearchgroup[uid] = 0
        elif receivedMsgText[-3:] in ['v20', 'e20', 'v19', 'v18', 'v17', 'e19', 'e18',
                                      'e17'] and uid in writeyourgroup.keys() and writeyourgroup[uid] == 1:
            otheruser = []
            group = event.text
            usergroup[str(event.user_id)] = group
            usergroup = updatefile(usergroup)
            usergroup = openfromfile(usergroup)
            write_msg(event.user_id, event.random_id, f"Вы указали, что Ваша группа: {usergroup[uid]}.")
            writeyourgroup[uid] = 0
        elif receivedMsgText == "изменения по группам":
            write_msg(event.user_id, event.random_id, f"Введите код группы, для которой нужно найти изменения: ")
            writeyourgroup[uid] = 0
            writesearchgroup[uid] = 1
        elif receivedMsgText[-3:] in ['v20', 'e20', 'v19', 'v18', 'v17', 'e19', 'e18',
                                      'e17'] and uid in writesearchgroup.keys() and writesearchgroup[uid] == 1:
            setgroup = event.text
            lastmuudatused = getmuudatused(setgroup, event.user_id)
            writesearchgroup[uid] = 0
        elif receivedMsgText[-3:] in ['v20', 'e20', 'v19', 'v18', 'v17', 'e19', 'e18',
                                      'e17'] and uid in writeyourgroup.keys() and writeyourgroup[uid] == 0:
            write_msg(event.user_id, event.random_id,
                      f"Для того, чтобы указать группу предварительно нажмите Изменить группу.")
        elif receivedMsgText == "в какой я группе?":
            usergroup = openfromfile(usergroup)
            if uid not in usergroup.keys():
                write_msg(event.user_id, event.random_id, "У вас не указан код группы.")
                write_msg(event.user_id, event.random_id,
                          "В какой группе вы находитесь?\nУкажите код вашей группы: ")
                writeyourgroup[uid] = 1
            if uid in usergroup.keys():
                write_msg(event.user_id, event.random_id,
                          f"Вы указали, что Ваша группа: {usergroup[uid]}.\nДля того, чтобы изменить свою группу нажмите \"Изменить группу\".")
        elif receivedMsgText == "моя группа":
            usergroup = openfromfile(usergroup)
            if uid not in usergroup.keys():
                write_msg(event.user_id, event.random_id, "У вас не указан код группы.")
                write_msg(event.user_id, event.random_id,
                          "В какой группе вы находитесь?\nУкажите код вашей группы: ")
                writeyourgroup[uid] = 1
            if uid in usergroup.keys():
                lastmuudatused = getmuudatused(usergroup[uid], event.user_id)
        elif receivedMsgText == "по датам":
            send_datekeyboard(event.peer_id, event.random_id,
                              f"Выберите дату, которую желаете найти или укажите в формате ДД.ММ.ГГГГ:")
            writeyourdate[uid] = 1
        elif receivedMsgText == "рассылка":
            write_msg(event.user_id, event.random_id, sendStatus(event.user_id))
        elif receivedMsgText == "по дню недели":
            send_weekkeyboard(event.peer_id, event.random_id,
                              "Выберите день недели с помощью клавиатуры: E, T, K, N, R, L, P.")
            writeyourweekday[uid] = 1
        elif receivedMsgText.upper() in ['E', 'T', 'K', 'N', 'R', 'L', 'P'] and uid in writeyourweekday.keys() and \
                writeyourweekday[uid] == 1:
            getmuudatusedweekly(event.user_id, event.text)
            writeyourweekday[uid] = 0
        elif event.text[-5:].receivedMsgText() in ['.2020', '.2021', '.2022', '.2023', '.2024', '.2025',
                                                   '.2026'] and uid in writeyourdate.keys() and writeyourdate[
            uid] == 1:
            if event.text[1] == ":":
                enddatetosearch = re.split(r':\s', event.text)
                newmuudatused = getmuudatusedall(event.user_id, enddatetosearch[1])
            else:
                newmuudatused = getmuudatusedall(event.user_id, event.text)
            writeyourdate[uid] = 0
        elif receivedMsgText == "поддержать проект":
            write_msg(event.peer_id, event.random_id, "https://www.paypal.me/blinchk")
        else:
            write_msg(event.user_id, event.random_id, f"Данной команды не существует")