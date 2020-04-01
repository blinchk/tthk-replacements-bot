import urllib.request, json

class COVIDParser:
    def __init__(self):
        url = 'https://raw.githubusercontent.com/okestonia/koroonakaart/master/koroonakaart/src/data.json'
        data = urllib.request.urlopen(url).read()
        self.data = json.loads(data)
    def getdata():
        global data
        covid = [data['confirmedCasesNumber'], data['testsAdministeredNumber'], data['recoveredNumber'], data['deceasedNumber'], data['activeCasesNumber']]
        print(covid)
        return covid
