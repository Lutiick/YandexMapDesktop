from PyQt5.QtWidgets import QWidget, QApplication, QPushButton
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import sys
import requests
from json import loads

WIDTH, HEIGHT = 650, 450
API_URL = 'https://static-maps.yandex.ru/1.x/'
GEO_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'
GEO_URL = 'https://geocode-maps.yandex.ru/1.x'
ORG_URL = 'https://search-maps.yandex.ru/v1/'
ORG_KEY = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.z = 14
        self.coords = [37.61, 55.75]
        self.type = 'map'
        self.mark = []
        self.zip = False
        self.initUi()
        self.setFocus()
        self.show()
    

    def initUi(self):
        self.setGeometry(250, 250, WIDTH, HEIGHT)
        self.setWindowTitle('Карта')

        self.imageLabel = QLabel(self)
        self.imageLabel.move(0, 0)
        self.imageLabel.resize(WIDTH, HEIGHT)

        self.image = QImage()
        self.setImage(self.loadImage())

        self.coordInputX = QLineEdit(self)
        self.coordInputX.resize(150, 20)
        self.coordInputX.move(0, HEIGHT - 20)
        self.coordInputX.setText(str(self.coords[0]))

        self.coordInputY = QLineEdit(self)
        self.coordInputY.resize(150, 20)
        self.coordInputY.move(150, HEIGHT - 20)
        self.coordInputY.setText(str(self.coords[1]))

        self.submitBtn = QPushButton('Ввод', self)
        self.submitBtn.resize(70, 20)
        self.submitBtn.move(300, HEIGHT-20)
        self.submitBtn.clicked.connect(self.moveTo)
        
        self.schemaBtn = QPushButton('Схема', self)
        self.schemaBtn.resize(70, 20)
        self.schemaBtn.move(WIDTH - 210, 0)
        self.schemaBtn.clicked.connect(self.changeType)
        self.schemaBtn.setStyleSheet("background-color: yellow")

        self.sputnikBtn = QPushButton('Спутник', self)
        self.sputnikBtn.resize(70, 20)
        self.sputnikBtn.move(WIDTH - 140, 0)
        self.sputnikBtn.clicked.connect(self.changeType)

        self.hybridBtn = QPushButton('Гибрид', self)
        self.hybridBtn.resize(70, 20)
        self.hybridBtn.move(WIDTH - 70, 0)
        self.hybridBtn.clicked.connect(self.changeType)

        self.searchInput = QLineEdit(self)
        self.searchInput.resize(200, 20)
        self.searchInput.move(20, 0)

        self.searchBtn = QPushButton('Искать', self)
        self.searchBtn.resize(70, 20)
        self.searchBtn.move(220, 0)
        self.searchBtn.clicked.connect(self.searchByName)

        self.dropSearchBtn = QPushButton('X', self)
        self.dropSearchBtn.resize(20, 20)
        self.dropSearchBtn.move(0, 0)
        self.dropSearchBtn.setStyleSheet('color: red')
        self.dropSearchBtn.clicked.connect(self.clearSearch)

        self.addressLabel = QLabel(self)
        self.addressLabel.setText('Адрес:')
        self.addressLabel.move(0, HEIGHT - 60)
        self.addressLabel.resize(50, 22)
        self.addressLabel.setStyleSheet('background:white; padding-left:3px')

        self.addressInput = QLineEdit(self)
        self.addressInput.resize(300, 20)
        self.addressInput.move(0, HEIGHT - 40)

        self.addressBtn = QPushButton('Ввод', self)
        self.addressBtn.resize(70, 20)
        self.addressBtn.move(300, HEIGHT - 40)
        self.addressBtn.clicked.connect(self.searchByName)

        self.zipBtn = QPushButton('Включить ZIP в адресе', self)
        self.zipBtn.resize(140, 20)
        self.zipBtn.move(40, HEIGHT - 60)
        self.zipBtn.clicked.connect(self.zipToggler)

    def zipToggler(self):
        if self.zip:
            self.zipBtn.setText('Включить ZIP в адресе')
            self.zip = False
        else:
            self.zipBtn.setText('Выключить ZIP в адресе')
            self.zip = True

    def searchByCoords(self):
        geocode = ','.join(map(str, self.coords))
        params = {
            'geocode': geocode,
            'apikey': GEO_KEY,
            'format': 'json'
        }

        r = requests.get(GEO_URL, params=params)
        r = loads(r.text)['response']
        r = r['GeoObjectCollection']['featureMember'][0]['GeoObject']
        name = r['name']
        address = r['metaDataProperty']['GeocoderMetaData']['text']
        if self.zip and 'postal_code' in r["metaDataProperty"]["GeocoderMetaData"]["Address"]:
            address += '; ZIP: ' + r["metaDataProperty"]["GeocoderMetaData"]["Address"]['postal_code']
        self.addressInput.setText(address)
        self.searchInput.setText(name)
        self.redrawMap()

    def searchByOrganisation(self):
        pass

    def searchByName(self):
        if self.sender() == self.addressBtn:
            geocode = self.addressInput.text()
        elif self.sender() == self.searchBtn:
            geocode = self.searchInput.text()
            
        params = {
            'geocode': geocode,
            'apikey': GEO_KEY,
            'format': 'json'
        }

        r = requests.get(GEO_URL, params=params)
        r = loads(r.text)['response']
        r = r['GeoObjectCollection']['featureMember'][0]['GeoObject']
        x, y = map(float, r['Point']['pos'].split())
        name = r['name']
        address = r['metaDataProperty']['GeocoderMetaData']['text']
        if self.zip and 'postal_code' in r["metaDataProperty"]["GeocoderMetaData"]["Address"]:
            address += '; ZIP: ' + r["metaDataProperty"]["GeocoderMetaData"]["Address"]['postal_code']
        self.addressInput.setText(address)
        self.searchInput.setText(name)
        self.coords = [x, y]
        self.mark = [x, y]
        self.redrawMap()
    
    def clearSearch(self):
        self.searchInput.clear()
        self.addressInput.clear()
        self.mark = []
        self.redrawMap()

    def setImage(self, image):
        self.image.loadFromData(image)
        self.imageLabel.setPixmap(QPixmap(self.image))
    
    def moveTo(self):
        self.coords = [float(self.coordInputX.text()), float(self.coordInputY.text())]
        self.setFocus()
        self.redrawMap()

    def mousePressEvent(self, e):
        x, y = e.x(), e.y()
        dx = 360 * (x - (WIDTH / 2)) / ((2 ** self.z * 256))
        dy = 270 * (y - (HEIGHT / 2)) / ((2 ** self.z * 256))

        self.coords[0] += dx
        self.coords[1] -= dy
        self.mark = self.coords.copy()
        if e.button() == Qt.LeftButton:
            self.searchByCoords()
        elif e.button() == Qt.RightButton:
            self.searchByOrganisation()
        if self.rect().contains(e.pos()):
            self.setFocus()

    def loadImage(self):
        params = {
            'l': self.type,
            'll': ",".join(map(str, self.coords)),
            'z': self.z,
            'size': ','.join((str(WIDTH), str(HEIGHT)))
        }
        if self.mark:
            params['pt'] = ",".join(map(str, self.mark)) + ',pm2rdm'
        r = requests.get(API_URL, params=params)
        return r.content

    def redrawMap(self):
        self.coordInputX.setText(str(self.coords[0]))
        self.coordInputY.setText(str(self.coords[1]))
        self.imageLabel.clear()
        self.setImage(self.loadImage())   

    def keyPressEvent(self, event):
        key = event.key()
        controls = [
            Qt.Key_Enter, Qt.Key_Right, Qt.Key_Left,
            Qt.Key_Up, Qt.Key_Down, Qt.Key_PageDown,
            Qt.Key_PageUp
        ]
        if key == Qt.Key_PageUp:
            self.z -= 1
        if key == Qt.Key_PageDown:
            self.z += 1
        if key == Qt.Key_Down:
            self.coords[1] -= 3 / 1.6 ** self.z
        if key == Qt.Key_Up:
            self.coords[1] += 3 / 1.6 ** self.z
        if key == Qt.Key_Left:
            self.coords[0] -= 3 / 1.6 ** self.z
        if key == Qt.Key_Right:
            self.coords[0] += 3 / 1.6 ** self.z
        if key == Qt.Key_Enter:
            self.coords[0] == float(self.coordInputX.text)
            self.coords[1] == float(self.coordInputY.text)
        if key in controls:
            self.redrawMap()

    def changeType(self):
        snd = self.sender()
        for b in (self.schemaBtn, self.hybridBtn, self.sputnikBtn):
            b.setStyleSheet("background-color: #CDCDCD")
        snd.setStyleSheet("background-color: yellow")
        if snd.text() == 'Спутник':
            self.type = 'sat'
        elif snd.text() == "Схема":
            self.type = 'map'
        elif snd.text() == 'Гибрид':
            self.type = 'sat,skl'

        self.redrawMap()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())