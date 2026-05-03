class Account:
    
    def __init__(self, name, username, password, balance=0):
        self.__name = name
        self.__balance = 0
        self.__username = ''
        self.__password = ''
        
        self.set_username(username)
        self.set_password(password)
        self.set_balance(balance)
        
    def set_balance(self, value):
        if value < 0:
            self.__balance = 0
        else:
            self.__balance = value
            
    def set_username(self, username):
        if len(username) < 1 or not username.isalnum():
            raise ValueError("Username must be at least 1 character and alphanumeric")
        
        self.__username = username
        
    def set_password(self, password):
        if len(password) < 1 or not password.isalnum():
            raise ValueError("Password must be at least 1 character and alphanumeric")
        
        self.__password = password
            
    def deposit(self, amount):
        if amount > 0:
            self.set_balance(self.get_balance() + amount)
            return True
        return False
     
    def withdraw(self, amount):
        if amount > 0 and amount <= self.get_balance():
            self.set_balance(self.get_balance() - amount)
            return True
        return False
     
    def get_balance(self):
        return self.__balance
     
    def get_name(self):
        return self.__name

    def get_username(self):
        return self.__username
     
    def get_password(self):
        return self.__password
     
    def set_name(self, value):
        self.__name = value
         
    def __str__(self):
        return f'Account name: {self.get_name()}, Account balance: {self.get_balance():.2f}'


class SavingAccount(Account):
    
    minimum = 100
    rate = 0.02
         
    def __init__(self, name, username, password, balance=minimum, deposit_count=0):
        super().__init__(name, username, password, balance)
        self.__deposit_count = deposit_count
     
    def apply_interest(self):
        interest = self.get_balance() * self.rate
        super().deposit(interest)
        
    def deposit(self, amount):
        if amount <= 0:
            return False
        if super().deposit(amount):
            self.__deposit_count += 1
             
            if self.__deposit_count % 5 == 0:
                self.apply_interest()
            return True
     
        return False
     
    def withdraw(self, amount):
        if amount <= 0 or (super().get_balance() - amount) < self.minimum:
            return False
        return super().withdraw(amount)
         
    def set_balance(self, value):
        if value < self.minimum:
            super().set_balance(self.minimum)
        else:
            super().set_balance(value)
     
    def __str__(self):
        return f'{super().__str__()}'
