import vk_api as vkapi
import requests
import calendar
import datetime
from bs4 import BeautifulSoup
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton
import json
import os
import time
import re
output_rows = []
writeyourgroup = {}
writeyourdate = {}
writeyourweekday = {}
usergroup = {}



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

keyboard.add_button('Изменения моей группы', color=VkKeyboardColor.PRIMARY)
keyboard.add_line()
keyboard.add_button('Изменения по датам', color=VkKeyboardColor.DEFAULT)
keyboard.add_line()
keyboard.add_button('Изменения по дню недели', color=VkKeyboardColor.DEFAULT)
keyboard.add_line()  # Переход на вторую строку
keyboard.add_button('В какой я группе?', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('Изменить группу', color=VkKeyboardColor.NEGATIVE)


def numdayweek():
    result = time.gmtime(2)
    return calendar.weekday(result.tm_year, result.tm_mon, result.tm_mday)

def keynumdays():
    todaydate = datetime.date.today()
    day2date = datetime.date.today() + datetime.timedelta(days=1)
    day3date = datetime.date.today() + datetime.timedelta(days=2)
    day4date = datetime.date.today() + datetime.timedelta(days=3)
    day5date = datetime.date.today() + datetime.timedelta(days=4)
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

if numdayweek() == 0:
    WeekDayskeyboard.add_button("E", color=VkKeyboardColor.POSITIVE)
else:
    WeekDayskeyboard.add_button("E", color=VkKeyboardColor.DEFAULT)
if numdayweek() == 1:
    WeekDayskeyboard.add_button("T", color=VkKeyboardColor.POSITIVE)
else:
    WeekDayskeyboard.add_button("T", color=VkKeyboardColor.DEFAULT)
if numdayweek() == 2:
    WeekDayskeyboard.add_button("K", color=VkKeyboardColor.POSITIVE)
else:
    WeekDayskeyboard.add_button("K", color=VkKeyboardColor.DEFAULT)
WeekDayskeyboard.add_line()
if numdayweek() == 3:
    WeekDayskeyboard.add_button("N", color=VkKeyboardColor.POSITIVE)
else:
    WeekDayskeyboard.add_button("N", color=VkKeyboardColor.DEFAULT)
if numdayweek() == 4:
    WeekDayskeyboard.add_button("R", color=VkKeyboardColor.POSITIVE)
else:
    WeekDayskeyboard.add_button("R", color=VkKeyboardColor.DEFAULT)
if numdayweek() == 5:
    WeekDayskeyboard.add_button("L", color=VkKeyboardColor.POSITIVE)
else:
    WeekDayskeyboard.add_button("L", color=VkKeyboardColor.NEGATIVE)
if numdayweek() == 6:
    WeekDayskeyboard.add_button("P", color=VkKeyboardColor.POSITIVE)
else:
    WeekDayskeyboard.add_button("P", color=VkKeyboardColor.NEGATIVE)

today, day2, day3, day4, day5 = keynumdays()

FiveDayskeyboard.add_button(today, color=VkKeyboardColor.POSITIVE)
FiveDayskeyboard.add_button(day2, color=VkKeyboardColor.PRIMARY)
FiveDayskeyboard.add_button(day3, color=VkKeyboardColor.PRIMARY)
FiveDayskeyboard.add_button(day4, color=VkKeyboardColor.PRIMARY)
FiveDayskeyboard.add_button(day5, color=VkKeyboardColor.PRIMARY)

# парсим
r = requests.get('http://www.tthk.ee/tunniplaani-muudatused/')
html_content = r.text
soup = BeautifulSoup(html_content, 'html.parser')
table = soup.findChildren('table')
def updatefile(usergroup):
    file = open('ids.txt', 'w', encoding='utf-8')
    file.write(json.dumps(usergroup))
    file.close()
    return usergroup
def openfromfile(usergroup):
    file = open('ids.txt', 'r', encoding='utf-8')
    usergroup = eval(file.read())
    file.close()
    return usergroup
def write_msg(user_id, random_id, message):
    vk.method('messages.send', {'user_id': user_id, 'random_id': random_id, 'message': message})
def send_keyboard(peer_id, random_id, message):
    vk.method('messages.send', {'peer_id': peer_id, 'random_id': random_id, 'keyboard': keyboard.get_keyboard(), 'message': message})
def send_weekkeyboard(peer_id, random_id, message):
    vk.method('messages.send', {'peer_id': peer_id, 'random_id': random_id, 'keyboard': WeekDayskeyboard.get_keyboard(), 'message': message})
def send_datekeyboard(peer_id, random_id, message):
    vk.method('messages.send', {'peer_id': peer_id, 'random_id': random_id, 'keyboard': FiveDayskeyboard.get_keyboard(), 'message': message})
# Ничего особенного.

usergroup = openfromfile(usergroup)


def parsepage(table):
    print(len(table))
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

def getmuudatused(setgroup, usergroup, user):
    forshow = []
    muudatused = parsepage(table)
    for i in muudatused:
        if setgroup in i[2]:
            if i[4] == " ":
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]}")
            elif i[4].lower() == "jääb ära" and (i[5] == "" or i[5] == None):
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} не состоится")
            elif i[4].lower() == "söögivahetund" and (i[5] == "" or i[5] == None):
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} обеденный перерыв")
            elif i[5].lower() == "iseseisev töö kodus":
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} самостоятельная работа дома")
            else:
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} Преподаватель: {i[4]} Кабинет: {i[5]}")
    if len(forshow) > 0:
        write_msg(event.user_id, event.random_id, f"Для группы {setgroup} на данный момент следующие изменения в расписании:")
        send_keyboard(event.user_id, event.random_id, "Что-то ещё?")
        for w in forshow:
            write_msg(event.user_id, event.random_id, w)
    elif len(forshow) == 0:
        write_msg(user, event.random_id,"Для вашей группы изменений в расписании нет. Подробнее: www.tthk.ee/tunniplaani-muudatused.")
        send_keyboard(event.user_id, event.random_id, "Что-то ещё?")

