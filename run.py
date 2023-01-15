from PyQt5 import  uic #loading ui files
from PyQt5.QtGui import QFont,QIcon 
from PyQt5.QtCore import QThread,pyqtSignal,Qt
from PyQt5.QtWidgets import QHBoxLayout,QLabel ,QMainWindow,QApplication,QVBoxLayout,QFrame,QWidget,QMessageBox
import pyrebase# for connecting to firebase
import time 
import json
import sys

config = {"apiKey": "AIzaSyCLBtEH-AVU-A9kmI7lXjuoC3jne75cXU8", #firebase database config

  "authDomain": "schoolcs-4f1e9.firebaseapp.com",

  "databaseURL": "https://schoolcs-4f1e9-default-rtdb.asia-southeast1.firebasedatabase.app",

  "projectId": "schoolcs-4f1e9",

  "storageBucket": "schoolcs-4f1e9.appspot.com",

  "messagingSenderId": "44756241883",

  "appId": "1:44756241883:web:58835f7bb01362983cabfe",

  "measurementId": "G-DM43PXDCXE"
}

firebase  = pyrebase.initialize_app(config) #initializing firebase
auth = firebase.auth()  #calling auth method

def read_creds(): # a function to read the credentials from credentials.json
    with open("credentials.json","r") as file:
        creds = file.read()
        email = json.loads(creds)["email"]
        password = json.loads(creds)["password"]
        return [email,password] # returning email and password in list

def firebase_auth(email,password): # a function to sign into firebase account
    user = auth.sign_in_with_email_and_password(email,password)
    db = firebase.database()
    return [user,db] # returning user secrets and database secrets in list

