from PyQt6.QtWidgets import QMainWindow
from accounts import Account, SavingAccount
from banking_info_gui import Ui_banking_info_window
from registration_window import Ui_registration_window
import csv


class LoginController:
    """
    Controls user authentication, registration, banking operations,
    and transaction logging for the GUI application.
    """

    def __init__(self, ui, window: QMainWindow) -> None:
        """
        Initialize the controller and connect UI signals.

        Args:
            ui: The login window UI instance.
            window: The main login window.
        """
        self.ui = ui
        self.window: QMainWindow = window
        self.checking: Account | None = None
        self.savings: SavingAccount | None = None
        self.banking_window: QMainWindow | None = None
        self.banking_ui: Ui_banking_info_window | None = None
        self.registration_window: QMainWindow | None = None
        self.registration_ui: Ui_registration_window | None = None

        self.connect_signals()
        self.ui.feedback_txt.setText("")

    def connect_signals(self) -> None:
        """
        Connect UI buttons to controller methods.
        """
        self.ui.signin_button.clicked.connect(self.login)
        self.ui.register_button.clicked.connect(self.open_registration_window)

    def login(self) -> None:
        """
        Handle user login by validating credentials against stored users.
        """
        username: str = self.ui.username_input.text().strip()
        password: str = self.ui.password_input.text().strip()

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

    def open_registration_window(self) -> None:
        """
        Open the registration window.
        """
        self.registration_window = QMainWindow()
        self.registration_ui = Ui_registration_window()
        self.registration_ui.setupUi(self.registration_window)

        self.registration_ui.validation_txt.setText("")

        self.registration_ui.pushButton.clicked.connect(self.registration)
        self.registration_ui.return_button.clicked.connect(self.return_to_login)

        self.registration_window.show()
        self.window.hide()

    def return_to_login(self) -> None:
        """
        Return from registration window to login window.
        """
        if self.registration_window:
            self.registration_window.close()
        self.window.show()

    def registration(self) -> None:
        """
        Register a new user and store their data in users.csv.
        """
        name: str = self.registration_ui.user_name.text().strip()
        username: str = self.registration_ui.user_username.text().strip()
        password: str = self.registration_ui.user_password.text().strip()
        checking_text: str = self.registration_ui.user_checking_balance.text().strip()
        savings_text: str = self.registration_ui.user_savings_balance.text().strip()

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
            checking_balance: float = float(checking_text) if checking_text else 0.0
            savings_balance: float = float(savings_text) if savings_text else 0.0
        except ValueError:
            self.registration_ui.validation_txt.setText("Balances must be numeric.")
            return

        if checking_balance < 0 or savings_balance < 0:
            self.registration_ui.validation_txt.setText("Balances cannot be negative.")
            return

        with open("users.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name, username, password, checking_balance, savings_balance])

        self.registration_ui.validation_txt.setText("Account registered successfully.")

    def validate_login_inputs(self, username: str, password: str) -> bool:
        """
        Validate login input fields.

        Returns:
            True if valid, False otherwise.
        """
        if username == "":
            self.ui.feedback_txt.setText("Please enter a username.")
            return False

        if password == "":
            self.ui.feedback_txt.setText("Please enter a password.")
            return False

        return True

    def open_banking_window(self, username: str) -> None:
        """
        Open the banking window and initialize balances.
        """
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

    def get_registered_user(self, username: str, password: str) -> tuple | None:
        """
        Retrieve user data from users.csv if credentials match.
        """
        try:
            with open("users.csv", "r", newline="") as file:
                for row in csv.reader(file):
                    if len(row) < 5:
                        continue

                    if username == row[1] and password == row[2]:
                        return row[0], row[1], row[2], float(row[3]), float(row[4])
        except FileNotFoundError:
            return None

        return None

    def update_balance_labels(self) -> None:
        """
        Update balance labels in the banking window.
        """
        self.banking_ui.user_checking_balance_label.setText(f"${self.checking.get_balance():.2f}")
        self.banking_ui.user_savings_balance_label.setText(f"${self.savings.get_balance():.2f}")

    def transaction(self) -> None:
        """
        Handle deposit or withdrawal transactions.
        """
        amount = self.get_transaction_amount()
        if amount is None:
            return

        if self.banking_ui.deposit_button.isChecked():
            self.handle_deposit(amount)
        elif self.banking_ui.withdraw_button.isChecked():
            self.handle_withdraw(amount)
        else:
            self.banking_ui.validation_message_txt.setText("Select deposit or withdraw.")
            return

        self.update_balance_labels()
        self.banking_ui.amount_input.clear()

    def get_transaction_amount(self) -> float | None:
        """
        Validate and return transaction amount.
        """
        try:
            amount = float(self.banking_ui.amount_input.text().strip())
        except ValueError:
            self.banking_ui.validation_message_txt.setText("Enter a valid amount.")
            return None

        if amount <= 0:
            self.banking_ui.validation_message_txt.setText("Amount must be positive.")
            return None

        return amount

    def handle_deposit(self, amount: float) -> None:
        """
        Deposit funds into selected account.
        """
        if self.banking_ui.checking_button.isChecked():
            self.checking.deposit(amount)
            self.store_transaction(self.checking.get_username(), "Deposit", "Checking", amount, self.checking.get_balance())
            self.banking_ui.validation_message_txt.setText("Deposit successful.")

        elif self.banking_ui.savings_button.isChecked():
            self.savings.deposit(amount)
            self.store_transaction(self.savings.get_username(), "Deposit", "Savings", amount, self.savings.get_balance())
            self.banking_ui.validation_message_txt.setText("Deposit successful.")

    def handle_withdraw(self, amount: float) -> None:
        """
        Withdraw funds from selected account.
        """
        if self.banking_ui.checking_button.isChecked():
            if self.checking.withdraw(amount):
                self.store_transaction(self.checking.get_username(), "Withdraw", "Checking", amount, self.checking.get_balance())
                self.banking_ui.validation_message_txt.setText("Withdraw successful.")
            else:
                self.banking_ui.validation_message_txt.setText("Insufficient funds.")

        elif self.banking_ui.savings_button.isChecked():
            if self.savings.withdraw(amount):
                self.store_transaction(self.savings.get_username(), "Withdraw", "Savings", amount, self.savings.get_balance())
                self.banking_ui.validation_message_txt.setText("Withdraw successful.")
            else:
                self.banking_ui.validation_message_txt.setText("Insufficient funds.")

    def sign_out(self) -> None:
        """
        Return user to login screen.
        """
        self.banking_window.close()
        self.ui.username_input.clear()
        self.ui.password_input.clear()
        self.ui.feedback_txt.setText("")
        self.window.show()

    def store_transaction(self, username: str, action: str, account_type: str, amount: float, balance: float) -> None:
        """
        Log transaction to CSV file.
        """
        with open("transactions.csv", "a", newline="") as file:
            csv.writer(file).writerow([username, action, account_type, amount, balance])
