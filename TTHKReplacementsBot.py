import vk_api as vkapi
import requests
from bs4 import BeautifulSogFFup
from vk_api.longpoll import VkLongPoll, VkEventType
import json
output_rows = []
writeyourgroup = {}
usergroup = {}
# token : 4753258aa36e727b82691af62ec3425da7e41b82afc62cac1d0fbbf401cdaad837c069ec9ed4f5beb59c4

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
token = "4753258aa36e727b82691af62ec3425da7e41b82afc62cac1d0fbbf401cdaad837c069ec9ed4f5beb59c4"
vk = vkapi.VkApi(token=token)
values = []

usergroup = openfromfile(usergroup)

def parsepage():
    for i in range(len(table)):
        muudatused = []
        my_table = table[i]
        rows = my_table.find_all('tr')
        for row in rows:
            muudatus = []
            cells = row.find_all('td')
            for cell in cells:
                if cell.text not in ["\xa0", "Kuupäev", "Rühm", "Tund", "Õpetaja", "Ruum"]:
                    data = cell.text
                    muudatus.append(data)
            if muudatus != []:
                muudatused.append(muudatus)
            else:
                continue
    return muudatused

def getmuudatused(group, usergroup, user):
    forshow = []
    muudatused = parsepage()
    for i in muudatused:
        if group == i[2]:
            if i[4] == "jääb ära":
                forshow.append(f"{i[0]} Дата: {i[1]} Группа: {i[2]} Урок: {i[3]} не состоится")
#                forshow.append(f"{i[0]} Дата: {i[1]} Группа: {i[2]} Урок: {i[3]} Преподаватель: {i[4]}")
            else:
                forshow.append(f"{i[0]} Дата: {i[1]} Группа: {i[2]} Tund: {i[3]} Преподаватель: {i[4]} Кабинет: {i[5]}")
    if len(forshow) > 0:
        write_msg(event.user_id, event.random_id, f"Для группы {group} на данный момент следующие изменения в расписании:")
        for w in forshow:
            write_msg(event.user_id, event.random_id, w)
#    elif len(forshow) == 0:
#       write_msg(user, event.random_id,"Для вашей группы изменений в расписании нет. Подробнее: www.tthk.ee/tunniplaani-muudatused.")
longpoll = VkLongPoll(vk)
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            if event.text == "Начать" or event.text == "Указать группу":
                write_msg(event.user_id, event.random_id, "В какой группе вы находитесь?")
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
                write_msg(event.user_id, event.random_id, f"Вы указали, что Ваша группа: {usergroup[str(event.user_id)]}.")
            elif event.text.lower() == "изменения":
                group = usergroup[str(event.user_id)]
                lastmuudatused = getmuudatused(group, usergroup, event.user_id)
            else:
                write_msg(event.user_id, event.random_id, f"Данной команды не существует.")
                print(event.text)
