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
            cur = sqlite3.connect("main.db").cursor()
            cur.execute("CREATE TABLE c4mainv1(uid, f_name, l_name, balance, "
                        "credit, address, dob, pass_hash, user_role)")
            while True:
                pw = getpass(prompt='Set an admin password: ')
                if pw == getpass(prompt='Confirm password: '):
                    break
                print("Passwords do not match. Please try again.")
            pass_hash = PasswordHasher().hash(pw)
            del pw
            cur.execute("INSERT INTO c4mainv1(uid, pass_hash, user_role)"
                        " VALUES (?, ?, ?)", (1, pass_hash, "admin"))
            cur.close()

        #create connection
        self.con = sqlite3.connect("main.db")
        self.cur = self.con.cursor()

        #check if the database is official
        a = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='c4mainv1'").fetchall()
        print(a)
        if a != [('c4mainv1',)]:
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
        sql = ("INSERT INTO c4mainv1 (uid, f_name, l_name, address, dob, pass_hash, "
               "balance, user_role)"
               " VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
        args = (uid, f_name, l_name, address, dob, pass_hash, balance, "user")
        self.cur.execute(sql, args)
        self.con.commit()
        print("success!!!!!")
        print(self.cur.execute(f"SELECT * FROM c4mainv1 WHERE uid={uid}").fetchall())
    def login(self):
        uid = (int(input("Enter your account number: ")),)
        pass_hash = self.cur.execute("SELECT PASS_HASH FROM c4mainv1 WHERE uid=?", uid).fetchone()[0]
        pw = getpass(prompt="Enter your password: ")
        try:
            print(PasswordHasher().verify(pass_hash, pw))
        except argon2.exceptions.VerifyMismatchError:
            print(False)