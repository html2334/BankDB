import sqlite3
import secrets

import argon2.exceptions
from argon2 import PasswordHasher
from getpass import getpass
from datetime import date
from pathlib import Path

class Bank:
    def __init__(self):
        #startup sequence, create db if nonexistent
        print("WARNING: Ensure the database has either been created by the program"
              " or has been designed to the correct specification.")
        if not Path("main.db").is_file():
            if input("No database found, create new? (Y/N): ").upper() != "Y":
                raise Exception("Database not created.")
            open("main.db", "x")
            con = sqlite3.connect("main.db")
            cur = con.cursor()
            cur.execute("CREATE TABLE c4mainv1(uid, f_name, l_name, balance, "
                        "debt, max_loan, address, dob, pass_hash, user_role)")
            while True:
                pw = getpass(prompt='Set an admin password: ')
                if pw == getpass(prompt='Confirm password: '):
                    break
                print("Passwords do not match. Please try again.")
            pass_hash = PasswordHasher().hash(pw)
            del pw
            cur.execute("INSERT INTO c4mainv1(uid, f_name, pass_hash, user_role)"
                        " VALUES (?, ?, ?, ?)", (1, "Admin", pass_hash, "admin"))
            con.commit()
            cur.close()

        #create connection
        self.con = sqlite3.connect("main.db")
        self.cur = self.con.cursor()
        #role for determining whether permission granted, set upon login
        self.role = ""
        self.name = ""
        self.acc = None

        #check if the database is official
        a = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='c4mainv1'").fetchone()
        print(a)
        if a != ('c4mainv1',):
            self.cur.close()
            raise Exception("There is no table called c4mainv1, has the database been produced by the program?")
    def register(self):
        while True:
            uid = secrets.randbelow(100000000)
            a = self.cur.execute(f"SELECT 1 FROM c4mainv1 WHERE uid = {uid}").fetchone()
            if a is None:
                break
        f_name = input("What are your given name(s)? ")
        l_name = input("What is your surname? ")
        address = input("Enter your address: ")
        while True:
            try:
                bd = input("Enter your date of birth (DD/MM/YYYY): ").split("/")
                if len(bd) > 3 or int(bd[2]) < 1900:
                    raise Exception
                dob = date(int(bd[2]), int(bd[1]), int(bd[0]))
                break
            except:
                print("Invalid date")
        while True:
            pw = getpass(prompt='Set a password: ')
            if pw == getpass(prompt='Confirm password: '):
                break
            print("Passwords do not match. Please try again.")
        pass_hash = PasswordHasher().hash(pw)
        del pw
        balance = 0
        debt = 0
        max_loan = 500
        sql = ("INSERT INTO c4mainv1 (uid, f_name, l_name, address, dob, pass_hash, "
               "balance, debt, max_loan, user_role)"
               " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
        args = (uid, f_name, l_name, address,
                dob, pass_hash, balance, debt, max_loan, "user")
        print(f"You are now registered as account number {uid}")
        self.cur.execute(sql, args)
        self.con.commit()
    def login(self):
        try:
            self.acc = int(input("Enter your account number: "))
            pass_hash = self.cur.execute("SELECT pass_hash FROM c4mainv1 WHERE uid=?", (self.acc,)).fetchone()[0]
        except:
            print("Account does not exist.")
            return False
        pw = getpass(prompt="Enter your password: ")
        try:
            if PasswordHasher().verify(pass_hash, pw):
                del pass_hash, pw
                self.name = self.cur.execute("SELECT f_name FROM c4mainv1 WHERE uid=?", (self.acc,)).fetchone()[0]
                self.role = self.cur.execute("SELECT user_role FROM c4mainv1 WHERE uid=?", (self.acc,)).fetchone()[0]
                return True
        except argon2.exceptions.VerifyMismatchError:
            print("Incorrect password.")
            return False

    def edit(self):
        try:
            target = int(input("Select target account: "))
            a = self.cur.execute("SELECT 1 FROM c4mainv1 WHERE uid = ?", (target,)).fetchone()
            if a is None:
                print("Account does not exist.")
                return
        except ValueError:
            print("Invalid account.")
            return
        a = {
            "uid": int,
            "f_name": str,
            "l_name": str,
            "address": str,
            "dob": str,
            "pass_hash": str,
            "balance": float,
            "debt": float,
            "max_loan": float,
            "user_role": str,
        }
        print("""List of columns: {
            "uid": int,
            "f_name": str,
            "l_name": str,
            "address": str,
            "dob": str,
            "pass_hash": str,
            "balance": float,
            "debt": float,
            "max_loan": float,
            "user_role": str,
        }""")

        b = input("Select a column: ")
        if b in a:
            c = a[b](input("Insert new value: "))
            #yes it's using f strings, but it's validated so should be fine
            self.cur.execute(f"UPDATE c4mainv1 SET {b} = ? WHERE uid = ?",
                             (c, target))
            self.con.commit()
            print("Target successfully updated.")
        else:
            print("Invalid column.")

    def balance(self):
        bal = self.cur.execute("SELECT balance FROM c4mainv1 WHERE uid=?", (self.acc,)).fetchone()[0]
        print(f"You have ${bal} in your account.")


    def pay(self):
        try:
            target = int(input("Select target account: "))
            a = self.cur.execute("SELECT 1 FROM c4mainv1 WHERE uid = ?", (target,)).fetchone()
            if a is None:
                print("Account does not exist.")
                return
        except ValueError:
            print("Invalid account.")
            return
        a = self.cur.execute("SELECT 1 FROM c4mainv1 WHERE uid = ?", (target,)).fetchone()
        if a is None:
            print("Account does not exist.")
            return
        try:
            bal = self.cur.execute("SELECT balance FROM c4mainv1 WHERE uid=?", (self.acc,)).fetchone()[0]
            a = float(input("How much money to transfer? (no $ sign): "))
            if bal - a >= 0 and a > 0:
                self.cur.execute("UPDATE c4mainv1 SET balance = "
                                 "? WHERE uid = ?", (bal - a, self.acc))
                bal = self.cur.execute("SELECT balance FROM c4mainv1 WHERE uid=?", (target,)).fetchone()[0]
                self.cur.execute("UPDATE c4mainv1 SET balance = ?"
                                 "WHERE uid = ?", (bal + a, target))
                self.con.commit()
                print(f"Money successfully transferred to {target}")
            elif a <= 0:
                print("You must transfer a positive amount of money.")
            else:
                print("Not enough balance.")
        except ValueError:
            print("Invalid value.")

    def borrow(self):
        pass

    def pay_back(self):
        pass

    def increase_loan(self):
        """try:
            target = int(input("Select target account: "))
            a = self.cur.execute("SELECT 1 FROM c4mainv1 WHERE uid = ?", (target,)).fetchone()
            if a is None:
                print("Account does not exist.")
                return
        except ValueError:
            print("Invalid account.")
            return
        """
        pass