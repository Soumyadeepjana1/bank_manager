import sys
import ctypes
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QStackedWidget, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

# Load Shared Library
try:
    lib_path = os.path.join(os.path.dirname(__file__), "libbank.so")
    bank_lib = ctypes.CDLL(lib_path)
except Exception as e:
    print(f"Failed to load backend library: {e}")
    sys.exit(1)

# Define Function Signatures
bank_lib.init_db.restype = ctypes.c_int

bank_lib.create_account.argtypes = [ctypes.c_char_p, ctypes.c_double]
bank_lib.create_account.restype = ctypes.c_int

bank_lib.get_balance.argtypes = [ctypes.c_int]
bank_lib.get_balance.restype = ctypes.c_double

bank_lib.deposit.argtypes = [ctypes.c_int, ctypes.c_double]
bank_lib.deposit.restype = ctypes.c_int

bank_lib.withdraw.argtypes = [ctypes.c_int, ctypes.c_double]
bank_lib.withdraw.restype = ctypes.c_int

# Initialize DB
if bank_lib.init_db() == 0:
    print("Database Initialization Failed!")
    sys.exit(1)

# Style Tokens
STYLE_SHEET = """
QMainWindow {
    background-color: #121212;
}
QWidget {
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Inter', 'Roboto', sans-serif;
    font-size: 14px;
}
QPushButton {
    background-color: #6200ea;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #7c4dff;
}
QPushButton:pressed {
    background-color: #311b92;
}
QLineEdit {
    background-color: #1e1e1e;
    border: 1px solid #333;
    padding: 10px;
    border-radius: 4px;
    color: #fff;
}
QLineEdit:focus {
    border: 1px solid #6200ea;
}
QLabel {
    font-size: 16px;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Antigravity Bank System")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet(STYLE_SHEET)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Header
        title = QLabel("Bank Management System")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        self.main_layout.addWidget(title)

        # Content Area
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Pages
        self.stacked_widget.addWidget(self.create_menu_page())
        self.stacked_widget.addWidget(self.create_account_page())
        self.stacked_widget.addWidget(self.action_page("Deposit", self.handle_deposit))
        self.stacked_widget.addWidget(self.action_page("Withdraw", self.handle_withdraw))
        self.stacked_widget.addWidget(self.check_balance_page())

    def switch_page(self, i):
        self.stacked_widget.setCurrentIndex(i)

    def go_home(self):
        self.switch_page(0)

    def create_menu_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        btn1 = QPushButton("Create New Account")
        btn1.clicked.connect(lambda: self.switch_page(1))
        
        btn2 = QPushButton("Deposit Money")
        btn2.clicked.connect(lambda: self.switch_page(2))
        
        btn3 = QPushButton("Withdraw Money")
        btn3.clicked.connect(lambda: self.switch_page(3))
        
        btn4 = QPushButton("Check Balance")
        btn4.clicked.connect(lambda: self.switch_page(4))

        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)
        layout.addWidget(btn4)
        
        return page

    def create_account_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        layout.addWidget(QLabel("Owner Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        layout.addWidget(QLabel("Initial Deposit ($):"))
        self.init_dep_input = QLineEdit()
        layout.addWidget(self.init_dep_input)

        submit = QPushButton("Create Account")
        submit.clicked.connect(self.handle_create_account)
        layout.addWidget(submit)

        back = QPushButton("Back")
        back.setStyleSheet("background-color: #424242;")
        back.clicked.connect(self.go_home)
        layout.addWidget(back)

        return page

    def action_page(self, action_name, handler):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        layout.addWidget(QLabel(f"{action_name} - Account Code ID:"))
        acc_id_input = QLineEdit()
        layout.addWidget(acc_id_input)
        
        layout.addWidget(QLabel("Amount ($):"))
        amt_input = QLineEdit()
        layout.addWidget(amt_input)

        submit = QPushButton(action_name)
        submit.clicked.connect(lambda: handler(acc_id_input.text(), amt_input.text()))
        layout.addWidget(submit)

        back = QPushButton("Back")
        back.setStyleSheet("background-color: #424242;")
        back.clicked.connect(self.go_home)
        layout.addWidget(back)

        return page

    def check_balance_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        layout.addWidget(QLabel("Account Code ID:"))
        self.bal_id_input = QLineEdit()
        layout.addWidget(self.bal_id_input)

        submit = QPushButton("Check")
        submit.clicked.connect(self.handle_check_balance)
        layout.addWidget(submit)

        self.bal_result = QLabel("")
        self.bal_result.setAlignment(Qt.AlignCenter)
        self.bal_result.setStyleSheet("color: #00e676; font-size: 18px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.bal_result)

        back = QPushButton("Back")
        back.setStyleSheet("background-color: #424242;")
        back.clicked.connect(self.go_home)
        layout.addWidget(back)

        return page

    # Handlers
    def handle_create_account(self):
        name = self.name_input.text()
        amt_str = self.init_dep_input.text()
        
        if not name or not amt_str:
            QMessageBox.warning(self, "Error", "Details missing")
            return
            
        try:
            amt = float(amt_str)
            if amt < 0: raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid amount")
            return

        name_c = ctypes.c_char_p(name.encode('utf-8'))
        acc_id = bank_lib.create_account(name_c, ctypes.c_double(amt))
        if acc_id != -1:
            QMessageBox.information(self, "Success", f"Account created! Your ID is {acc_id}")
            self.name_input.clear()
            self.init_dep_input.clear()
            self.go_home()
        else:
            QMessageBox.warning(self, "Error", "Failed to create account")

    def handle_deposit(self, acc_id_str, amt_str):
        try:
            acc_id = int(acc_id_str)
            amt = float(amt_str)
            if amt <= 0: raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input values")
            return

        res = bank_lib.deposit(acc_id, ctypes.c_double(amt))
        if res == 1:
            QMessageBox.information(self, "Success", "Deposit successful!")
            self.go_home()
        else:
            QMessageBox.warning(self, "Error", "Deposit failed. Check Account ID.")

    def handle_withdraw(self, acc_id_str, amt_str):
        try:
            acc_id = int(acc_id_str)
            amt = float(amt_str)
            if amt <= 0: raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input values")
            return

        res = bank_lib.withdraw(acc_id, ctypes.c_double(amt))
        if res == 1:
            QMessageBox.information(self, "Success", "Wait for cash dispensed... Transaction successful!")
            self.go_home()
        else:
            QMessageBox.warning(self, "Error", "Withdraw failed. Invalid Account ID or Insufficient Funds.")

    def handle_check_balance(self):
        acc_id_str = self.bal_id_input.text()
        try:
            acc_id = int(acc_id_str)
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid account ID")
            return

        bal = bank_lib.get_balance(acc_id)
        if bal == -1.0:
            self.bal_result.setText("Account not found")
            self.bal_result.setStyleSheet("color: #ff5252;")
        else:
            self.bal_result.setText(f"Balance: ${bal:.2f}")
            self.bal_result.setStyleSheet("color: #00e676;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
