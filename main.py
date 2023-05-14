import datetime
import sqlite3
import requests
from bs4 import BeautifulSoup
import sys
import pyautogui as pg
from PyQt5 import QtCore, QtGui, QtWidgets
from astro_calendar import *
from asking import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QDate
from bs4 import BeautifulSoup
import webbrowser
global db
global sql
db=sqlite3.connect('alldates.db', check_same_thread=False)
sql=db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS dates (info TEXT, day TEXT, month TEXT, year TEXT, fulldate TEXT)""")
db.commit()

#Main window
app = QtWidgets.QApplication(sys.argv)
Dialog = QtWidgets.QDialog()
ui = Ui_Dialog()
ui.setupUi(Dialog)
Dialog.show()

#Asking window
global Asking_dialog
global asking_ui
Asking_dialog = QtWidgets.QDialog()
asking_ui = Ui_Asking_dialog()
asking_ui.setupUi(Asking_dialog)


ui.newslabel.setText("Зачекайте - оновлюється інформація")
now = datetime.datetime.today()
ui.calendardate.setSelectedDate(QDate(int(now.strftime('%Y')),int(now.strftime('%m')), int(now.strftime('%d'))))
ui.linedate.setDate(ui.calendardate.selectedDate())
sql.execute(f"SELECT info FROM dates WHERE fulldate = '{ui.calendardate.selectedDate().toString('dd-MM-yyyy')}'")
result=sql.fetchone()
if result==None:
    ui.keys.setText("Немає жодної інформації стосовно цієї дати. Ви можете додати її сюди та оновити календар.")
else:
    ui.keys.setText(result[0])

#Defs
def upload_info():
    sql.execute(f"SELECT info FROM dates WHERE fulldate = '{ui.calendardate.selectedDate().toString('dd-MM-yyyy')}'")
    result=sql.fetchone()
    if result==None:
        ui.keys.setText("Немає жодної інформації стосовно цієї дати. Ви можете додати її в це поле та оновити календар.")
    else:
        ui.keys.setText(result[0])

def calendardate_changed():
    ui.linedate.setDate(ui.calendardate.selectedDate())
    upload_info()
    last()

def linedate_changed():
    ui.calendardate.setSelectedDate(ui.linedate.date())
    upload_info()
    last()

def update_db():
    adding_info=ui.keys.toPlainText()
    adding_date=ui.calendardate.selectedDate().toString('dd-MM-yyyy')
    day=adding_date[0:2]
    month=adding_date[3:5]
    year=adding_date[6:]
    asking()
    sql.execute(f"SELECT info FROM dates WHERE fulldate = '{adding_date}'")
    result=sql.fetchone()
    if result!=None and result[0]!='':
        if adding_info!='' and adding_info!='Немає жодної інформації стосовно цієї дати. Ви можете додати її в це поле та оновити календар.':
            sql.execute("UPDATE dates SET info = ? WHERE fulldate = ?", (adding_info, adding_date))
            db.commit()
    else:
        if adding_info!='' and adding_info!='Немає жодної інформації стосовно цієї дати. Ви можете додати її в це поле та оновити календар.':
            sql.execute("INSERT INTO dates VALUES (?, ?, ?, ?, ?)", (adding_info, day, month, year, adding_date))
            db.commit()
    Asking_dialog.close()

def cancel():
    Asking_dialog.close()

def asking():
    Asking_dialog.show()

def parse():
    URL='https://www.ukrinform.ua/tag-astronomia'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    items = soup.findAll('article', limit=1)
    for item in items:
        global link
        news=item.find("section").h2.get_text(strip=True)
        link = 'https://www.ukrinform.ua'+item.find("figure").a.get('href')
        if len(news)>=90:
            news=news[0:90]+'...'
        ui.newslabel.setText('Остання новина\n'+news)
parse()


def last():
    choosed_date=ui.calendardate.selectedDate().toString('dd-MM-yyyy')
    if int(choosed_date[0])!=0:
        checking_day=int(choosed_date[0:2])
    else:
        checking_day=int(choosed_date[1])
    choosed_month=choosed_date[3:5]
    choosed_year=choosed_date[6:]
    dates_list=[]
    sql.execute(f"SELECT day FROM dates WHERE month = '{choosed_month}' AND year = '{choosed_year}'")
    results=sql.fetchall()
    if results!=[]:
        for result in results:
            if int(result[0][0])==0:
                if int(result[0][1])>checking_day:
                    dates_list.append(int(result[0]))
            else:
                if int(result[0])>checking_day:
                    dates_list.append(int(result[0]))
        if dates_list==[]:
            ui.nextevent.setText(f'У цьому місяці після {checking_day}.{choosed_month} не залишилось активних подій')
        else:
            dates_list.sort()
            string_dl=''
            for i in dates_list:
                if i<10:
                    string_dl=f"{string_dl} {'0'+str(i)}.{choosed_month},"
                else:
                    string_dl=f"{string_dl} {str(i)}.{choosed_month},"
                if len(string_dl)>=90:
                    string_dl=f"{string_dl[:90]} ...."
            ui.nextevent.setText(f'Залишилось подій у цьому місяці (після {checking_day}.{choosed_month}):\n'+string_dl[:len(string_dl)-1])
    results.clear()
    dates_list.clear()
last()
        

#Connecting to buttons
ui.calendardate.clicked.connect(calendardate_changed)
ui.linedate.dateChanged.connect(linedate_changed)
ui.update.clicked.connect(asking)
ui.movelink.clicked.connect(lambda: webbrowser.open(link))
asking_ui.yesb.clicked.connect(update_db)
asking_ui.nob.clicked.connect(cancel)


sys.exit(app.exec_())