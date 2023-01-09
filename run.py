from PyQt5 import  uic
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QThread,pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout,QLabel ,QMainWindow,QApplication
import pyrebase
import time 
import json
import sys

config = {"apiKey": "AIzaSyCLBtEH-AVU-A9kmI7lXjuoC3jne75cXU8",

  "authDomain": "schoolcs-4f1e9.firebaseapp.com",

  "databaseURL": "https://schoolcs-4f1e9-default-rtdb.asia-southeast1.firebasedatabase.app",

  "projectId": "schoolcs-4f1e9",

  "storageBucket": "schoolcs-4f1e9.appspot.com",

  "messagingSenderId": "44756241883",

  "appId": "1:44756241883:web:58835f7bb01362983cabfe",

  "measurementId": "G-DM43PXDCXE"
}

with open("credentials.json","r") as file:
    creds = file.read()
    email = json.loads(creds)["email"]
    password = json.loads(creds)["password"]

firebase  = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(email,password)
db = firebase.database()

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('project.ui', self)
        self.send_button.clicked.connect(self.send)
        self.thread = checkMessage()
        self.thread.start()
        self.thread.update.connect(self.change_text)
        self.show()
        
    def send(self):
        data = {"from":email,"message":f"{self.type.text()}"}
        db.child("chat").child(f"{time.strftime('%d-%m-%Y')}").child(f"{time.strftime('%H:%M:%S')}").set(data, user['idToken'])

    def change_text(self , val):
        msg=val
        if msg["data"]==None:
            return
        print(msg)
        if msg["path"] == "/":
            for x in msg["data"]:
                
                # self.display.setHtml(f"<br><p align='center'>{x}</p><br>")
                for y in msg["data"][x]:
                    h_layout = QHBoxLayout()
                    msg_box = QLabel()
                    msg_box.setText(f"{msg['data'][x][y]['from']}\n{msg['data'][x][y]['message']}")
                    msg_box.setStyleSheet("background:#b4eeb4;border-radius: 6px 23px;")
                    msg_box.setFont(QFont("Calibri",12))
                    h_layout.addWidget(msg_box)
                    h_layout.addStretch()
                    self.display.addLayout(h_layout)
                    
        else:
            pass
        
class checkMessage(QThread):
    update = pyqtSignal(dict)
    def check(self,message):
        self.text = message
        self.update.emit(self.text)
    def run(self):
        self.my_stream = db.child("chat").stream(self.check,user['idToken'])

app = QApplication(sys.argv)
window = Ui()
app.exec_()
