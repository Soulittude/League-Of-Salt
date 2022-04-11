from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
import sys
import Ui_MainWindow
import requests
import json
import ast

with open('headers.json') as json_file:
    headerlar = json.load(json_file)

with open('queries.json') as json_dosyasi:
    url = json.load(json_dosyasi)

class SihirdarClass:
    def __init__(self, name, region):
        self.profil(name, region)
        id = self.id
        accountId = self.accountId
        print(self.lig_winrate(id,region))

    def profil(self, name, region):
        sihirdar = url["sihirdar"].format(reg = region, summonerName=name)
        sihirdar_req = requests.get(url=sihirdar, headers=headerlar)
        profil = sihirdar_req.json()

        self.id= profil["id"]
        self.accountId = profil["accountId"]

        self.nick = name
        self.level = profil['summonerLevel']
        self.resim = url['profil_resmi'].format(res = profil['profileIconId']) + ".png"

    def lig_winrate(self, id, region):
        lig = url["lig"].format(reg=region, encryptedSummonerId=id)
        lig_req = requests.get(url=lig, headers=headerlar)
        lig_bilgisi = lig_req.json()

        try:
            lig_bilgisi[0]['queueType']
        except IndexError:
            return("Unranked")
            
        if lig_bilgisi[0]['queueType'] == "RANKED_SOLO_5x5":
            self.lig = lig_bilgisi[0]['tier']
            self.kume = lig_bilgisi[0]['rank']
            self.lp = lig_bilgisi[0]['leaguePoints']
            self.lig = print("{lig} {kume}({lp}lp)".format(lig=self.lig, kume = self.kume, lp = self.lp))
            self.winrate = int(100/(lig_bilgisi[0]['wins'] + lig_bilgisi[0]['losses']) * lig_bilgisi[0]['wins'])
            return("%{winrate} ({mac_sayisi} Maç)".format(winrate = self.winrate, mac_sayisi=lig_bilgisi[0]['wins'] + lig_bilgisi[0]['losses']))

        elif lig_bilgisi[0]['queueType'] == "RANKED_FLEX_SR":
            self.lig = lig_bilgisi[1]['tier']
            self.kume = lig_bilgisi[1]['rank']
            self.lp = lig_bilgisi[1]['leaguePoints']
            self.lig = print("{lig} {kume}({lp} lp)".format(lig=self.lig, kume = self.kume, lp = self.lp))
            self.winrate = int(100/(lig_bilgisi[1]['wins'] + lig_bilgisi[1]['losses']) * lig_bilgisi[1]['wins'])
            
            return("%{winrate} ({mac_sayisi} Maç)".format(winrate = self.winrate, mac_sayisi=lig_bilgisi[1]['wins'] + lig_bilgisi[1]['losses']))

class Pencere(QMainWindow, Ui_MainWindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(330, 80)
        self.ara.clicked.connect(self._id_bul)

    def _id_bul(self):
        sihirdar = url["sihirdar"].format(reg = self.region.currentText(), summonerName=self.nick.text())
        sihirdar_req = requests.get(url=sihirdar, headers=headerlar)
        profil = sihirdar_req.json()
        try:
            self.id = profil["id"]
            self.accountId = profil["accountId"]
            self._sihirdar_ara()
            return

        except KeyError:
            return(print("Böyle bir sihirdar bulunamadı. Lütfen nicki ve bölgeyi kontrol edin!"))

    def _sihirdar_ara(self):
        nick = self.nick.text()
        nick = nick.replace(" ", "%20")
        region = self.region.currentText()
        oyuncu = SihirdarClass(nick, region)
        self._aktif_mac()
        
    def _aktif_mac(self):
        aktif_mac = url["aktif_mac"].format(reg=self.region.currentText(), encryptedSummonerId=self.id)
        aktif_mac = requests.get(url=aktif_mac, headers=headerlar)

        aktif_mac = aktif_mac.json()
        aktif_mac = str(aktif_mac)
        ilk = 129
        son = aktif_mac.rfind("observers") - 3
        aktif_mac = aktif_mac[ilk:son]

        try:
            aktif_mac = ast.literal_eval(aktif_mac)
            sihirdar_id_list = []
            for sihirdar_numarasi in range(0,10):
                sihirdar_id_list.append(aktif_mac[sihirdar_numarasi]['summonerId'])
                print(sihirdar_id_list[sihirdar_numarasi])
                
        except SyntaxError:
            return(print("Bu sihirdar şuanda bir maçta değil!"))
            
        
app = QApplication(sys.argv)
pencere = Pencere()
pencere.show()
sys.exit(app.exec_())