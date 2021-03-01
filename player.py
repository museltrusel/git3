import sys
from PyQt5 import uic
from PyQt5 import QtCore, QtMultimedia
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QDialog, QMessageBox
import sqlite3
import hashlib


class RegistrationWindow(QMainWindow, QDialog):
    def __init__(self):
        super().__init__()

        uic.loadUi('ui/registration.ui', self)

        self.setWindowTitle('вход')
        self.initLoginUi()
        self.initRegistrationUi()

    def loginCheck(self):

        con = sqlite3.connect('data/users.db')

        cursor = con.cursor()
        name = self.lineEdit.text()
        password = self.lineEdit_2.text()
        passw = bytes(password, 'utf-8')
        sha = hashlib.sha1(passw).hexdigest()

        if not name or not password:
            QMessageBox.information(self, 'Внимание!', 'Вы не заполнили все поля.')
            return

        con.commit()
        result = cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                                (name, sha))

        if len(result.fetchall()):
            self.openMainWindow()

        else:
            QMessageBox.information(self, 'Внимание!', 'Неправильное имя пользователя или пароль!')
            return

    def registrationCheck(self):

        con = sqlite3.connect('data/users.db')
        cursor = con.cursor()

        name = self.lineEdit.text()
        password = self.lineEdit_2.text()
        passw = bytes(password, 'utf-8')
        sha = hashlib.sha1(passw).hexdigest()

        if not name or not password:
            QMessageBox.information(self, 'Внимание!', 'Вы не заполнили все поля.')
            return

        result = cursor.execute("SELECT * FROM users WHERE username = ?", (name,))

        if result.fetchall():
            QMessageBox.information(self, 'Внимание!', 'Пользоватеть с таким именем уже зарегистрирован.')

        else:
            cursor.execute("INSERT INTO USERS VALUES(?, ?)",
                           (name, sha))

            con.commit()
            self.openMainWindow()

    def initLoginUi(self):

        self.pushButton.clicked.connect(self.loginCheck)

    def initRegistrationUi(self):

        self.pushButton_2.clicked.connect(self.registrationCheck)

    def openMainWindow(self):

        RegistrationWindow.close(self)
        self.wind = MyWidget()
        self.wind.show()


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        # загружаем файл
        uic.loadUi('ui/player1.ui', self)


        self.name_file = 'music/Барбарики - Барбарики.mp3'
        self.load_mp3(self.name_file)

        # подключаем кнопочки play, stop, return

        self.play.clicked.connect(self.player.play)
        self.pause.clicked.connect(self.player.pause)
        self.return_2.clicked.connect(self.player.stop)
        self.parameter = None

        # эта кнопочка для поиска нужной песенки

        self.find_mus.clicked.connect(self.find)

        # радио батоны для поиска, каждому соответствует своя ф-я

        self.radioButton_singer.toggled.connect(self.find_singer)
        self.radioButton_name.toggled.connect(self.find_name)
        self.radioButton_genre.toggled.connect(self.find_genre)
        # Подключение к БД
        con = sqlite3.connect("data/song.db")

        # Создание курсора
        self.cur = con.cursor()

        result = self.cur.execute("""SELECT things.name FROM things
                    WHERE True""").fetchall()
        print(self.cur.execute("""SELECT place.name_place FROM place""").fetchall())

        # тупа переменные
        # размеры кнопочки
        self.a = 390
        self.b = 20

        # список где будут кнопочки лежать

        self.result = list()

        # координаты кнопочек

        self.x = 10
        self.y = 135

        for elem in result:
            # подключаемся ко 2-ой бд
            file_bd = sqlite3.connect("data/files.db")
            car = file_bd.cursor()

            elem = str(*elem)

            # по названию песни находим файл который ей соответсвует
            print(elem)
            name = car.execute("""SELECT name_file FROM file
                    WHERE name = ? """, (elem,)).fetchone()
            print(name)

            # создаю кнопочку с песенкой
            bt = QPushButton(str(*name), self)

            bt.move(self.x, self.y)
            bt.resize(self.a, self.b)

            self.name_file ='music/' + str(*name) + '.mp3'

            bt.clicked.connect(self.play_mus)

            # заношу кнопчку и имя файла который ей соответсвует

            self.result.append([bt, self.name_file, elem])
            # меняю координаты высоты
            self.y += 25

    def load_mp3(self, filename):

        # эта штука в материалах урока
        # QT. Установка дополнительных компонентов. PyQTGraph
        # там написано как эта штука работает

        media = QtCore.QUrl.fromLocalFile(filename)
        content = QtMultimedia.QMediaContent(media)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(content)

    def play_mus(self):
        # узнаем какая кнопочка активировала

        sender = self.sender()

        # в матрице кнопочек находим кнопочку
        # в списке где лежит кнопочка находится имя файла который ей соответсвует
        k = 0
        for i in self.result:
            if sender in i:
                self.name_file = i[1]
                break
            else:
                k += 1

        # загружаем файл

        self.load_mp3(self.name_file)

        # подключаем кнопочки play, stop, return

        self.play.clicked.connect(self.player.play)
        self.pause.clicked.connect(self.player.pause)
        self.return_2.clicked.connect(self.player.stop)

        # узнаем жанр и исполнителя трека

        genre = self.cur.execute("""SELECT things.id_type FROM things
                            WHERE things.name = ? """, (self.result[k][2],)).fetchone()
        singer = self.cur.execute("""SELECT things.id_place FROM things
                            WHERE things.name = ? """, (self.result[k][2],)).fetchone()

        genre = self.cur.execute("""SELECT type.name FROM type
                                    WHERE type.id = ? """, (*genre,)).fetchone()
        singer = self.cur.execute("""SELECT place.name_place FROM place
                                    WHERE place.id = ? """, (*singer,)).fetchone()

        # загружаем данные о треке в проигрыватель

        self.label_genre.setText(*genre)
        self.label_singer.setText(*singer)
        self.label_song.setText(self.result[k][2])

    def start_screen(self):
        for i in self.result:
            i[0].deleteLater()

        result = self.cur.execute("""SELECT things.name FROM things""").fetchall()
        self.result = list()
        self.y = 135

        for elem in result:
            # подключаемся ко 2-ой бд
            file_bd = sqlite3.connect("data/files.db")
            car = file_bd.cursor()

            elem = str(*elem)

            # по названию песни находим файл который ей соответсвует

            name = car.execute("""SELECT name_file FROM file
                    WHERE name = ? """, (elem,)).fetchone()

            # создаю кнопочку с песенкой
            bt = QPushButton(str(*name), self)

            bt.move(self.x, self.y)
            bt.resize(self.a, self.b)

            self.name_file = 'music/' + str(*name) + '.mp3'

            bt.clicked.connect(self.play_mus)
            bt.show()

            # заношу кнопчку и имя файла который ей соответсвует

            self.result.append([bt, self.name_file, elem])
            # меняю координаты высоты
            self.y += 25

    def find(self):

        # поиск по исполнителю

        if self.parameter == 1:

            # устраненение сообщения об ошибке

            self.error.setText('')
            self.request = self.linefind.text().lower()
            singers = self.cur.execute("""SELECT place.name_place FROM place""").fetchall()
            flag = False
            for i in singers:
                if self.request in i:
                    flag = True
                    break
            if flag:
                self.error.setText('')
                for i in self.result:
                    i[0].deleteLater()

                singer = self.cur.execute("""SELECT s.id FROM place AS s
                                    WHERE s.name_place = ? """, (self.request,)).fetchone()

                singer = self.cur.execute("""SELECT s.name FROM things AS s
                                                    WHERE s.id_place = ? """, (*singer,)).fetchall()
                self.y = 135
                self.result = []

                for elem in singer:
                    # подключаемся ко 2-ой бд
                    file_bd = sqlite3.connect("data/files.db")
                    car = file_bd.cursor()

                    elem = str(*elem)

                    # по названию песни находим файл который ей соответсвует

                    name = car.execute("""SELECT name_file FROM file
                            WHERE name = ? """, (elem,)).fetchone()

                    # создаю кнопочку с песенкой
                    bt = QPushButton(str(*name), self)

                    bt.move(self.x, self.y)
                    bt.resize(self.a, self.b)

                    self.name_file = 'music/' + str(*name) + '.mp3'

                    bt.clicked.connect(self.play_mus)
                    bt.show()

                    # заношу кнопчку и имя файла который ей соответсвует

                    self.result.append([bt, self.name_file, elem])
                    # меняю координаты высоты
                    self.y += 25

            else:
                self.error.setText('ничего не найдено')
                self.start_screen()

        # поиск по жанру

        elif self.parameter == 2:
            # устраненение сообщения об ошибке
            self.error.setText('')

            self.request = self.linefind.text()

            singers = self.cur.execute("""SELECT type.name FROM type""").fetchall()
            flag = False

            for i in singers:
                if self.request in i:
                    flag = True
                    break
            if flag:

                self.error.setText('')

                for i in self.result:
                    i[0].deleteLater()

                genre = self.cur.execute("""SELECT t.id FROM type AS t
                                                WHERE t.name = ? """, (self.request,)).fetchone()

                genre = self.cur.execute("""SELECT s.name FROM things AS s
                                                                WHERE s.id_type = ? """, (*genre,)).fetchall()
                self.y = 135
                self.result = []
                for elem in genre:
                    # подключаемся ко 2-ой бд
                    file_bd = sqlite3.connect("data/files.db")
                    car = file_bd.cursor()

                    elem = str(*elem)

                    # по названию песни находим файл который ей соответсвует

                    name = car.execute("""SELECT name_file FROM file
                                        WHERE name = ? """, (elem,)).fetchone()

                    # создаю кнопочку с песенкой
                    bt = QPushButton(str(*name), self)
                    bt.move(self.x, self.y)
                    bt.resize(self.a, self.b)
                    self.name_file = 'music/' + str(*name) + '.mp3'
                    bt.clicked.connect(self.play_mus)
                    bt.show()
                    # заношу кнопчку и имя файла который ей соответсвует
                    self.result.append([bt, self.name_file, elem])
                    # меняю координаты высоты
                    self.y += 25

            else:
                self.error.setText('ничего не найдено')
                self.start_screen()

        # поиск по названию
        elif self.parameter == 3:
            # устраненение сообщения об ошибке
            self.error.setText('')

            self.request = self.linefind.text()

            singers = self.cur.execute("""SELECT things.name FROM things""").fetchall()

            flag = False

            for i in singers:
                if self.request in i:
                    flag = True
                    break

            if flag:

                self.error.setText('')
                for i in self.result:
                    i[0].deleteLater()

                genre = [self.request]

                self.y = 135

                self.result = []

                for elem in genre:
                    # подключаемся ко 2-ой бд
                    file_bd = sqlite3.connect("data/files.db")
                    car = file_bd.cursor()
                    elem = str(elem)

                    # по названию песни находим файл который ей соответсвует

                    name = car.execute("""SELECT name_file FROM file
                                                    WHERE name = ? """, (elem,)).fetchone()
                    # создаю кнопочку с песенкой
                    bt = QPushButton(str(*name), self)
                    bt.move(self.x, self.y)
                    bt.resize(self.a, self.b)
                    self.name_file = 'music/' + str(*name) + '.mp3'
                    bt.clicked.connect(self.play_mus)
                    bt.show()
                    # заношу кнопчку и имя файла который ей соответсвует
                    self.result.append([bt, self.name_file, elem])
                    # меняю координаты высоты
                    self.y += 25

            else:
                self.error.setText('ничего не найдено')
                self.start_screen()
        # параметр не указан
        else:
            # выыод сообщения об ошибке
            self.error.setText('вы не указали параметр поиска')

    def find_singer(self):
        self.parameter = 1

    def find_name(self):
        self.parameter = 3

    def find_genre(self):
        self.parameter = 2


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RegistrationWindow()
    ex.show()
    sys.exit(app.exec())
