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
            elif a.upper() == ("X" or "EXIT"):
                raise Exception("Program terminated by user.")
        print(f"Welcome, {bank.name}!")
        while True:
            cmd = input("Enter a command: ")
            match cmd:
                case "help":
                    if bank.role == "user":
                        print("""You may run the commands:
                        balance
                        pay
                        borrow
                        pay_back
                        logout/exit""")
                    else:
                        print("Consult README or internal documents for"
                              "full list of commands")
                case "balance":
                    if bank.role != "admin":
                        bank.balance()
                case "pay":
                    if bank.role != "admin":
                        bank.pay()
                case "borrow":
                    if bank.role != "admin":
                        bank.borrow()
                case "pay_back":
                    if bank.role != "admin":
                        bank.pay_back()
                case "edit":
                    if bank.role != "admin":
                        print("Invalid command.")
                    else:
                        bank.edit()
                case "increase_loan":
                    if bank.role != ("admin" or "banker"):
                        print("Invalid command.")
                    else:
                        bank.increase_loan()
                case "logout":
                    print(f"Logged out of account {bank.acc}")
                    break
                case "exit":
                    print(f"Logged out of account {bank.acc}")
                    break
                case _:
                    print("Invalid command.")