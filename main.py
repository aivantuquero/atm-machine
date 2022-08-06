from PyQt5 import QtWidgets, uic
import sys
import sqlite3

#define conection and cursor
connection = sqlite3.connect('ATM.db')
cursor = connection.cursor()

command1 = """CREATE TABLE IF NOT EXISTS users(accountNum INTEGER PRIMARY KEY, name TEXT, address TEXT, user TEXT, password TEXT, balance INTEGER, status TEXT)"""
command2 = """CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY AUTOINCREMENT, accountNum INTEGER, type TEXT, value INTEGER, FOREIGN KEY (accountNum) REFERENCES users (accountNum))"""


cursor.execute(command1)
cursor.execute(command2)

# admin-username: admin
# admin-password: 1234

#for user persistent data - GLOBAL VARS
user = ""
password =""
accountNum = 0
 
iterator = 0

prompt = 0
tempUser = ""
Acc_change_History = []

attempt = 3
ATM_balance = 50000

class Register(QtWidgets.QMainWindow):
    def __init__(self):
        super(Register, self).__init__()
        uic.loadUi('Register.ui', self)
        

        self.Login=Login()
        self.Menu=Menu()
        self.Security=Security()
        self.Deposit=Deposit()
        self.Withdraw=Withdraw()
        self.Balance=Balance()
        self.User=User()
        self.Admin=Admin()
        self.History=History()
        self.Unblock=Unblock()
        self.Welcome=Welcome()
        self.Activity=Activity()

        self.Welcome.display()

        #EVENTS
        self.btnRegister.clicked.connect(lambda: self.registerUser())
        self.Login.btnLogin.clicked.connect(lambda: self.loginUser())
        self.Security.btnCancel.clicked.connect(lambda: (self.Security.hide(), self.Welcome.display()) )
        
        self.Menu.btnHistory.clicked.connect(lambda: (self.setPrompt(6), self.Security.display(), self.Menu.hide()))
        self.Menu.btnDeposit.clicked.connect(lambda: (self.setPrompt(1), self.Security.display(), self.Menu.hide()))
        self.Menu.btnUser.clicked.connect(lambda: (self.setPrompt(4), self.Security.display(), self.Menu.hide()))
        self.Menu.btnWithdraw.clicked.connect(lambda: (self.setPrompt(2), self.Security.display(), self.Menu.hide()))
        self.Menu.btnCheck.clicked.connect(lambda: (self.setPrompt(3), self.Security.display(), self.Menu.hide()))
        self.Login.btnCancel.clicked.connect(lambda: (self.Login.hide(), self.Welcome.display()))
        self.Welcome.btnLogin.clicked.connect(lambda: (self.Login.display(), self.Welcome.hide()))
        self.Welcome.btnAdmin.clicked.connect(lambda: (self.setPrompt(5), self.Security.display(), self.Welcome.hide()))
        self.Deposit.btnCancel.clicked.connect(lambda: (self.Menu.display(), self.Deposit.hide()))
        self.User.btnCancel.clicked.connect(lambda: (self.Menu.display(), self.User.hide()))
        
        self.Menu.btnExit.clicked.connect(lambda: (self.Welcome.display(), self.logOut(), self.Menu.hide()))

        self.User.btnUpdate.clicked.connect(lambda: (self.update()))
        self.Security.btnDone.clicked.connect(lambda: self.securityPrompt())
        self.Deposit.btnDeposit.clicked.connect(lambda: self.deposit())
        self.Withdraw.btnWithdraw.clicked.connect(lambda: self.withdraw())
        self.Balance.btnCancel.clicked.connect(lambda: (self.Balance.hide(), self.Menu.show()))
        self.Withdraw.btnCancel.clicked.connect(lambda: (self.Menu.display(), self.Withdraw.hide()))

        #Admin events
        self.Admin.btnUnblock.clicked.connect(lambda: (self.Unblock.display(), self.Admin.hide()))
        self.Admin.btnHistory.clicked.connect(lambda: (self.History.display(), self.initHistory(), self.Admin.hide()))
        self.Unblock.btnCancel.clicked.connect(lambda: (self.Admin.display(), self.Unblock.hide()))
        self.Admin.btnExit.clicked.connect(lambda: (self.Admin.hide(), self.Welcome.display()))
        self.Unblock.btnUnblock.clicked.connect(lambda: (self.unblock(), self.Admin.display(), self.Unblock.hide()))
        self.Admin.btnRegister.clicked.connect(lambda: (self.show(), self.clear(), self.Admin.hide()))
        self.Admin.btnUser.clicked.connect(lambda: (self.setPrompt(4), self.Security.display(), self.Admin.hide()))
        self.Admin.btnCustomer.clicked.connect(lambda: (self.setPrompt(7), self.Security.display(), self.Admin.hide()))
        self.Activity.btnBack.clicked.connect(lambda: (self.Menu.display(), self.Activity.hide()))

        self.History.btnBack.clicked.connect(lambda: (self.Admin.display(), self.History.hide() ))
    
    def logOut(self):
        global user
        global password

        user = ""
        password = ""

    def initHistory(self):

        accounts = ""
        dep = ""
        wit = ""


        cursor.execute('''SELECT * FROM users ORDER BY accountNum DESC LIMIT 4''')
        all_rows = cursor.fetchall()
        for row in all_rows:
            accounts += (" , " + row[3])

        cursor.execute('''SELECT * FROM transactions ORDER BY id DESC LIMIT 4''')
        all_rows = cursor.fetchall()
        for row in all_rows:
            if row[2] == "Deposit":
                dep += (" , " + str(row[3]))
            
            if row[2] == "Withdraw":
                wit += (" , " + str(row[3]))


        self.History.txtCreate.setText("Recently created accounts : "+ accounts)
        self.History.txtWithdraw.setText("Values withdrawn today: " + wit)
        self.History.txtDeposit.setText("Values deposited today:" + dep)
        self.History.txtChange.setText("Account Change: " + str(Acc_change_History))


    def unblock(self):
        acc = self.Unblock.txtUsername.text()
        cursor.execute('''SELECT * FROM users WHERE user=?''', [acc])
        user1 = cursor.fetchone()
        if user1:
            cursor.execute('''UPDATE users SET status = ? WHERE user = ? ''', ("ACTIVE", acc))
            print("account is now unblocked")
        else:
            print("Account not found, Please try again.")
        connection.commit()
        

    def update(self):

        global Acc_change_History

        global tempUser

        cursor.execute('''UPDATE users SET name = ?, address = ?, user = ?, password = ? WHERE user = ? ''', (self.User.txtName.text(), self.User.txtAddress.text(), self.User.txtUsername.text(), self.User.txtPin.text(), tempUser))

        connection.commit()
        Acc_change_History.append({"Username": self.User.txtUsername.text()}) 

        self.User.hide()
        print("\nUpdate Successfull, Logging out for security...\n")
        self.Welcome.display()
   
    
    def setPrompt(self, num):
        global prompt
        prompt = num

    def withdraw(self):

        cursor.execute('''SELECT * FROM users WHERE user=?''', [user])
        user1 = cursor.fetchone()

        global ATM_balance
        print("Your Current Balance: ", user1[5])
        print("Maximum withdraw amount: Php 20,000")
        withdraw = int(self.Withdraw.txtWithdraw.text())
        if withdraw > user1[5]:
            print("")
            print("!! Insufficient Balance !!")
            print("")
        elif withdraw > 20000:
            print("")
            print("!! Withdrawal has reached it's maximum amount !!")
            print("")
        elif withdraw > ATM_balance:
            print("")
            print("!! Insufficient ATM Balance. Please try again !!")
            print("")
            if ATM_balance < 1:
                print("")
                print("!! ATM's money has reached it's limit. Please come again tomorrow !!")
                print("")

        else:
            bal = user1[5] - withdraw


            ATM_balance = ATM_balance - withdraw
            print("")
            print("---Withdraw Successful----")
            print("Your new balance is ", bal)
            print("")
            print("")
            cursor.execute('''UPDATE users SET balance = ? WHERE user = ? ''', (bal, user))
            connection.commit()
            
            

            self.Menu.display()
            self.Withdraw.txtWithdraw.setText("")
            self.Withdraw.hide()


            cursor.execute('''INSERT INTO transactions(accountNum, type, value) VALUES(?,?,?)''', (accountNum, 'Withdraw', withdraw))
            connection.commit()



    def securityPrompt(self):
        global user
        global password
        global prompt
        global attempt

        userInput = self.Security.txtUsername.text()
        passwordInput = self.Security.txtPin.text()

        self.Security.txtUsername.setText("")
        self.Security.txtPin.setText("")

        if prompt == 1:
  
            
            try:
                if user == userInput and password == passwordInput:

                    cursor.execute('''SELECT * FROM users WHERE user = ?''', [user])
                    user1 = cursor.fetchone()

                    self.Deposit.txtBalance.setText("Balance: "+ str(user1[5]))
                    self.Deposit.display()
                    self.Security.hide()
                    connection.commit()


                else:
                    raise ValueError('Account not found')


            except ValueError:
                ctr = attempt - 1
                print("")
                print("Account Not Found!")
                print("")
                print(f"{ctr}  attempt/s left!")
                print("")
                attempt = attempt - 1

                if attempt == 0:
                    cursor.execute('''SELECT * FROM users WHERE user=?''', [user])
                    user1 = cursor.fetchone()
                    if user1:
                        cursor.execute('''UPDATE users SET status = ? WHERE user = ? ''', ("BLOCKED", user))
                        print("Account has now been blocked!")
                        connection.commit()
                        user = ""
                        password = ""

                    
                    print("Having trouble? Report it to admin. Resetting attempts...")
                    attempt = 3


        
        if prompt == 2:
            

            try:
                if user == userInput and password == passwordInput:
                    cursor.execute('''SELECT * FROM users WHERE user = ?''', [user])
                    user1 = cursor.fetchone()


                    self.Withdraw.txtBalance.setText("Balance: "+ str(user1[5]))
                    self.Withdraw.display()
                    self.Security.hide()


                else:
                    raise ValueError('Account not found')


            except ValueError:
                ctr = attempt - 1
                print("")
                print("Account Not Found!")
                print("")
                print(f"{ctr}  attempt/s left!")
                print("")
                attempt = attempt - 1

                if attempt == 0:
                    cursor.execute('''SELECT * FROM users WHERE user=?''', [user])
                    user1 = cursor.fetchone()
                    if user1:
                        cursor.execute('''UPDATE users SET status = ? WHERE user = ? ''', ("BLOCKED", user))
                        print("Account has now been blocked!")
                        connection.commit()
                        user = ""
                        password = ""

                    
                    print("Having trouble? Report it to admin. Resetting attempts...")
                    attempt = 3



        if prompt == 3:
            try:
                if user == userInput and password == passwordInput:
                    cursor.execute('''SELECT * FROM users WHERE user=?''', [user])
                    user1 = cursor.fetchone()

                    self.Balance.txtBalance.setText("Balance: "+ str(user1[5]))     
                    self.Balance.display()
                    self.Security.hide()


                else:
                    raise ValueError('Account not found')


            except ValueError:
                ctr = attempt - 1
                print("")
                print("Account Not Found!")
                print("")
                print(f"{ctr}  attempt/s left!")
                print("")
                attempt = attempt - 1

                if attempt == 0:
                    cursor.execute('''SELECT * FROM users WHERE user=?''', [user])
                    user1 = cursor.fetchone()
                    if user1:
                        cursor.execute('''UPDATE users SET status = ? WHERE user = ? ''', ("BLOCKED", user))
                        print("Account has now been blocked!")
                        connection.commit()
                        user = ""
                        password = ""

                    
                    print("Having trouble? Report it to admin. Resetting attempts...")
                    attempt = 3


        if prompt == 4:
            
            try:
                if userInput != "" and passwordInput != "":
                    global tempUser
                    cursor.execute('''SELECT * FROM users WHERE user=?''', [userInput])
                    tempUser = userInput
                    user1 = cursor.fetchone()

                    self.User.txtName.setText(user1[1])
                    self.User.txtUsername.setText(user1[3])
                    self.User.txtAddress.setText(user1[2])
                    self.User.txtPin.setText(user1[4])
                    self.User.txtBalance.setText("Balance: "+ str(user1[5]))


                    self.User.display()
                    self.Security.hide()



                else:
                    raise ValueError('Account not found')


            except ValueError:
                ctr = attempt - 1
                print("")
                print("Account Not Found!")
                print("")
                print(f"{ctr}  attempt/s left!")
                print("")
                attempt = attempt - 1

                if attempt == 0:
                    cursor.execute('''SELECT * FROM users WHERE user=?''', [user])
                    user1 = cursor.fetchone()
                    if user1:
                        cursor.execute('''UPDATE users SET status = ? WHERE user = ? ''', ("BLOCKED", user))
                        print("Account has now been blocked!")
                        connection.commit()
                        user = ""
                        password = ""

                    
                    print("Having trouble? Report it to admin. Resetting attempts...")
                    attempt = 3



        #admin
        if prompt == 5:
            
            if userInput == "admin" and passwordInput == "1234":

                self.Admin.display()
                self.Security.hide()


            else:
                print("Account not found")
            
        #activity history
        if prompt == 6:
            try:
                if user == userInput and password == passwordInput:

                    self.Activity.btnBack.clicked.disconnect()

                    self.Activity.txtHistory.setText("Activity History for: "+user)

                    deposits = []
                    withdraws = []

                    cursor.execute('''SELECT * FROM transactions WHERE accountNum=?''', [accountNum])

                    all_rows = cursor.fetchall()
                    for row in all_rows:
                        if row[2] == "Deposit":
                            deposits.append(row[3])
                        else:
                            withdraws.append(row[3])

                    row = 0
                    if len(deposits) > len(withdraws):
                        self.Activity.tableHistory.setRowCount(len(deposits))
                    else:
                        self.Activity.tableHistory.setRowCount(len(withdraws))

                    for activity in deposits:
                        print(activity)
                        self.Activity.tableHistory.setItem(row, 0, QtWidgets.QTableWidgetItem(str(activity)))
                        row = row + 1
                    
                    row=0
                    for activity in withdraws:
                        print(activity)
                        self.Activity.tableHistory.setItem(row, 1, QtWidgets.QTableWidgetItem(str(activity)))
                        row = row + 1
                    
                    self.Activity.btnBack.clicked.connect(lambda: (self.Menu.display(), self.Activity.hide()))
                    self.Activity.display()
                    self.Security.hide()



                else:
                    raise ValueError('Account not found')


            except ValueError:
                ctr = attempt - 1
                print("")
                print("Account Not Found!")
                print("")
                print(f"{ctr}  attempt/s left!")
                print("")
                attempt = attempt - 1

                if attempt == 0:
                    cursor.execute('''SELECT * FROM users WHERE user=?''', [user])
                    user1 = cursor.fetchone()
                    if user1:
                        cursor.execute('''UPDATE users SET status = ? WHERE user = ? ''', ("BLOCKED", user))
                        print("Account has now been blocked!")
                        connection.commit()
                        user = ""
                        password = ""

                    
                    print("Having trouble? Report it to admin. Resetting attempts...")
                    attempt = 3

        if prompt == 7:
            try:
                if userInput != "" and passwordInput != "":

                    self.Activity.btnBack.clicked.disconnect()

                    self.Activity.txtHistory.setText("Activity History for: "+user)

                    deposits = []
                    withdraws = []

                    cursor.execute('''SELECT * FROM transactions WHERE accountNum=?''', [accountNum])

                    all_rows = cursor.fetchall()
                    
                    for row in all_rows:
                        if row[2] == "Deposit":
                            deposits.append(row[3])
                        else:
                            withdraws.append(row[3])

                    row = 0
                    if len(deposits) > len(withdraws):
                        self.Activity.tableHistory.setRowCount(len(deposits))
                    else:
                        self.Activity.tableHistory.setRowCount(len(withdraws))

                    for activity in deposits:
                        print(activity)
                        self.Activity.tableHistory.setItem(row, 0, QtWidgets.QTableWidgetItem(str(activity)))
                        row = row + 1
                    
                    row=0
                    for activity in withdraws:
                        print(activity)
                        self.Activity.tableHistory.setItem(row, 1, QtWidgets.QTableWidgetItem(str(activity)))
                        row = row + 1
                    
                    self.Activity.btnBack.clicked.connect(lambda: (self.Admin.display(), self.Activity.hide()))
                    self.Activity.display()
                    self.Security.hide()



                else:
                    raise ValueError('Account not found')


            except ValueError:
                ctr = attempt - 1
                print("")
                print("Account Not Found!")
                print("")
                print(f"{ctr}  attempt/s left!")
                print("")
                attempt = attempt - 1

                if attempt == 0:
                    cursor.execute('''SELECT * FROM users WHERE user=?''', [user])
                    user1 = cursor.fetchone()
                    if user1:
                        cursor.execute('''UPDATE users SET status = ? WHERE user = ? ''', ("BLOCKED", user))
                        print("Account has now been blocked!")
                        connection.commit()
                        user = ""
                        password = ""

                    
                    print("Having trouble? Report it to admin. Resetting attempts...")
                    attempt = 3
        
 

    def deposit(self):
        global user
        deposit = int(self.Deposit.txtValue.text())

        cursor.execute('''SELECT * FROM users WHERE user=?''', [user])
        user1 = cursor.fetchone()

        bal = user1[5] + deposit

        cursor.execute('''UPDATE users SET balance = ? WHERE user = ? ''', (bal, user))
        connection.commit()

        cursor.execute('''INSERT INTO transactions(accountNum, type, value) VALUES(?,?,?)''', (accountNum, 'Deposit', deposit))
        connection.commit()

        self.Deposit.hide()
        self.Menu.display()

        print("Deposit is Sucessful!")
        


    def clear(self):
        self.txtName.setText("")
        self.txtAddress.setText("")
        self.txtUsername.setText("")
        self.txtPin.setText("")
        self.txtStartMoney.setText("")
    
    def registerUser(self):
        if self.txtName.text() == "" or self.txtUsername.text() == "" or self.txtAddress.text() == "" or self.txtPin.text() == "" or self.txtStartMoney.text() == "":
            return

        global iterator
        global transactions

        print("iterator: " , iterator)

        cursor.execute('''SELECT user, password FROM users WHERE user=? AND password=?''', (self.txtUsername.text(), self.txtPin.text()))
        user1 = cursor.fetchone()

        if user1:
            print("User already exist, please kindly choose another one!")
        else:
            # this will get the last account value 
            cursor.execute('''SELECT * FROM users WHERE accountNum=(SELECT max(accountNum) FROM users)''')

            accNo = cursor.fetchone()

            if accNo:
                iterator = int(accNo[0])+1


            cursor.execute('''INSERT INTO users(accountNum, name, address, user, password, balance, status) VALUES(?,?,?,?,?,?,?)''', (iterator, self.txtName.text(), self.txtAddress.text(), self.txtUsername.text(), self.txtPin.text(), int(self.txtStartMoney.text()), 'ACTIVE'))
            cursor.execute('''INSERT INTO transactions(accountNum, type, value) VALUES(?,?,?)''', (iterator, 'Deposit', int(self.txtStartMoney.text())))

            connection.commit()
            self.txtName.setText("")
            self.txtAddress.setText("")
            self.txtUsername.setText("")
            self.txtPin.setText("")
            self.txtStartMoney.setText("")
            connection.commit()

            self.hide()
            self.Login.display()

    def loginUser(self):
        global user
        global password
        global accountNum
        global attempt

        
        #if walang nakalagay
        if self.Login.txtUsername.text() == "" or self.Login.txtPin.text() == "":
            return
        try:
            cursor.execute('''SELECT * FROM users WHERE user=? AND password=?''', (self.Login.txtUsername.text(), self.Login.txtPin.text()))
            user1 = cursor.fetchone()

            if user1:
                if(user1[6] == "BLOCKED"):
                    print("The user is currently blocked. Please kindly report it to admin")
                    return
                user = self.Login.txtUsername.text()
                password = self.Login.txtPin.text()
                accountNum = int(user1[0])
                self.Login.hide()
                self.Menu.display()
                self.Login.txtUsername.setText("")
                self.Login.txtPin.setText("")

            else:
                raise ValueError('Account not found')


        except ValueError:
            ctr = attempt - 1
            print("")
            print("Account Not Found!")
            print("")
            print(f"{ctr}  attempt/s left!")
            print("")
            attempt = attempt - 1

            if attempt == 0:
                cursor.execute('''SELECT * FROM users WHERE user=?''', [self.Login.txtUsername.text()])
                user1 = cursor.fetchone()
                if user1:
                    cursor.execute('''UPDATE users SET status = ? WHERE user = ? ''', ("BLOCKED", self.Login.txtUsername.text()))
                    print("Account has now been blocked!")
                    connection.commit()

                
                print("Having trouble? Report it to admin. Resetting attempts...")
                attempt = 3


