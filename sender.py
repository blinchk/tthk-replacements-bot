from bot import *
import time

mysql_l = os.environ['MYSQL_LOGIN']
mysql_p = os.environ["MYSQL_PASS"]
access_token = os.environ["ACCESS_TOKEN"]
vk = vkapi.VkApi(token=access_token)

def sendeveryday():
    usergroup = openfromfile(usergroup)
    print("Запускаю рассылку:")
    print(time.strftime("%H:%M:%S"))
    for i in usergroup.keys():
        getmuudatused(usergroup[i], i)

while True:
    if time.strftime("%H:%M:%S", time.localtime()) == '00:57:00':
        sendeveryday()
    time.sleep(1.1)
    continue
