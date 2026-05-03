from PyQt6.QtWidgets import QMainWindow
from accounts import Account, SavingAccount
from banking_info_gui import Ui_banking_info_window
from registration_window import Ui_registration_window
import csv


class LoginController:

    def __init__(self, ui, window):
        self.ui = ui
        self.window = window
        self.checking = None
        self.savings = None
        self.banking_window = None
        self.banking_ui = None
        self.registration_window = None
        self.registration_ui = None

        self.connect_signals()
        self.ui.feedback_txt.setText("")

    def connect_signals(self):
        self.ui.signin_button.clicked.connect(self.login)
        self.ui.register_button.clicked.connect(self.open_registration_window)

    def login(self):
        username = self.ui.username_input.text().strip()
        password = self.ui.password_input.text().strip()

        if not self.validate_login_inputs(username, password):
            return

        user_data = self.get_registered_user(username, password)

        if user_data is not None:
            name, saved_username, saved_password, checking_balance, savings_balance = user_data

            self.ui.feedback_txt.setText("Login successful.")

            self.checking = Account(name, saved_username, saved_password, checking_balance)
            self.savings = SavingAccount(name, saved_username, saved_password, savings_balance)
            self.open_banking_window(name)
        else:
            self.ui.feedback_txt.setText("Invalid username or password.")
    def open_registration_window(self):
        self.registration_window = QMainWindow()
        self.registration_ui = Ui_registration_window()
        self.registration_ui.setupUi(self.registration_window)

        self.registration_ui.validation_txt.setText("")

        self.registration_ui.pushButton.clicked.connect(self.registration)
        self.registration_ui.return_button.clicked.connect(self.return_to_login)

        self.registration_window.show()
        self.window.hide()

    def return_to_login(self):
        self.registration_window.close()
        self.window.show()

    def registration(self):
        name = self.registration_ui.user_name.text().strip()
        username = self.registration_ui.user_username.text().strip()
        password = self.registration_ui.user_password.text().strip()
        checking_text = self.registration_ui.user_checking_balance.text().strip()
        savings_text = self.registration_ui.user_savings_balance.text().strip()

        if name == "":
            self.registration_ui.validation_txt.setText("Please enter a name.")
            return

        if username == "" or not username.isalnum():
            self.registration_ui.validation_txt.setText("Username must be alphanumeric.")
            return

        if password == "" or not password.isalnum():
            self.registration_ui.validation_txt.setText("Password must be alphanumeric.")
            return

        try:
            checking_balance = float(checking_text) if checking_text != "" else 0.0
            savings_balance = float(savings_text) if savings_text != "" else 0.0
        except ValueError:
            self.registration_ui.validation_txt.setText("Balances must be numeric.")
            return

        if checking_balance < 0 or savings_balance < 0:
            self.registration_ui.validation_txt.setText("Balances cannot be negative.")
            return

        with open("users.csv", "a", newline="") as users_file:
            writer = csv.writer(users_file)
            writer.writerow([name, username, password, checking_balance, savings_balance])

        self.registration_ui.validation_txt.setText("Account registered successfully.")
    def validate_login_inputs(self, username, password):
        if username == "":
            self.ui.feedback_txt.setText(
                "Please enter a username.\nUsername must be alphanumeric."
            )
            return False

        if password == "":
            self.ui.feedback_txt.setText(
                "Please enter a password.\nPassword must be alphanumeric."
            )
            return False

        return True

    def create_accounts(self, username, password):
        self.checking = Account(username, username, password, 1000)
        self.savings = SavingAccount(username, username, password, 500)

    def open_banking_window(self, username):
        self.banking_window = QMainWindow()
        self.banking_ui = Ui_banking_info_window()
        self.banking_ui.setupUi(self.banking_window)

        self.banking_ui.person_name_label.setText(username)
        self.update_balance_labels()
        self.banking_ui.validation_message_txt.setText("")

        self.banking_ui.submit_trans_button.clicked.connect(self.transaction)
        self.banking_ui.pushButton.clicked.connect(self.sign_out)

        self.banking_window.show()
        self.window.hide()

    def get_registered_user(self, username, password):
        try:
            with open("users.csv", "r", newline="") as users_file:
                reader = csv.reader(users_file)

                for row in reader:
                    if len(row) < 5:
                        continue

                    name = row[0]
                    saved_username = row[1]
                    saved_password = row[2]
                    checking_balance = float(row[3])
                    savings_balance = float(row[4])

                    if username == saved_username and password == saved_password:
                        return name, saved_username, saved_password, checking_balance, savings_balance

        except FileNotFoundError:
            return None

        return None
    def update_balance_labels(self):
        self.banking_ui.user_checking_balance_label.setText(
            f"${self.checking.get_balance():.2f}"
        )
        self.banking_ui.user_savings_balance_label.setText(
            f"${self.savings.get_balance():.2f}"
        )

    def transaction(self):
        amount = self.get_transaction_amount()

        if amount is None:
            return

        if self.banking_ui.deposit_button.isChecked():
            self.handle_deposit(amount)

        elif self.banking_ui.withdraw_button.isChecked():
            self.handle_withdraw(amount)

        else:
            self.banking_ui.validation_message_txt.setText(
                "Select deposit or withdraw."
            )
            return

        self.update_balance_labels()
        self.banking_ui.amount_input.clear()

    def get_transaction_amount(self):
        try:
            amount = float(self.banking_ui.amount_input.text().strip())
        except ValueError:
            self.banking_ui.validation_message_txt.setText("Enter a valid amount.")
            return None

        if amount <= 0:
            self.banking_ui.validation_message_txt.setText("Amount must be positive.")
            return None

        return amount

    def handle_deposit(self, amount):
        if self.banking_ui.checking_button.isChecked():
            self.checking.deposit(amount)
            self.store_transaction(
                self.checking.get_username(),
                "Deposit",
                "Checking",
                amount,
                self.checking.get_balance(),
            )
            self.banking_ui.validation_message_txt.setText(
                "Deposit to checking successful."
            )

        elif self.banking_ui.savings_button.isChecked():
            self.savings.deposit(amount)
            self.store_transaction(
                self.savings.get_username(),
                "Deposit",
                "Savings",
                amount,
                self.savings.get_balance(),
            )
            self.banking_ui.validation_message_txt.setText(
                "Deposit to savings successful."
            )

        else:
            self.banking_ui.validation_message_txt.setText(
                "Select an account to deposit into."
            )

    def handle_withdraw(self, amount):
        if self.banking_ui.checking_button.isChecked():
            if self.checking.withdraw(amount):
                self.store_transaction(
                    self.checking.get_username(),
                    "Withdraw",
                    "Checking",
                    amount,
                    self.checking.get_balance(),
                )
                self.banking_ui.validation_message_txt.setText(
                    "Withdraw from checking successful."
                )
            else:
                self.banking_ui.validation_message_txt.setText(
                    "Insufficient funds for withdrawal."
                )

        elif self.banking_ui.savings_button.isChecked():
            if self.savings.withdraw(amount):
                self.store_transaction(
                    self.savings.get_username(),
                    "Withdraw",
                    "Savings",
                    amount,
                    self.savings.get_balance(),
                )
                self.banking_ui.validation_message_txt.setText(
                    "Withdraw from savings successful."
                )
            else:
                self.banking_ui.validation_message_txt.setText(
                    "Insufficient funds."
                )

        else:
            self.banking_ui.validation_message_txt.setText(
                "Select an account to withdraw from."
            )

    def sign_out(self):
        self.banking_window.close()

        self.ui.username_input.clear()
        self.ui.password_input.clear()
        self.ui.feedback_txt.setText("")

        self.window.show()

    def store_transaction(self, username, action, account_type, amount, balance):
        with open("transactions.csv", "a", newline="") as transactions_file:
            writer = csv.writer(transactions_file)
            writer.writerow([username, action, account_type, amount, balance])
