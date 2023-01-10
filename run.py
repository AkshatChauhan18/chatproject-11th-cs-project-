from PyQt5 import  uic
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QThread,pyqtSignal,Qt
from PyQt5.QtWidgets import QHBoxLayout,QLabel ,QMainWindow,QApplication,QVBoxLayout,QFrame,QWidget,QScrollArea
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
        self.scrollArea.verticalScrollBar().setStyleSheet("QScrollBar:vertical {"              
    "    background:#162432;"
    "    width:14px;    "
    "    margin: 10px 0px 10px 0px;"
    "    border-radius:5px"
    "}"
    "QScrollBar::handle:vertical {"
    "    background: #4d525e;"
    "    border-radius:5px;"
    "    maximum-height:30px"
    "}"
    "QScrollBar::add-line:vertical {"
    "    height: 0px"
    "}"
    "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {"
    "    background: none"
    "}"
    "QScrollBar::sub-line:vertical {"
    "    height: 0px;"
    "}")
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
                date_widget = QLabel()
                date_widget.setText(x)
                date_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                date_widget.setStyleSheet("color:gray;background:rgba(0, 0, 0, 0.44)")
                font  =QFont()
                font.setBold(True)
                font.setPointSize(13)
                date_widget.setFont(font)
                self.display.addWidget(date_widget)
                for y in msg["data"][x]:
                    h_layout = QHBoxLayout()
                    h_layout.addWidget(self.create_msgbox(msg['data'][x][y]['from'],y,msg['data'][x][y]['message']))
                    h_layout.addStretch()
                    self.display.addLayout(h_layout)
                    
        else:
            _,dte,tme =  msg["path"].split("/")
            date_widget = QLabel()
            date_widget.setText(dte)
            date_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            date_widget.setStyleSheet("color:gray;background:rgba(0, 0, 0, 0.44)")
            font  =QFont()
            font.setBold(True)
            font.setPointSize(13)
            date_widget.setFont(font)
            self.display.addWidget(date_widget)
            h_layout = QHBoxLayout()
            h_layout.addWidget(self.create_msgbox(msg["data"]["from"],tme,msg["data"]["message"]))
            h_layout.addStretch()
            self.display.addLayout(h_layout)
    def create_msgbox(self,usr,tm,msg):
        msg_box = QWidget()
        # msg_box.setBaseSize(209,91)
        msg_box.setStyleSheet("background:#b4eeb4;border-radius: 23px;")
        verticalLayout = QVBoxLayout(msg_box)
        verticalLayout.setContentsMargins(9, 9, 9, 0)

        frame = QFrame(msg_box)
        frame.setStyleSheet("background:#8dbb8d;border-width:10px;border-radius:8px")
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)

        horizontalLayout = QHBoxLayout(frame)
        usr_name = QLabel(frame)
        horizontalLayout.addWidget(usr_name)
        tme = QLabel(frame)
        tme.setLayoutDirection(Qt.LeftToRight)
        tme.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        tme.setWordWrap(True)
        horizontalLayout.addWidget(tme)
        verticalLayout.addWidget(frame)
        main_msg = QLabel()
        font = QFont()
        font.setFamily("Segoe UI Black")
        font.setPointSize(10)
        font.setBold(True)
        main_msg.setFont(font)
        main_msg.setStyleSheet("border-radius:10px")
        verticalLayout.addWidget(main_msg)
        usr_name.setText(usr)
        tme.setText(tm)
        main_msg.setText(msg)
        
        return msg_box
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