def getmuudatusedall(user, date):
    forshowall = []
    muudatused = parsepage(table)
    for i in muudatused:
        if i[4] == " ":
            if i[1] == date:
                forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]}")
        elif i[4].lower() == "jääb ära" and (i[5] == "" or i[5] == None):
            if i[1] == date:
                forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} не состоится")
        elif i[4].lower() == "söögivahetund" and (i[5] == "" or i[5] == None):
            if i[1] == date:
                forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} обеденный перерыв")
        elif i[5].lower() == "iseseisev töö kodus":
            if i[1] == date:
                forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} самостоятельная работа дома")
        else:
            if i[1] == date:
                forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} Преподаватель: {i[4]} Кабинет: {i[5]}")
    if len(forshowall) > 0:
        write_msg(user, event.random_id, f"В учебном заведении на {date} следующие изменения в расписании:")
        kogutunniplaan = ""
        for w in forshowall:
            kogutunniplaan += f"{w}\n"
        write_msg(user, event.random_id, kogutunniplaan)
        send_keyboard(event.user_id, event.random_id, "Что-то ещё?")
    elif len(forshowall) == 0:
        write_msg(user, event.random_id,"В данный момент изменений в расписании нет на дату, которую вы ввели. Подробнее: www.tthk.ee/tunniplaani-muudatused.")
        send_keyboard(event.user_id, event.random_id, "Что-то ещё?")

def getmuudatusedweekly(user, weekday):
    forshoweek = []
    muudatused = parsepage(table)
    for i in muudatused:
        if i[4] == " ":
            if i[0] == weekday:
                forshoweek.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]}")
        elif i[4].lower() == "jääb ära" and (i[5] == "" or i[5] == None):
            if i[0] == weekday:
                forshoweek.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} не состоится")
        elif i[4].lower() == "söögivahetund" and (i[5] == "" or i[5] == None):
            if i[0] == weekday:
                forshoweek.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} обеденный перерыв")
        elif i[5].lower() == "iseseisev töö kodus":
            if i[0] == weekday:
                forshoweek.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} самостоятельная работа дома")
        else:
            if i[0] == weekday:
                forshoweek.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} Преподаватель: {i[4]} Кабинет: {i[5]}")
    if len(forshoweek) > 0:
        write_msg(user, event.random_id, f"В учебном заведении на {DayOfWeek[weekday]} следующие изменения в расписании:")
        kogutunniplaan = ""
        for w in forshoweek:
            kogutunniplaan += f"{w}\n"
        write_msg(user, event.random_id, kogutunniplaan)
        send_keyboard(event.user_id, event.random_id, "Что-то ещё?")
    elif len(forshoweek) == 0:
        write_msg(user, event.random_id,"В данный момент изменений в расписании нет на день недели, который вы ввели. Подробнее: www.tthk.ee/tunniplaani-muudatused.")
        send_keyboard(event.user_id, event.random_id, "Что-то ещё?")


