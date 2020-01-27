import vk_api as vkapi
import requests
from bs4 import BeautifulSoup
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton
import json
output_rows = []
writeyourgroup = {}
usergroup = {}
# token : 4753258aa36e727b82691af62ec3425da7e41b82afc62cac1d0fbbf401cdaad837c069ec9ed4f5beb59c4
# клавиатура
keyboard = VkKeyboard(one_time=False, inline=False)

keyboard.add_button('Изменения моей группы', color=VkKeyboardColor.PRIMARY)
keyboard.add_button('Изменения всех групп', color=VkKeyboardColor.DEFAULT)
keyboard.add_line()  # Переход на вторую строку
keyboard.add_button('В какой я группе?', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('Изменить группу', color=VkKeyboardColor.NEGATIVE)


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

token = "4753258aa36e727b82691af62ec3425da7e41b82afc62cac1d0fbbf401cdaad837c069ec9ed4f5beb59c4"
vk = vkapi.VkApi(token=token)


DayOfWeek = {'E': 'Понедельник',
            'T': 'Вторник',
            'K': 'Среда',
            'N': 'Четверг',
            'R': 'Пятница',
            'L': 'Суббота',
            'P': "Воскресенье"}


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
            print(muudatused)
            if muudatus != []:
                muudatused.append(muudatus)
        else:
            continue
    print(muudatused)
    return muudatused

def getmuudatused(setgroup, usergroup, user):
    forshow = []
    muudatused = parsepage(table)
    print(muudatused)
    for i in muudatused:
        if setgroup in i[2]:
            if i[4].lower() == "jääb ära":
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} не состоится")
            elif i[4].lower() == "söögivahetund":
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} обеденный перерыв")
            elif i[5].lower() == "iseseisev töö kodus":
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} самостоятельная работа дома")
            else:
                forshow.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} Преподаватель: {i[4]} Кабинет: {i[5]}")
    if len(forshow) > 0:
        write_msg(event.user_id, event.random_id, f"Для группы {setgroup} на данный момент следующие изменения в расписании:")
        for w in forshow:
            write_msg(event.user_id, event.random_id, w)
    elif len(forshow) == 0:
        write_msg(user, event.random_id,"Для вашей группы изменений в расписании нет. Подробнее: www.tthk.ee/tunniplaani-muudatused.")

def getmuudatusedall(user):
    forshow = []
    forshowall = []
    muudatused = parsepage(table)
    print(muudatused)
    for i in muudatused:
        if i[4].lower() == "jääb ära":
            forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} не состоится")
        elif i[4].lower() == "söögivahetund":
            forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} обеденный перерыв")
        elif i[5].lower() == "iseseisev töö kodus":
            forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} самостоятельная работа дома")
        else:
            forshowall.append(f"{DayOfWeek[i[0]]} {i[1]} Группа: {i[2]} Урок: {i[3]} Преподаватель: {i[4]} Кабинет: {i[5]}")
    if len(forshow) > 0:
        write_msg(event.user_id, event.random_id, f"В учебном заведении на данный момент следующие изменения в расписании:")
        for w in forshow:
            write_msg(event.user_id, event.random_id, w)
    elif len(forshow) == 0:
        write_msg(user, event.random_id,"В данный момент изменений в расписании нет. Подробнее: www.tthk.ee/tunniplaani-muudatused.")


longpoll = VkLongPoll(vk)
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            if event.text.lower() == "начать":
                usergroup = openfromfile(usergroup)
                send_keyboard(event.peer_id, event.random_id, "Выберите вариант из клаиватуры ниже.")
                print(usergroup.keys())
                if str(event.user_id) not in usergroup.keys():
                    write_msg(event.user_id, event.random_id, "У вас не указан код группы.")
            elif event.text.lower() == "указать группу" or event.text.lower() == "изменить группу":
                write_msg(event.user_id, event.random_id, "В какой группе вы находитесь?\nУкажите код вашей группы: ")
                writeyourgroup[event.user_id] = 1
            elif event.text[-3:].lower() in ['v19', 'v18', 'v17', 'e19', 'e18', 'e17'] and writeyourgroup[event.user_id] == 1:
                group = event.text
                print(group)
                usergroup[str(event.user_id)] = group
                write_msg(event.user_id, event.random_id, f"Вы указали, что Ваша группа: {usergroup[str(event.user_id)]}.")
                print(usergroup)
                writeyourgroup[event.user_id] = 0
                usergroup = updatefile(usergroup)
            elif event.text.lower() == "в какой я группе?":
                if str(event.user_id) not in usergroup.keys():
                    write_msg(event.user_id, event.random_id, "У вас не указан код группы.")
                    pass
                write_msg(event.user_id, event.random_id, f"Вы указали, что Ваша группа: {usergroup[str(event.user_id)]}.")
            elif event.text.lower() == "изменения моей группы":
                setgroup = usergroup[str(event.user_id)]
                lastmuudatused = getmuudatused(setgroup, usergroup, event.user_id)
            elif event.text.lower() == "изменения всех групп":
                newmuudatused = getmuudatusedall(event.user_id)
            else:
                write_msg(event.user_id, event.random_id, f"Данной команды не существует.")
                print(event.text)
