import sys
from random import shuffle, uniform, choice
from io import BytesIO
import requests
from PIL import Image
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QPixmap
from guessing_game import Ui_MainWindow

cities_list = [city.strip() for city in open('cities.txt', encoding='utf8').readlines()]


class GuessingGame(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        super().setupUi(self)
        self.PROFIT = 10
        shuffle(cities_list)
        self.cur_city = 0
        self.score = 0
        self.api_server = API()
        self.answerButton.clicked.connect(self.check_answer)
        self.nextButton.clicked.connect(self.change_slide)
        self.finishButton.clicked.connect(self.finish)
        self.scoreWidget.display(self.score)
        self.display_image(cities_list[self.cur_city])

    def check_answer(self):
        if self.answerField.text().lower() == cities_list[self.cur_city].lower():
            self.statusBar().showMessage('Правильный ответ!')
            self.score += self.PROFIT
            self.scoreWidget.display(self.score)
        else:
            self.statusBar().showMessage(f'Неверный ответ: правильный ответ - {cities_list[self.cur_city]}')
        self.answerField.setReadOnly(True)
        self.answerButton.setEnabled(False)
        QTimer.singleShot(700, self.change_slide)

    def change_slide(self):
        self.cur_city += 1
        if self.cur_city == len(cities_list):
            self.finish()
            return
        self.statusBar().showMessage('')
        self.answerField.setReadOnly(False)
        self.answerField.clear()
        self.answerButton.setEnabled(True)
        self.display_image(cities_list[self.cur_city])

    def finish(self):
        msg = QMessageBox()
        text = f'''Игра завершена! Ваша статистика:
Очков - {self.score};
Правильных ответов - {self.score // 10}/{self.cur_city};
Процент выполнения - {self.score / self.cur_city * 10 if self.cur_city else 0:.2F}%.'''
        if self.cur_city == len(cities_list):
            text += '\nПоздравляем с прохождением игры полностью! Такое ещё мало кому удавалось.'
        msg.setText(text)
        msg.exec_()
        self.close()

    def display_image(self, city):
        self.api_server.get_image(city)
        pixmap = QPixmap('tmp.png')
        self.mapWidget.setPixmap(pixmap)


class API:
    def __init__(self):
        self.geocoder_api_server = 'http://geocode-maps.yandex.ru/1.x/'
        self.geocoder_params = {'apikey': '40d1649f-0493-4b70-98ba-98533de7710b', 'format': 'json'}
        self.static_api_server = 'https://static-maps.yandex.ru/1.x/'

    def get_image(self, city):
        self.geocoder_params['geocode'] = city
        response = requests.get(self.geocoder_api_server, params=self.geocoder_params).json()
        toponym = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
        lon_1, lat_1 = map(float, toponym["boundedBy"]["Envelope"]["lowerCorner"].split())
        lon_2, lat_2 = map(float, toponym["boundedBy"]["Envelope"]["upperCorner"].split())
        lon, lat = uniform(lon_1, lon_2), uniform(lat_1, lat_2)
        map_params = {"ll": ",".join([str(lon), str(lat)]), "z": 14, "l": choice(["map", "sat"])}
        response = requests.get(self.static_api_server, params=map_params)
        Image.open(BytesIO(response.content)).save('tmp.png')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GuessingGame()
    window.show()
    sys.exit(app.exec_())
