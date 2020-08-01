# Connecting vk_api
# Connecting time tools
import datetime
import json
# Connecting tools of deploy
import os
# Connecting parsing tools
import re
import urllib

# Connecting pyMySQL
import pymysql
import requests
import vk_api
from bs4 import BeautifulSoup
from pymysql.cursors import DictCursor
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id


# Multi-threading TO-DO
# import logging
# import threading

class Server:

    def __init__(self, api_token):
        self.vk = vk_api.VkApi(token=api_token)
        self.longpoll = VkLongPoll(self.vk)
        self.bot = Bot(self.vk)
        self.writeyourgroup = []
        self.writesearchgroup = []
        self.writeweekday = []
        self.writedate = []

    def start(self):
        print("Bot successfully deployed and started.")
        k = Keyboard()
        tc = TimeCatcher()
        db = SQL()
        c = Changes()
        covid = COVID()
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    print(event.text)
                    if event.text.lower() == 'начать':
                        self.bot.sendKeyboard(keyboard=k.keyboard, id=event.user_id,
                                              msg='Выберите вариант из списка ниже.')
                    elif event.text.lower() == 'covid-19':
                        self.bot.sendMsg(id=event.user_id, msg=covid.getData())
                    elif event.text.lower() == 'по датам':
                        self.writedate.append(event.user_id)
                        self.bot.sendKeyboard(keyboard=k.fiveDaysKeyboard, id=event.user_id,
                                              msg='Выберите дату из списка ниже:')
                    elif event.text.lower() == 'по дню недели':
                        self.writeweekday.append(event.user_id)
                        self.bot.sendKeyboard(keyboard=k.weekDaysKeyboard, id=event.user_id,
                                              msg='Выберите день недели из списка ниже:')
                    elif event.text.lower() == 'в какой я группе?':
                        self.bot.sendMsg(id=event.user_id,
                                         msg=f'Вы указали, что Ваша группа: {db.getUserGroup(id=event.user_id)}.\n'
                                             'Для того, чтобы изменить свою группу нажмите \"Изменить группу\".')
                    elif event.text.lower() == 'изменить группу':
                        self.bot.sendMsg(id=event.user_id, msg="В какой группе вы находитесь?\n"
                                                               "Для групп, которые делятся на подгруппы указывается только группа: MEHpv19 вместо MEHpv19-2.\n"
                                                               "Укажите код вашей группы:")
                        self.writeyourgroup.append(event.user_id)
                    elif event.text.lower()[-3:] in tc.getGroupList() and event.user_id in self.writeyourgroup:
                        db.setUserGroup(id=event.user_id, group=event.text)
                        self.bot.sendMsg(id=event.user_id,
                                         msg=f'Вы указали, что Ваша группа: {db.getUserGroup(id=event.user_id)}.')
                        self.writeyourgroup.remove(event.user_id)
                    elif event.text.lower() == 'моя группа':
                        self.bot.sendMsg(id=event.user_id, msg=c.makeChanges(db.getUserGroup(id=event.user_id)))
                    elif event.text.lower() == 'по группам':
                        self.bot.sendMsg(id=event.user_id, msg="Введите код группы, для которой нужно найти изменения:")
                        self.writesearchgroup.append(event.user_id)
                    elif event.text.lower()[-3:] in tc.getGroupList() and event.user_id in self.writesearchgroup:
                        self.bot.sendMsg(id=event.user_id, msg=c.makeChanges(event.text))
                        self.writesearchgroup.remove(event.user_id)
                    elif event.text in tc.keyboardNumDays and event.user_id in self.writeweekday:
                        self.bot.sendMsg(id=event.user_id, msg=c.makeChanges(event.text))
                        self.writeweekday.remove(event.user_id)
                    elif event.text[-4:] == str(datetime.date.today().year) and event.user_id in self.writedate:
                        self.bot.sendMsg(id=event.user_id, msg=c.makeChanges(event.text))
                        self.writedate.remove(event.user_id)
                    else:
                        self.bot.sendMsg(id=event.user_id, msg="Данной команды не существует.")
            elif event.type == VkEventType.USER_TYPING:
                print(f"Пользователь {event.user_id} пишет.")
            else:
                pass


