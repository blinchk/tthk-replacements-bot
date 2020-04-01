import json
import urllib.request


def getdata():
    url = 'https://raw.githubusercontent.com/okestonia/koroonakaart/master/koroonakaart/src/data.json'
    data = urllib.request.urlopen(url).read()
    data = json.loads(data)
    covid = [data['confirmedCasesNumber'], data['testsAdministeredNumber'], data['recoveredNumber'],
             data['deceasedNumber'], data['activeCasesNumber']]
    print(covid)
    return covid