class Login(QtWidgets.QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        uic.loadUi('Login.ui', self)
    
    def display(self):
        self.show()

class Menu(QtWidgets.QMainWindow):
    def __init__(self):
        super(Menu, self).__init__()
        uic.loadUi('Menu.ui', self)

    def display(self):
        self.show()
    
class Security(QtWidgets.QMainWindow):
    def __init__(self):
        super(Security, self).__init__()
        uic.loadUi('Security.ui', self)
    
    def display(self):
        self.show()
    
class Deposit(QtWidgets.QMainWindow):
    def __init__(self):
        super(Deposit, self).__init__()
        uic.loadUi('Deposit.ui', self)
    
    def display(self):
        self.show()

class Withdraw(QtWidgets.QMainWindow):
    def __init__(self):
        super(Withdraw, self).__init__()
        uic.loadUi('Withdraw.ui', self)
    
    def display(self):
        self.show()

class Balance(QtWidgets.QMainWindow):
    def __init__(self):
        super(Balance, self).__init__()
        uic.loadUi('Balance.ui', self)
    
    def display(self):
        self.show()

class User(QtWidgets.QMainWindow):
    def __init__(self):
        super(User, self).__init__()
        uic.loadUi('User.ui', self)
    
    def display(self):
        self.show()

class Admin(QtWidgets.QMainWindow):
    def __init__(self):
        super(Admin, self).__init__()
        uic.loadUi('Admin.ui', self)
    
    def display(self):
        self.show()
    
class History(QtWidgets.QMainWindow):
    def __init__(self):
        super(History, self).__init__()
        uic.loadUi('History.ui', self)
    
    def display(self):
        self.show()

class Unblock(QtWidgets.QMainWindow):
    def __init__(self):
        super(Unblock, self).__init__()
        uic.loadUi('Unblock.ui', self)
    
    def display(self):
        self.show()

class Welcome(QtWidgets.QMainWindow):
    def __init__(self):
        super(Welcome, self).__init__()
        uic.loadUi('Welcome.ui', self)
    
    def display(self):
        self.show()

class Activity(QtWidgets.QMainWindow):
    def __init__(self):
        super(Activity, self).__init__()
        uic.loadUi('Activity.ui', self)
    
    def display(self):
        self.show()

app = QtWidgets.QApplication(sys.argv)
Window = Register()
app.exec_()