class TimeCatcher:

    def __init__(self):
        self.keyboardNumDays = ['E', 'T', 'K', 'N', 'R', 'L', 'P']
        self.dayOfWeek = {'E': 'Понедельник',
                          'T': 'Вторник',
                          'K': 'Среда',
                          'N': 'Четверг',
                          'R': 'Пятница',
                          'L': 'Суббота',
                          'P': "Воскресенье"}
        self.datelist = []
        for i in range(5):  # Taking
            x = datetime.date.today() + datetime.timedelta(hours=2) + datetime.timedelta(days=i)
            self.datelist.append([self.keyboardNumDays[x.weekday()], x.day, x.month, x.year])
        for i in self.datelist:
            if i[1] < 10:
                i[1] = str(i[1])
                i[1] = '0' + i[1]
            if i[2] < 10:
                i[2] = str(i[2])
                i[2] = '0' + i[2]

    def todayWeekDay(self):
        return (datetime.date.today() + datetime.timedelta(hours=2)).weekday()

    def getGroupList(self):
        groupList = []
        yearnow = datetime.date.today().year
        for i in range(int(str(yearnow)[:-2]) - 3, int(str(yearnow)[:-2]) + 1, 1):
            groupList.append('v' + str(i))
            groupList.append('e' + str(i))
        return groupList


class Keyboard:

    def __init__(self):
        # Default keyboard
        self.keyboard = VkKeyboard(one_time=False, inline=False)
        self.keyboard.add_button('Моя группа', color=VkKeyboardColor.PRIMARY)
        self.keyboard.add_button('COVID-19', color=VkKeyboardColor.NEGATIVE)
        self.keyboard.add_line()
        self.keyboard.add_button('По датам', color=VkKeyboardColor.DEFAULT)
        self.keyboard.add_button('По дню недели', color=VkKeyboardColor.DEFAULT)
        self.keyboard.add_button('По группам', color=VkKeyboardColor.DEFAULT)
        self.keyboard.add_line()  # Переход на вторую строку
        self.keyboard.add_button('В какой я группе?', color=VkKeyboardColor.POSITIVE)
        self.keyboard.add_button('Изменить группу', color=VkKeyboardColor.NEGATIVE)
        self.keyboard.add_button('Рассылка', color=VkKeyboardColor.DEFAULT)
        # fiveDaysKeyboard
        self.fiveDaysKeyboard = VkKeyboard(one_time=False, inline=True)
        tc = TimeCatcher()
        for i in range(5):
            if i == 0:
                color = VkKeyboardColor.POSITIVE
            elif (tc.datelist[i])[0] == 'L' or (tc.datelist[i])[0] == 'P':
                color = VkKeyboardColor.NEGATIVE
            else:
                color = VkKeyboardColor.DEFAULT
            if i > 0: self.fiveDaysKeyboard.add_line()
            self.fiveDaysKeyboard.add_button(
                f"{(tc.datelist[i])[0]}: {(tc.datelist[i])[1]}.{(tc.datelist[i])[2]}.{(tc.datelist[i])[3]}", color)
        # weekDaysKeyboard
        self.weekDaysKeyboard = VkKeyboard(one_time=False, inline=True)
        for i in tc.keyboardNumDays:
            if tc.keyboardNumDays.index(i) == tc.todayWeekDay():
                color = VkKeyboardColor.POSITIVE
            elif tc.keyboardNumDays.index(i) == 5 or tc.keyboardNumDays.index(i) == 6:
                color = VkKeyboardColor.NEGATIVE
            else:
                color = VkKeyboardColor.DEFAULT
            if i == 'R': self.weekDaysKeyboard.add_line()
            self.weekDaysKeyboard.add_button(i, color=color)


class Bot:

    def __init__(self, vk):
        self.vk = vk

    def sendMsg(self, id, msg):
        self.vk.method('messages.send', {'user_id': id, 'random_id': get_random_id(), 'message': msg})

    def sendKeyboard(self, keyboard, id, msg):
        self.vk.method('messages.send', {'user_id': id, 'random_id': get_random_id(), 'message': msg,
                                         'keyboard': keyboard.get_keyboard()})