longpoll = VkLongPoll(vk)
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            if event.text.lower() == "начать" or event.text.lower() == 'start':
                usergroup = openfromfile(usergroup)
                send_keyboard(event.peer_id, event.random_id, "Выберите вариант из клаиватуры ниже.")
                if str(event.user_id) not in usergroup.keys():
                    write_msg(event.user_id, event.random_id, "У вас не указан код группы.")
            elif event.text.lower() == "указать группу" or event.text.lower() == "изменить группу":
                write_msg(event.user_id, event.random_id, "В какой группе вы находитесь?\nУкажите код вашей группы: ")
                writeyourgroup[event.user_id] = 1
            elif event.text[-3:].lower() in ['v19', 'v18', 'v17', 'e19', 'e18', 'e17'] and writeyourgroup[event.user_id] == 1:
                group = event.text
                usergroup[str(event.user_id)] = group
                write_msg(event.user_id, event.random_id, f"Вы указали, что Ваша группа: {usergroup[str(event.user_id)]}.")
                writeyourgroup[event.user_id] = 0
                usergroup = updatefile(usergroup)
                send_keyboard(event.user_id, event.random_id, "Что-то ещё?")
            elif str(event.user_id) not in writeyourgroup.keys() and event.text[-3:].lower() in ['v19', 'v18', 'v17', 'e19', 'e18', 'e17']:
                write_msg(event.user_id, event.random_id, f"Данной команды не существует.")
                write_msg(event.user_id, event.random_id, f"Для того, чтобы указать группу предварительно нажмите Изменить группу.")
                send_keyboard(event.user_id, event.random_id, "Что-то ещё?")
            elif event.text.lower() == "в какой я группе?":
                if str(event.user_id) not in usergroup.keys():
                    write_msg(event.user_id, event.random_id, "У вас не указан код группы.")
                    write_msg(event.user_id, event.random_id, "В какой группе вы находитесь?\nУкажите код вашей группы: ")
                    writeyourgroup[event.user_id] = 1
                if str(event.user_id) in usergroup.keys():
                    write_msg(event.user_id, event.random_id, f"Вы указали, что Ваша группа: {usergroup[str(event.user_id)]}.")
            elif event.text.lower() == "изменения моей группы":
                if str(event.user_id) not in usergroup.keys():
                    write_msg(event.user_id, event.random_id, "У вас не указан код группы.")
                    write_msg(event.user_id, event.random_id, "В какой группе вы находитесь?\nУкажите код вашей группы: ")
                    writeyourgroup[event.user_id] = 1
                if str(event.user_id) in usergroup.keys():
                    setgroup = usergroup[str(event.user_id)]
                    lastmuudatused = getmuudatused(setgroup, usergroup, event.user_id)
            elif event.text.lower() == "изменения по датам":
                send_datekeyboard(event.peer_id, event.random_id, f"Выберите дату, которую желаете найти или укажите в формате ДД.ММ.ГГГГ:")
                writeyourdate[str(event.user_id)] = 1
            elif event.text.lower() == "изменения по дню недели":
                send_weekkeyboard(event.peer_id, event.random_id, "Выберите день недели с помощью клавиатуры: E, T, K, N, R, L, P.")
                writeyourweekday[str(event.user_id)] = 1
            elif event.text.lower() in ['e', 't', 'k', 'n', 'r', 'l', 'p'] and str(event.user_id) in writeyourweekday.keys():
                getmuudatusedweekly(event.user_id, event.text)
            elif event.text[-5:].lower() in ['.2020', '.2021', '.2022', '.2023', '.2024', '.2025', '.2026'] and writeyourdate[str(event.user_id)] == 1:
                if event.text[1] == ":":
                    enddatetosearch = re.split(r':\s',event.text)
                    newmuudatused = getmuudatusedall(event.user_id, enddatetosearch[1])
                else:
                    newmuudatused = getmuudatusedall(event.user_id, event.text)
            else:
                write_msg(event.user_id, event.random_id, f"Данной команды не существует.")
