
import sys
import psycopg2
import re
from Dane import klata, podciagniecia, dip
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLineEdit, QLabel, QPushButton, QWidget, QCheckBox, QVBoxLayout, QTabWidget, QFrame
from PyQt6.QtGui import QIntValidator

nazwa_uzytkownika = ""

class Aplikacja(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ek_rej = Rejestracja(self)
        self.ek_rej.show()

    def ek_log(self):
        self.ek_rej.hide()
        self.ek_log = Logowanie(self)
        self.ek_log.show()

    def ek_dz(self):
        self.ek_log.hide()
        self.ek_dz = Działanie()
        self.ek_dz.show()

class Rejestracja(QMainWindow):
    def __init__(self, aplikacja):
        super().__init__()
        self.aplikacja = aplikacja
        self.setFixedSize(350, 300)
        self.setWindowTitle('Dawaj byq')
        self.pola()
        self.komunikaty()
        self.przyciski()

    def pola(self):  # Pola tekstowych
        self.nu = QLineEdit('', self)
        self.h = QLineEdit('', self)
        self.ph = QLineEdit('', self)

        self.label_nu = QLabel("Nazwa użytkownika: ", self)
        self.label_h = QLabel("Hasło: ", self)
        self.label_ph = QLabel("Powtórz hasło: ", self)

        self.label_nu.move(10, 24)
        self.label_h.move(10, 68)
        self.label_ph.move(10, 108)
        self.label_nu.setWordWrap(True)
        self.h.setEchoMode(QLineEdit.EchoMode.Password)
        self.ph.setEchoMode(QLineEdit.EchoMode.Password)

        list1 = [self.nu, self.h, self.ph, ]  # lista z polami do wpisania
        list2 = [self.label_nu, self.label_h, self.label_ph, ]  # lista z podpisami dla list 1
        ps = -10  # Położenie startowe

        for i in list1:
            ps += 40
            i.setFixedWidth(200)
            i.setFixedHeight(25)
            i.move(100, ps)

    def przyciski(self):        #Przyciski

        self.cbx = QCheckBox('Wyświetl hasło', self)
        self.cbx.move(100, 135)

        self.Rej = QPushButton('Zarejestruj się', self)
        self.Rej.move(-3, 180)
        self.Rej.setFixedSize(355, 25)
        self.Rej.setEnabled(False)

        linia = QFrame(self)
        linia.setGeometry(0, 238, 400, 5)
        linia.setStyleSheet("background-color: silver;")

        self.dalej = QLabel("Posiadasz już konto ? Zaloguj się.", self)
        self.dalej.move(90, 240)
        self.dalej.setFixedWidth(350)

        self.p_dalej = QPushButton('Przejdź dalej', self)
        self.p_dalej.move(-3, 270)
        self.p_dalej.setFixedSize(355, 25)

        self.cbx.clicked.connect(self.pas)
        self.Rej.clicked.connect(self.dodanie)
        self.p_dalej.clicked.connect(self.aplikacja.ek_log)

    def komunikaty(self):       # Komunikaty
        self.zln = QLabel('Nazwa użytkownika ma mieć od 1 do 12 znaków.', self)
        self.zlh = QLabel('Hasło musi zawierać od 8 do 12 znaków, w tym co najmniej jedną dużą literę.', self)
        self.zlhp = QLabel('Podane hasła muszą być identycznę', self)
        self.ui = QLabel('Użytkownik o podanej nazwie już istnieje', self)

        list1 = (self.zlhp, self.zln, self.zlh, self.ui)
        for i in list1:
            i.hide()
            i.setFixedWidth(340)
            i.setWordWrap(True)
            i.move(10, 205)

        self.h.textChanged.connect(self.spr)
        self.ph.textChanged.connect(self.spr)
        self.nu.textChanged.connect(self.spr)

    def pas(self):  # Odpowiada za wyświetlanie hasła
        if self.cbx.isChecked():
            self.h.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ph.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.h.setEchoMode(QLineEdit.EchoMode.Password)
            self.ph.setEchoMode(QLineEdit.EchoMode.Password)

    def spr(self):            # Warunki dla hasła i nazwy użytkownika

        spr_nazwy = "SELECT * FROM users WHERE login = %s"
        usera = self.polaczenie(spr_nazwy, self.nu.text())

        if not re.match(r'^.{1,12}$',self.nu.text()):
            self.zlhp.hide()
            self.zlh.hide()
            self.ui.hide()
            self.zln.show()
            self.Rej.setEnabled(False)
        elif usera:
            self.zln.hide()
            self.zlh.hide()
            self.zlhp.hide()
            self.ui.show()
            self.Rej.setEnabled(False)
        else:
            if not re.match(r'^(?=.*[A-Z]).{8,12}$', self.h.text()):
                self.zlh.show()
                self.zlhp.hide()
                self.zln.hide()
                self.ui.hide()
                self.Rej.setEnabled(False)
            elif self.h.text() != self.ph.text():
                self.zlhp.show()
                self.zlh.hide()
                self.zln.hide()
                self.ui.hide()
                self.Rej.setEnabled(False)
            else:
                self.zlhp.hide()
                self.zlh.hide()
                self.zln.hide()
                self.ui.hide()
                self.Rej.setEnabled(True)

    def dodanie(self): # Dodaje użytkownika do bazy danych
            zapytanie = "INSERT INTO users (login, haslo) VALUES (%s, %s)"
            self.polaczenie(zapytanie, self.nu.text(), self.h.text())

    def polaczenie(self, zapytanie, *args): # Połączenie do bazy danych

        self.conn = psycopg2.connect(
            dbname="Users",
            user="michal",
            password="mko1nji2",
            host="localhost"
        )
        self.cursor = self.conn.cursor()

        if zapytanie.startswith("SELECT"):
            self.cursor.execute(zapytanie, args)
            self.cursor.fetchone()
        else:
            self.cursor.execute(zapytanie, args)
            self.conn.commit()


        self.cursor.close()
        self.conn.close()

class Logowanie(QMainWindow):

    def __init__(self, aplikacja):
        super().__init__()
        self.aplikacja = aplikacja
        self.setFixedSize(350, 250)
        self.setWindowTitle('Dawaj byq')
        self.ekran()

    def ekran(self):

        self.nu1 = QLineEdit('', self)
        self.nu1.move(100, 30)
        self.nu1.setFixedWidth(200)
        self.nu1.setFixedHeight(25)

        self.h1 = QLineEdit('', self)
        self.h1.move(100, 70)
        self.h1.setFixedWidth(200)
        self.h1.setFixedHeight(25)
        self.h1.setEchoMode(QLineEdit.EchoMode.Password)

        self.label_nu1 = QLabel("Nazwa użytkownika: ", self)
        self.label_nu1.setWordWrap(True)
        self.label_nu1.move(10, 24)

        self.label_h1 = QLabel("Hasło: ", self)
        self.label_h1.move(10, 68)

        self.Zal = QPushButton('Zaloguj się', self)
        self.Zal.move(-3, 180)
        self.Zal.setFixedSize(355,25)

        self.cbx1 = QCheckBox('Wyświetl hasło',self)
        self.cbx1.move(100,90)

        self.cbx1.stateChanged.connect(self.pas1)
        self.nu1.textChanged.connect(self.sprawdzenie)
        self.h1.textChanged.connect(self.sprawdzenie)
        self.Zal.clicked.connect(self.aplikacja.ek_dz)
        self.Zal.setEnabled(False)


    def pas1(self):  #Wyświetlanie hasła

        if self.cbx1.isChecked():
            self.h1.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.h1.setEchoMode(QLineEdit.EchoMode.Password)

    def sprawdzenie(self):      #Sprawdzenie poprawdności loginu i hasla
        self.conn = psycopg2.connect(
            dbname="Users",
            user="michal",
            password="mko1nji2",
            host="localhost"
        )
        self.cursor = self.conn.cursor()

        zapytanie = "SELECT * FROM users WHERE login = %s AND haslo = %s"
        self.cursor.execute(zapytanie, (self.nu1.text(), self.h1.text()))
        user = self.cursor.fetchone()

        self.cursor.close()
        self.conn.close()

        if user:
            self.Zal.setEnabled(True)
            global nazwa_uzytkownika
            nazwa_uzytkownika = self.nu1.text()

        else:
            self.Zal.setEnabled(False)

class Działanie(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setFixedSize(450, 220)
        self.setWindowTitle('Dawaj byq')
        self.ekran2()

    def ekran2(self):

        a = 0  # pozycja startowa Y dla nazw pól
        b = 0  # pozycja startowa Y dla pól do wprowadzania


        self.nu = QLabel(f"Użytkownik : ", self)
        self.nu.move(10, a)
        self.wa = QLabel("Waga : ", self)
        self.mbp = QLabel("Wyciskanie na ławce(kg) : ", self)
        self.md = QLabel("Dip(pow) : ", self)
        self.mpn = QLabel("Podciąganie nachwyt(pow) : ", self)
        self.wynik = QPushButton('Oblicz', self)
        self.wynik.move(10, 180)
        self.wynik.clicked.connect(self.oblicz_dane)

        self.lwa = QLineEdit('', self)
        self.lmbp = QLineEdit('', self)
        self.lmd = QLineEdit('', self)
        self.lmpn = QLineEdit('', self)


        self.list = [self.wa,self.mbp,self.md,self.mpn,]
        self.listl = [self.lwa, self.lmbp, self.lmd, self.lmpn,]

        for i in self.list:
            a += 33
            i.move(10, a)
            i.setWordWrap(True)

        for i in self.listl:
            b += 35
            i.move(100, b)
            i.setFixedWidth(75)
            i.setFixedHeight(25)
            i.setValidator(QIntValidator(0, 100))

    def oblicz_dane(self):      # Wywołuje wynik obliczeń
        waga = self.lwa.text()
        pola = [(self.lmbp, klata, 68), (self.lmd, dip, 102), (self.lmpn, podciagniecia, 136)]

        if self.lwa.text() == '':
            QMessageBox.warning(self, 'Błąd', 'Podaj wagę')
        else:
            self.wyczysc()
            for pole, cwiczenie, pozycja_y in pola:
                if not pole.text():
                    tekst = 'Wprowadz dane'
                else:
                    tekst = self.liczenie(float(waga), int(pole.text()), cwiczenie)
                self.wprowadzone_dane(pole, tekst, pozycja_y)

    def wprowadzone_dane(self, pole, tekst, pozycja_y):
        if pole.text() == '':
            etykieta = QLabel('Wprowadź dane', self)
        else:
            etykieta = QLabel(tekst, self)
        etykieta.move(200, pozycja_y)
        etykieta.show()

    def wyczysc(self):      # Czyści poprzenie etykiety wyników
        for i in self.findChildren(QLabel):
            if i.text() in ('Wprowadź dane', 'Początkujący', 'Nowicjusz', 'Średnio zaawansowany', 'Zaawansowany', 'Elitarny'):
                i.setParent(None)

    def liczenie(self, w, z, s): # Oblicza wynik
        # w - waga
        # z - ilość powtórzeń
        # s - słownik z którego ma skorzystać
        # Zaokrąglenie podanej wagi
        pa = 50 * round(w / 50, 1)
        paz = round(pa, 1)

        # Znalezienie odpowiedniego klucza
        for klucz, wartosc in s.items():
            if wartosc['w'] == paz:
                zk = klucz  # Znaleziony klucz

        # sprawdza najbliższą wartośc cięzaru do podanej przez użytkownika
        lbw = [value for key, value in s[zk].items() if key != 'w']  # lista z pominięciem 'w'
        war = min(lbw, key=lambda x: abs(x - z))  # Przeszukanie lbw

        # Zwraca poziom użytkownika
        for i in s[zk]:
            if s[zk][i] == war and i != 'w':
                return i

if __name__ == '__main__':
    app = QApplication(sys.argv)
    Aplikacja = Aplikacja()
    sys.exit(app.exec())