class Ui(QMainWindow):
    def __init__(self,user_info,db_info,user_name):
        super(Ui, self).__init__()
        uic.loadUi('project.ui', self)# loading project.ui
        self.setWindowIcon(QIcon("icon.ico"))   
        self.user_name = user_name
        self.user_info = user_info
        self.db_info = db_info
        self.sh = 0 #setting a flag for settings 
        self.user_btn.clicked.connect(self.show_settings)#if user button is clicked call show_settings() function
        self.send_button.clicked.connect(self.send)#if send button is clicked call send() function
        self.pass_btn.clicked.connect(self.reset_password)#if pass button is clicked call reset_password() function
        self.del_btn.clicked.connect(self.delete_user_warning)#if delete user button is clicked call delete_user_warning() function
        self.settings.setHidden(True)#hide the settings tool bar
        self.scrollArea.verticalScrollBar().setStyleSheet("QScrollBar:vertical {"       #set setylesheet of scrollbar       
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
        self.thread.start()#calling checkMessage class to start the new thread to check whether database is edited or not
        self.thread.update.connect(self.change_text)#if pyqtsignal gives something set the output in change_text() function
        
    def show_settings(self):
        if self.sh == 0:
            
            self.settings.setHidden(False)
            self.sh =1
        else:
            self.settings.setHidden(True)
            self.sh =0
    
    def reset_password(self):
        auth.send_password_reset_email(self.user_name)#request firebase to send reset password email
        self.show_Warning("Password reset email sent!","pass").exec()#show msg box 

    def delete_user_warning(self):
        warning = self.show_Warning("Do you really want to delete your account?","acc")
        returnValue = warning.exec()#show warning box asking for confirmation
        if returnValue == QMessageBox.Yes:#if yes button is pressed delete user
            print(self.user_name)
            auth.delete_user_account(self.user_info["idToken"])#request firebase to delete user
            self.close()#close main UI
            
        

    def send(self):
        data = {"from":self.user_name,"message":f"{self.type.text()}"}#set data to firebase 
        self.db_info.child("chat").child(f"{time.strftime('%d-%m-%Y')}").child(f"{time.strftime('%H:%M:%S')}").set(data, self.user_info['idToken'])

    def change_text(self , val):
        msg=val
        if msg["data"]==None:#when the database is empty return and stop the function
            return
        print(msg)
        if msg["path"] == "/":#on first stream the path is "/"
            for x in msg["data"]:
                self.current_date=x
                date_widget = self.create_date_widget(x)
                self.display.addWidget(date_widget)#then add date widget
                for y in msg["data"][x]:
                    h_layout = QHBoxLayout()
                    h_layout.addWidget(self.create_msgbox(msg['data'][x][y]['from'],y,msg['data'][x][y]['message']))
                    h_layout.addStretch()
                    self.display.addLayout(h_layout)#then add hboxlayout containing the msgbox
                    
        else:
            _,dte,tme =  msg["path"].split("/")#after the first stream the in corresponding stream the path changes to '/date/time'
            if dte != self.current_date:
                date_widget = self.create_date_widget(dte)
                self.display.addWidget(date_widget)
                self.current_date = dte
            h_layout = QHBoxLayout()
            h_layout.addWidget(self.create_msgbox(msg["data"]["from"],tme,msg["data"]["message"]))
            h_layout.addStretch()
            self.display.addLayout(h_layout)
    
    def create_msgbox(self,usr,tm,msg):# creating the chat box ui
        msg_box = QWidget()
        msg_box.setStyleSheet("background:#b4eeb4;border-radius: 18px;")
        verticalLayout = QVBoxLayout(msg_box)
        verticalLayout.setContentsMargins(9, 9, 9, 0)
        frame = QFrame(msg_box)
        frame.setStyleSheet("background:#8dbb8d;border-width:10px;border-radius:8px")
        horizontalLayout = QHBoxLayout(frame)
        usr_name = QLabel(frame)
        tme = QLabel(frame)
        tme.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        tme.setWordWrap(True)
        horizontalLayout.addWidget(usr_name)
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

    def create_date_widget(self,dte):#creating the date widget using Qlabel
        date_widget = QLabel()
        date_widget.setText(dte)
        date_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_widget.setStyleSheet("color:gray;background:rgba(0, 0, 0, 0.44)")
        date_widget.setMaximumHeight(30)
        font  =QFont()
        font.setBold(True)
        font.setPointSize(13)
        date_widget.setFont(font)
        return date_widget#returning the date_widget object

    def show_Warning(self,text,type):#return the date_widget object so that it can be used above
        msg = QMessageBox(self)
        msg.setStyleSheet("background:none;color:rgba(48, 227, 197, 1)")
        msg.setIcon(QMessageBox.Information)
        font = QFont()
        font.setBold(True)
        msg.setFont(font)
        if type == "acc":#if the msg is for delete account then set following settings
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        
        msg.setText(text)
        msg.setWindowTitle("Warning")
        return msg #return the msg object so that it can be used above


class checkMessage(QThread):#creating an another class to run a new thread to check the the database.
    update = pyqtSignal(dict)#a pyqtsignal wHich connects this thread with the main ui thread
    def __init__(self, db,user):
        super(QThread, self).__init__()
        self.db=db
        self.user= user
    def check(self,message):
        self.text = message
        self.update.emit(self.text)#using pyqtsignal to send the changed data to main ui
    def run(self):
        self.my_stream = self.db.child("chat").stream(self.check,self.user['idToken'])#Using pyrebase's stream function to check the database and putting output to check() function
    
class Ui_signUp(QMainWindow):
    def __init__(self):
        super(Ui_signUp, self).__init__()
        uic.loadUi('signup.ui', self)#loading signup ui
        self.setWindowIcon(QIcon("icon.ico"))
        self.logins_btn.clicked.connect(self.show_login)#if login instead button is clicked call show_login() function
        self.signup_btn.clicked.connect(self.create_user)#if sign up button is clicked call create_user() function
        self.login_win = Ui_logIn() # treating login_ui as a widget of sign_up Ui
        self.login_win.setParent(self)
        self.login_win.setHidden(True)#and hiding it at first
        self.login_win.login_btn.clicked.connect(self.login)# if log in button in login window is clicked then call login() function
 
    def show_login(self):
        self.frame.setHidden(True)#hiding the the frame of sign up window
        self.login_win.setHidden(False)#and showing login window

    def create_user(self):
        self.email = self.email_edit.text()#taking text from email input box and storing in variable
        self.password = self.pass_edit.text()#taking text from password input box and storing in variable
        self.name = self.name_edit.text()#taking text from name input box and storing in variable
        old_ss = self.name_edit.styleSheet()#storing the old stylesheet in a variable
        for x in [".", "$", "#", "[", "]", "/"]: # checking if the name contains any of these characters
            if x in self.name:
                self.name_edit.setStyleSheet(old_ss.replace("color:rgba(48, 227, 197, 1)","color:red"))
                self.name_edit.setPlaceholderText(f"User name can't have {x}")
                self.name_edit.clear()
                return
        try:#trying to create user
            auth.create_user_with_email_and_password(self.email, self.password)
        except Exception as e:#if any exception occurs store it in e
            print(e)
            if '"message": "WEAK_PASSWORD : Password should be at least 6 characters"' in str(e):
                self.email_edit.setStyleSheet(old_ss)
                self.pass_edit.setStyleSheet(old_ss.replace("color:rgba(48, 227, 197, 1)","color:red"))#replacing old stylesheet's color to red and setting it 
                self.pass_edit.setPlaceholderText("Pswd must be at least 6 characters")                #setting placeholder
                self.pass_edit.clear()                                                                 #clearing the input box to show placeholder
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
        else:  # if no error occurs save the credentials
            with open("credentials.json","w") as file:#opening the file in write mode and saving the credentials using json.dumps()
                file.write(json.dumps({"email":self.email,"password":self.password}))
            user_info,db_info= firebase_auth(self.email,self.password)
            self.main_window = Ui(user_info,db_info,self.email)
            self.main_window.show()#Now show the chat ui
            self.close()#and close the signup UI

            

    def login(self): 
        self.email = self.login_win.email_edit.text() #taking text from email input box and storing in variable
        self.password = self.login_win.pass_edit.text()#taking text from password input box and storing in variable
        old_ss = self.login_win.pass_edit.styleSheet() #getting the stylesheet stored in the ui file 
        try: #trying to authorize into firebase
            user_info,db_info=firebase_auth(self.email,self.password)
        except Exception as e: # taking exceptions and storing in e
            if '"message": "INVALID_EMAIL"' in str(e):
                self.login_win.pass_edit.setStyleSheet(old_ss)
                self.login_win.email_edit.setStyleSheet(old_ss.replace("color:rgba(48, 227, 197, 1)","color:red"))#replacing old stylesheet's color to red and setting it 
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
        else:# if no error occurs save the credentials
            with open("credentials.json","w") as file: #opening the file in write mode and saving the credentials using json.dumps()
                file.write(json.dumps({"email":self.email,"password":self.password}))

            self.main_window = Ui(user_info,db_info,self.email)
            self.main_window.show() #Now show the chat ui
            self.close()#and close the signup UI


    
class Ui_logIn(QWidget): #creating a class to load the login window ui
    def __init__(self):
        super(Ui_logIn, self).__init__()
        uic.loadUi('login.ui', self)
        self.setWindowIcon(QIcon("icon.ico")) # setting the window icon

   
    
creds = read_creds()

if creds[0] == "" or creds[1] =="": # checking whether the credentials.json is empty
    app = QApplication(sys.argv) 
    window = Ui_signUp()
    window.show()  #calling signup window
    app.exec_()
else:
    try: # trying to sign in firebase
        user_info,db_info = firebase_auth(creds[0],creds[1]) 
    except Exception as e: # if some error occurs show the signup window
        print(e)
        app = QApplication(sys.argv)
        window = Ui_signUp()
        window.show()
        app.exec_()
    else: #if there is no error show main chat window
        app = QApplication(sys.argv)
        window = Ui(user_info,db_info,creds[0])
        window.show()
        app.exec_()