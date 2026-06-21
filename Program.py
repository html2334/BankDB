import Bank

class Program:
    @staticmethod
    def main():
        bank = Bank.Bank()
        while True:
            print("Welcome to the BankDB easy banking computer!")
            a = input("Do you have an existing account? (Y/N): ")
            if a.upper() == ("Y" or "YES"):
                if bank.login():
                    break
            elif a.upper() == ("N" or "NO"):
                bank.register()
        print(f"Welcome, {bank.name}!")
