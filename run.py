from PyQt5 import  uic
from PyQt5.QtGui import QFont,QIcon
from PyQt5.QtCore import QThread,pyqtSignal,Qt
from PyQt5.QtWidgets import QHBoxLayout,QLabel ,QMainWindow,QApplication,QVBoxLayout,QFrame,QWidget
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

firebase  = pyrebase.initialize_app(config)
auth = firebase.auth()
def read_creds():
    with open("credentials.json","r") as file:
        creds = file.read()
        email = json.loads(creds)["email"]
        password = json.loads(creds)["password"]
        return [email,password]

def firebase_auth(email,password):
    user = auth.sign_in_with_email_and_password(email,password)
    db = firebase.database()
    return [user,db]

class Ui(QMainWindow):
    def __init__(self,user_info,db_info,user_name):
        super(Ui, self).__init__()
        uic.loadUi('project.ui', self)
        self.setWindowIcon(QIcon("icon.ico"))   
        self.user_name = user_name
        self.user_info = user_info
        self.db_info = db_info
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
    "    max-height:30px"
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
        self.thread = checkMessage(self.db_info,self.user_info)
        self.thread.start()
        self.thread.update.connect(self.change_text)
        
        
    def send(self):
        data = {"from":self.user_name,"message":f"{self.type.text()}"}
        self.db_info.child("chat").child(f"{time.strftime('%d-%m-%Y')}").child(f"{time.strftime('%H:%M:%S')}").set(data, self.user_info['idToken'])

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
    def __init__(self, db,user):
        super(QThread, self).__init__()
        self.db=db
        self.user= user
    def check(self,message):
        self.text = message
        self.update.emit(self.text)
    def run(self):
        self.my_stream = self.db.child("chat").stream(self.check,self.user['idToken'])
    
class Ui_signUp(QMainWindow):
    def __init__(self):
        super(Ui_signUp, self).__init__()
        uic.loadUi('signup.ui', self)
        self.setWindowIcon(QIcon("icon.ico"))
        self.logins_btn.clicked.connect(self.show_login)
        self.signup_btn.clicked.connect(self.create_user)
        self.login_win = Ui_logIn()
        self.login_win.setParent(self)
        self.login_win.setHidden(True)
        self.login_win.login_btn.clicked.connect(self.login)
 
    def show_login(self):
        self.frame.setHidden(True)
        self.login_win.setHidden(False)

    def create_user(self):
        self.email = self.email_edit.text()
        self.password = self.pass_edit.text()
        self.name = self.name_edit.text()
        old_ss = self.name_edit.styleSheet()
        for x in [".", "$", "#", "[", "]", "/"]:
            if x in self.name:
                self.name_edit.setStyleSheet(old_ss.replace("color:rgba(48, 227, 197, 1)","color:red"))
                self.name_edit.setPlaceholderText(f"User name can't have {x}")
                self.name_edit.clear()
                return
        try:
            auth.create_user_with_email_and_password(self.email, self.password)
        except Exception as e:
            print(e)
            if '"message": "WEAK_PASSWORD : Password should be at least 6 characters"' in str(e):
                self.email_edit.setStyleSheet(old_ss)
                self.pass_edit.setStyleSheet(old_ss.replace("color:rgba(48, 227, 197, 1)","color:red"))
                self.pass_edit.setPlaceholderText("Pswd must be at least 6 characters")
                self.pass_edit.clear()
            elif '"message": "INVALID_EMAIL"' in str(e):
                self.pass_edit.setStyleSheet(old_ss)
                self.email_edit.setStyleSheet(old_ss.replace("color:rgba(48, 227, 197, 1)","color:red"))
                self.email_edit.setPlaceholderText("Invalid Email!")
                self.email_edit.clear()
            elif '"message": "EMAIL_EXISTS"' in str(e):
                self.pass_edit.setStyleSheet(old_ss)
                self.email_edit.setStyleSheet(old_ss.replace("color:rgba(48, 227, 197, 1)","color:red"))
                self.email_edit.setPlaceholderText("Email Exists!")
                self.email_edit.clear()
        else:  
            user_info,db_info= firebase_auth(self.email,self.password)
            self.main_window = Ui(user_info,db_info,self.email)
            self.main_window.show()
            self.close()

            

    def login(self):
        self.email = self.login_win.email_edit.text()
        self.password = self.login_win.pass_edit.text()
        old_ss = self.login_win.pass_edit.styleSheet()
        try:
            firebase_auth(self.email,self.password)
        except Exception as e:
            if '"message": "INVALID_EMAIL"' in str(e):
                self.login_win.email_edit.setStyleSheet(old_ss.replace("color:rgba(48, 227, 197, 1)","color:red"))
                self.login_win.email_edit.setPlaceholderText("Invalid Email!")
                self.login_win.email_edit.clear()
            elif '"message": "EMAIL_NOT_FOUND"' in str(e):
                self.login_win.email_edit.setStyleSheet(old_ss.replace("color:rgba(48, 227, 197, 1)","color:red"))
                self.login_win.pass_edit.setStyleSheet(old_ss)
                self.login_win.email_edit.setPlaceholderText("User not found!")
                self.login_win.email_edit.clear()
            elif '"message": "INVALID_PASSWORD"' in str(e):
                self.login_win.pass_edit.setStyleSheet(old_ss.replace("color:rgba(48, 227, 197, 1)","color:red"))
                self.login_win.email_edit.setStyleSheet(old_ss)
                self.login_win.pass_edit.setPlaceholderText("Invalid Password!")
                self.login_win.pass_edit.clear()
        else:
            with open("credentials.json","w") as file:
                file.write(json.dumps({"email":self.email,"password":self.password}))

            user_info,db_info = firebase_auth(self.email,self.password)
            self.main_window = Ui(user_info,db_info,self.email)
            self.main_window.show()
            self.close()


    
class Ui_logIn(QWidget):
    def __init__(self):
        super(Ui_logIn, self).__init__()
        uic.loadUi('login.ui', self)
        self.setWindowIcon(QIcon("icon.ico"))

   
    
creds = read_creds()
if creds[0] == "" or creds[1] =="":
    app = QApplication(sys.argv)
    window = Ui_signUp()
    window.show()
    app.exec_()
else:
    try:
        user_info,db_info = firebase_auth(creds[0],creds[1])
    except Exception:
        app = QApplication(sys.argv)
        window = Ui_signUp()
        window.show()
        app.exec_()
    else:
        app = QApplication(sys.argv)
        window = Ui(user_info,db_info,creds[0])
        window.show()
        app.exec_()