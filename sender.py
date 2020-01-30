from bot import openfromfile, getmuudatused, sendeveryday
import time
print("Sender launched")

def sendeveryday():
    usergroup = openfromfile(usergroup)
    print("Запускаю рассылку:")
    print(time.strftime("%H:%M:%S"))
    for i in usergroup.keys():
        getmuudatused(usergroup[i], i)

while True:
    if time.strftime("%H:%M:%S", time.localtime()) == '23:08:30':
        sendeveryday()
    time.sleep(1.1)
    continue
