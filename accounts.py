class Account:
    """
    Represents a basic bank account with deposit and withdrawal functionality.
    """

    def __init__(self, name: str, username: str, password: str, balance: float = 0) -> None:
        """
        Initialize an Account object.

        Args:
            name: Account holder's name.
            username: Account username (must be alphanumeric).
            password: Account password (must be alphanumeric).
            balance: Initial account balance (default is 0).
        """
        self.__name: str = name
        self.__balance: float = 0
        self.__username: str = ""
        self.__password: str = ""

        self.set_username(username)
        self.set_password(password)
        self.set_balance(balance)

    def set_balance(self, value: float) -> None:
        """
        Set the account balance.

        Args:
            value: New balance (negative values default to 0).
        """
        if value < 0:
            self.__balance = 0
        else:
            self.__balance = value

    def set_username(self, username: str) -> None:
        """
        Set the account username.

        Args:
            username: Username to assign.

        Raises:
            ValueError: If username is invalid.
        """
        if len(username) < 1 or not username.isalnum():
            raise ValueError("Username must be at least 1 character and alphanumeric")

        self.__username = username

    def set_password(self, password: str) -> None:
        """
        Set the account password.

        Args:
            password: Password to assign.

        Raises:
            ValueError: If password is invalid.
        """
        if len(password) < 1 or not password.isalnum():
            raise ValueError("Password must be at least 1 character and alphanumeric")

        self.__password = password

    def deposit(self, amount: float) -> bool:
        """
        Deposit money into the account.

        Args:
            amount: Amount to deposit.

        Returns:
            True if successful, False otherwise.
        """
        if amount > 0:
            self.set_balance(self.get_balance() + amount)
            return True
        return False

    def withdraw(self, amount: float) -> bool:
        """
        Withdraw money from the account.

        Args:
            amount: Amount to withdraw.

        Returns:
            True if successful, False otherwise.
        """
        if amount > 0 and amount <= self.get_balance():
            self.set_balance(self.get_balance() - amount)
            return True
        return False

    def get_balance(self) -> float:
        """
        Get current balance.

        Returns:
            Current account balance.
        """
        return self.__balance

    def get_name(self) -> str:
        """
        Get account holder name.

        Returns:
            Account holder's name.
        """
        return self.__name

    def get_username(self) -> str:
        """
        Get username.

        Returns:
            Account username.
        """
        return self.__username

    def get_password(self) -> str:
        """
        Get password.

        Returns:
            Account password.
        """
        return self.__password

    def set_name(self, value: str) -> None:
        """
        Set account holder name.

        Args:
            value: New name.
        """
        self.__name = value

    def __str__(self) -> str:
        """
        String representation of the account.

        Returns:
            Formatted account summary.
        """
        return f"Account name: {self.get_name()}, Account balance: {self.get_balance():.2f}"


class SavingAccount(Account):
    """
    A savings account with minimum balance and interest application.
    """

    minimum: float = 100
    rate: float = 0.02

    def __init__(
        self,
        name: str,
        username: str,
        password: str,
        balance: float = minimum,
        deposit_count: int = 0,
    ) -> None:
        """
        Initialize a SavingAccount.

        Args:
            name: Account holder's name.
            username: Account username.
            password: Account password.
            balance: Initial balance (default is minimum).
            deposit_count: Number of deposits made.
        """
        super().__init__(name, username, password, balance)
        self.__deposit_count: int = deposit_count

    def apply_interest(self) -> None:
        """
        Apply interest to the account balance.
        """
        interest: float = self.get_balance() * self.rate
        super().deposit(interest)

    def deposit(self, amount: float) -> bool:
        """
        Deposit funds and apply interest every 5 deposits.

        Args:
            amount: Amount to deposit.

        Returns:
            True if successful, False otherwise.
        """
        if amount <= 0:
            return False

        if super().deposit(amount):
            self.__deposit_count += 1

            if self.__deposit_count % 5 == 0:
                self.apply_interest()

            return True

        return False

    def withdraw(self, amount: float) -> bool:
        """
        Withdraw funds ensuring minimum balance is maintained.

        Args:
            amount: Amount to withdraw.

        Returns:
            True if successful, False otherwise.
        """
        if amount <= 0 or (self.get_balance() - amount) < self.minimum:
            return False

        return super().withdraw(amount)

    def set_balance(self, value: float) -> None:
        """
        Set balance ensuring it does not drop below minimum.

        Args:
            value: New balance.
        """
        if value < self.minimum:
            super().set_balance(self.minimum)
        else:
            super().set_balance(value)

    def __str__(self) -> str:
        """
        String representation of the savings account.

        Returns:
            Formatted account summary.
        """
        return super().__str__()
