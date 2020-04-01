import urllib.request, json

class COVIDParser:
    def __init__(self):
        url = 'https://raw.githubusercontent.com/okestonia/koroonakaart/master/koroonakaart/src/data.json'
        data = urllib.request.urlopen(url).read()
        self.data = json.loads(data)
    def getdata(self):
        covid = [self.data['confirmedCasesNumber'], self.data['testsAdministeredNumber'], self.data['recoveredNumber'], self.data['deceasedNumber'], self.data['activeCasesNumber']]
        print(covid)
        return covid