class SQL:

    def __init__(self):
        mysql_l = os.environ['MYSQL_LOGIN']
        mysql_p = os.environ["MYSQL_PASS"]
        self.connection = pymysql.connect(host='eu-cdbr-west-02.cleardb.net',
                                          user=mysql_l,
                                          password=mysql_p,
                                          db='heroku_0ccfbccd1823b55',
                                          cursorclass=DictCursor)

    def getUserGroup(self, id):
        with self.connection.cursor() as cursor:
            cursor.execute('''SELECT `thkruhm` FROM `users` WHERE (`vkid` = '%s')''' % id)
            row = cursor.fetchone()
            cursor.close()
            return row['thkruhm']

    def setUserGroup(self, id, group):
        usergroup = self.getUserGroup(id)
        with self.connection.cursor() as cursor:
            if len(usergroup) > 0:
                cursor.execute('''UPDATE `users` SET `thkruhm`='%s' WHERE `vkid`='%s' ''' % (group, id))
                cursor.close()
            else:
                cursor.execute(
                    '''INSERT INTO `users`(`vkid`, `thkruhm`, `sendStatus`) VALUES ('%s', '%s', 1)''' % (id, group))
                cursor.close()

    def sendStatus(self, id):
        with self.connection.cursor() as cursor:
            cursor.execute('''SELECT `sendStatus` FROM `users` WHERE (`vkid` = '%s')''' % id)
            row = cursor.fetchone()
            sendstatus = row['sendStatus']
            if sendStatus == 1:
                cursor.execute('''UPDATE `users` SET `sendStatus`=0 WHERE `vkid`='%s' ''' % id)
                cursor.close()
            else:
                cursor.execute('''UPDATE `users` SET `sendStatus`=1 WHERE `vkid`='%s' ''' % id)
                cursor.close()


