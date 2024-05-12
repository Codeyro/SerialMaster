# Импортируем библиотеки
import sys
import tkinter.filedialog as fd
import serial
import serial.tools.list_ports
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QObject, QThread, pyqtSignal
import design


# Задаём переменные
portList = None
ports = None
ser = serial.Serial
portActive = None
speedActive = 300
DBActive = 5
parityActive = 'N'
SBActive = 1


# Устанавливаем функции
def changeSpeed(s):
    global speedActive
    speedActive = s
    speedActive = int(speedActive)
    print(speedActive)


def changeDB(s):
    global DBActive
    DBActive = int(s)


def changeParity(s):
    global parityActive
    parityActive = s
    if parityActive == 'Нет':
        parityActive = 'N'
    elif parityActive == 'Нечётный':
        parityActive = 'O'
    elif parityActive == 'Чётный':
        parityActive = 'P'
    elif parityActive == 'Метка':
        parityActive = 'L'
    elif parityActive == 'Пробел':
        parityActive = 'S'


def changePort(s):
    global portActive
    portActive = s


def changeSB(s):
    global SBActive
    SBActive = s


# Создаём классы
class MainWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):  # Это нужно для доступа к переменным, методам и т.д. в файле design.py
        super().__init__()
        self.worker = UpdatePorts()
        self.thread = QThread()
        self.second_window = None
        self.output = None
        self.dragPos = None
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.comboBox.currentTextChanged.connect(changePort)
        self.comboBox_2.currentTextChanged.connect(changeSpeed)
        self.comboBox_3.currentTextChanged.connect(changeDB)
        self.comboBox_4.currentTextChanged.connect(changeParity)
        self.comboBox_5.currentTextChanged.connect(changeSB)
        self.connectButton.clicked.connect(self.connectToPort)
        self.clearButton.clicked.connect(self.clearOutput)
        self.copyButton.clicked.connect(self.copyOutput)
        self.saveButton.clicked.connect(self.saveOutput)
        self.helpButton.pressed.connect(self.updatePorts)
        self.sendButton.clicked.connect(self.sendData)
        self.homeButton.clicked.connect(self.home)
        self.homeButton_2.clicked.connect(self.home)
        self.aboutButton.clicked.connect(self.about)
        self.aboutButton_2.clicked.connect(self.about)
        self.settingsButton.clicked.connect(self.settings)
        self.settingsButton_2.clicked.connect(self.settings)
        self.stackedWidget.setCurrentIndex(0)
        self.settingsButton.hide()
        self.settingsButton_2.hide()
        self.newButton.hide()
        self.sendButton.setDisabled(True)
        self.updatePorts()

    def update(self):
        self.worker.moveToThread(self.thread)
        self.thread.customEvent(self.updatePorts())
        self.thread.start()

    def updatePorts(self):
        global ports
        global portList
        ports = serial.tools.list_ports.comports()
        portsList = []
        for port in ports:
            portsList.append(port.device)

        self.comboBox.clear()

        if len(portsList) > 0:
            self.comboBox.addItems(portsList)
            self.connectButton.setEnabled(True)
        else:
            self.comboBox.addItems('Портов не найдено')
            self.connectButton.setDisabled(True)

    def connectToPort(self, checked):
        global portActive
        global ser
        if checked == 1:
            self.connectButton.setText('Подключение...')

            self.comboBox.setDisabled(True)
            self.comboBox_2.setDisabled(True)
            self.comboBox_3.setDisabled(True)
            self.comboBox_4.setDisabled(True)
            self.comboBox_5.setDisabled(True)

            ser = serial.Serial(portActive, baudrate=speedActive, bytesize=DBActive, parity=parityActive,
                                stopbits=SBActive)
            self.sendButton.setEnabled(True)
            self.output.appendPlainText('Успешно подключено к последовательному порту!')
            self.connectButton.setText('Отключиться')
        else:
            ser.close()
            ser = None
            self.sendButton.setDisabled(True)
            self.output.appendPlainText('Успешно отключено от последовательного порта!')
            self.output.appendPlainText('')
            self.connectButton.setText('Подключиться')

            self.comboBox.setEnabled(True)
            self.comboBox_2.setEnabled(True)
            self.comboBox_3.setEnabled(True)
            self.comboBox_4.setEnabled(True)
            self.comboBox_5.setEnabled(True)

    def clearOutput(self):
        self.output.clear()
        self.output.appendPlainText('Serial master Copyright © 2023')
        self.output.appendPlainText('Все права защищены и принадлежат Codey.ro!')
        self.output.appendPlainText('')

    def copyOutput(self):
        self.output.selectAll()
        self.output.copy()

    def saveOutput(self):
        filetypes = (("Текстовый файл", "*.txt"), ("Любой", "*"))
        filename = fd.asksaveasfilename(title='Сохранить вывод...', initialfile='SM Output', initialdir='/',
                                        filetypes=filetypes)
        if filename:
            filename = filename + '.txt'
            file = open(filename, 'w')
            file.write(self.output.toPlainText())
            file.close()

    def sendData(self):
        global ser
        data = self.lineEdit.text()
        ser.write(data.encode())
        self.output.appendPlainText(self.lineEdit.text())
        self.lineEdit.clear()

    def home(self):
        self.stackedWidget.setCurrentIndex(0)

    def about(self):
        self.stackedWidget.setCurrentIndex(1)

    def settings(self):
        self.stackedWidget.setCurrentIndex(2)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
        self.dragPos = event.globalPosition().toPoint()
        event.accept()


class UpdatePorts(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    @staticmethod
    def run():
        global ports
        global portList
        ports = serial.tools.list_ports.comports()
        portsList = []
        for port in ports:
            portsList.append(port.device)


# Основная программа
if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    style = open('styles/style_dark.css', 'r')  # Открываем файл CSS
    app.setStyleSheet(style.read())  # Задаём CSS приложению
    window.show()  # Показываем окно
    app.exec()  # и запускаем приложение