class Changes:
    def __init__(self):
        pass

    def parseChanges(self):
        r = requests.get('http://www.tthk.ee/tunniplaani-muudatused/')
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.findChildren('table')
        changes = []
        for i in range(len(table)):
            my_table = table[i]
            rows = my_table.find_all('tr')
            for row in rows:
                change = []
                cells = row.find_all('td')
                for cell in cells:
                    if cell.text not in ["\xa0", "Kuupäev", "Rühm", "Tund", "Õpetaja", "Ruum"]:
                        data = cell.text
                        change.append(data)
                if change != []:
                    changes.append(change)
            else:
                continue
        return changes

    def convertChanges(self, i, date):
        changeList = []
        if date == True:
            if len(i) == 6:
                changeList.append(
                    f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]} \n👨‍🏫 Преподаватель: {i[4]}\nКабинет: {i[5]}\n")
            elif len(i) > 2 and i[3].lower() in "jääb ära":
                changeList.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 {i[2]}\n❌ Не состоится\n")
            elif len(i) > 4 and i[4].lower() in "jääb ära":
                changeList.append(f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n❌ Не состоится\n")
            elif len(i) > 4 and i[4].lower() in "söögivahetund":
                changeList.append(
                    f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]}\n ⏰ Урок: {i[3]}\n🆒 Обеденный перерыв\n")
            elif len(i) > 5 and i[5].lower() in "iseseisev töö kodus":
                changeList.append(
                    f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n🏠 Самостоятельная работа дома\n")
            elif len(i) > 5 and i[5].lower() in "iseseisev töö":
                changeList.append(
                    f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n📋 Самостоятельная работа\n")
            elif len(i) > 5 and (i[5].lower() == "" or i[5].lower() == " "):
                changeList.append(
                    f"🗓 {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n👨‍🏫 Преподаватель: {i[4]}\n")
            else:
                changeList.append(f"🗓 В {i[0]} Дата: {i[1]}\n🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n")
        elif date == False:
            if len(i) == 6:
                changeList.append(f"🦆 Группа: {i[2]} ⏰ Урок: {i[3]} \n👨‍🏫 Преподаватель: {i[4]}\nКабинет: {i[5]}\n")
            elif len(i) > 2 and i[3].lower() in "jääb ära":
                changeList.append(f"🦆 {i[2]}\n❌ Не состоится\n")
            elif len(i) > 4 and i[4].lower() in "jääb ära":
                changeList.append(f"🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n❌ Не состоится\n")
            elif len(i) > 4 and i[4].lower() in "söögivahetund":
                changeList.append(f"🦆 Группа: {i[2]}\n ⏰ Урок: {i[3]}\n🆒 Обеденный перерыв\n")
            elif len(i) > 5 and i[5].lower() in "iseseisev töö kodus":
                changeList.append(f"🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n🏠 Самостоятельная работа дома\n")
            elif len(i) > 5 and i[5].lower() in "iseseisev töö":
                changeList.append(f"🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n📋 Самостоятельная работа\n")
            elif len(i) > 5 and (i[5].lower() == "" or i[5].lower() == " "):
                changeList.append(f"🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n👨‍🏫 Преподаватель: {i[4]}\n")
            else:
                changeList.append(f"🦆 Группа: {i[2]} ⏰ Урок: {i[3]}\n")
        else:
            pass
        return changeList

    def makeChanges(self, data):
        tc = TimeCatcher()
        changes = self.parseChanges()
        changeList = []
        if data[-3:] in tc.getGroupList():
            for line in changes:
                if line[2].lower() in data.lower():
                    changeList = self.makeChanges(line, True)
            if len(changeList) > 0:
                refChanges = f"Для группы 🦆 {data} на данный момент следующие изменения в расписании:\n"
                for i in changeList:
                    refChanges += f"{i}\n"
                return refChanges
            elif len(changeList) == 0:
                return f"Для группы 🦆 {data} на данный момент изменений в расписании нет."
            else:
                pass
        elif data[-4:] == str(datetime.date.today().year):
            data = re.split(r':\s', data)
            data = data[1]
            for line in changes:
                if line[1] == data:
                    changeList = self.makeChanges(line, False)
            if len(changeList) > 0:
                refChanges = f"В учебном заведении на 🗓 {data} следующие изменения в расписании:\n"
                for i in changeList:
                    refChanges += f"{i}\n"
                return refChanges
            elif len(changeList) == 0:
                return f"В данный момент нет изменний в расписании на 🗓 {data}."
            else:
                pass
        elif data in tc.keyboardNumDays:
            for line in changes:
                if line[0] in data:
                    changeList = self.makeChanges(line, False)
            if len(changeList) > 0:
                refChanges = f"В учебном заведении на 🗓 {tc.dayOfWeek[data]} следующие изменения в расписании:\n"
                for i in forshow:
                    refChanges += f"{i}\n"
                return refChanges
            elif len(changeList) == 0:
                return f"В данный момент изменений в расписании нет на 🗓 {tc.dayOfWeek[data]}."
            else:
                pass
        else:
            pass


class COVID:
    def __init__(self):
        self.url = 'https://raw.githubusercontent.com/okestonia/koroonakaart/master/koroonakaart/src/data.json'

    def getData(self):
        data = urllib.request.urlopen(self.url).read()
        data = json.loads(data)
        covid = [data['confirmedCasesNumber'], data['testsAdministeredNumber'], data['recoveredNumber'],
                 data['deceasedNumber'], data['activeCasesNumber']]
        covid = f"🦠 COVID-19 в Эстонии:\n☣ {covid[0]} случаев заражения из 🧪 {covid[1]} тестов\n"
        f"😷 {covid[5]} болеет на данный момент и 💉 {covid[2]} выздоровели\n☠ {covid[3]} человек умерло.\n\n"
        f"⚠️В общественнах местах разрешено находится лишь вдвоём и держать дистанцию 2 метра от других людей. ⚠️"
        f"TTHK закрыт с 16 марта, в связи с чрезвычайным положением в Эстонской Республике."
        return covid


access_token = os.environ["ACCESS_TOKEN"]
server = Server(access_token)  # token will be here
server.start()
