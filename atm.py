import sqlite3
from datetime import datetime

# =========================
# DATABASE CONNECTION
# =========================
conn = sqlite3.connect("bank.db")  # creates bank.db automatically
cursor = conn.cursor()

# =========================
# CREATE TABLES
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    account_number TEXT PRIMARY KEY,
    name TEXT,
    pin TEXT NOT NULL,
    balance REAL NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number TEXT,
    type TEXT,
    amount REAL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# =========================
# SAMPLE ACCOUNTS (Optional)
# =========================
def add_sample_accounts():
    accounts = [
        ("1001", "Adithya Bolla", "1234", 5000),
        ("1002", "Ravi Kumar", "5678", 10000)
    ]
    cursor.executemany("INSERT OR IGNORE INTO accounts VALUES (?, ?, ?, ?)", accounts)
    conn.commit()

add_sample_accounts()

# =========================
# LOGIN FUNCTION
# =========================
def login():
    print("===== WELCOME TO PYTHON BANK ATM =====")
    account_number = input("Enter account number: ")
    pin = input("Enter PIN: ")
    
    cursor.execute("SELECT * FROM accounts WHERE account_number=? AND pin=?", (account_number, pin))
    account = cursor.fetchone()
    
    if account:
        print(f"\nLogin successful! Welcome {account[1]}")
        return account_number
    else:
        print("\nInvalid account number or PIN")
        return None

# =========================
# ATM OPERATIONS
# =========================
def menu(account_number):
    while True:
        print("\n===== ATM MENU =====")
        print("1. Check Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transfer Money")
        print("5. Mini Statement")
        print("6. Exit")
        
        choice = input("Enter your choice: ")

        if choice == "1":
            cursor.execute("SELECT balance FROM accounts WHERE account_number=?", (account_number,))
            balance = cursor.fetchone()[0]
            print(f"Your balance: ₹{balance:.2f}")

        elif choice == "2":
            amount = float(input("Enter amount to deposit: ₹"))
            cursor.execute("UPDATE accounts SET balance = balance + ? WHERE account_number=?", (amount, account_number))
            cursor.execute("INSERT INTO transactions(account_number, type, amount) VALUES (?, 'Deposit', ?)", (account_number, amount))
            conn.commit()
            print("Deposit successful!")

        elif choice == "3":
            amount = float(input("Enter amount to withdraw: ₹"))
            cursor.execute("SELECT balance FROM accounts WHERE account_number=?", (account_number,))
            balance = cursor.fetchone()[0]
            if amount <= balance:
                cursor.execute("UPDATE accounts SET balance = balance - ? WHERE account_number=?", (amount, account_number))
                cursor.execute("INSERT INTO transactions(account_number, type, amount) VALUES (?, 'Withdrawal', ?)", (account_number, amount))
                conn.commit()
                print("Withdrawal successful!")
            else:
                print("Insufficient balance.")

        elif choice == "4":
            target_account = input("Enter recipient account number: ")
            amount = float(input("Enter amount to transfer: ₹"))
            cursor.execute("SELECT balance FROM accounts WHERE account_number=?", (account_number,))
            balance = cursor.fetchone()[0]
            cursor.execute("SELECT * FROM accounts WHERE account_number=?", (target_account,))
            recipient = cursor.fetchone()
            
            if recipient and amount <= balance:
                cursor.execute("UPDATE accounts SET balance = balance - ? WHERE account_number=?", (amount, account_number))
                cursor.execute("UPDATE accounts SET balance = balance + ? WHERE account_number=?", (amount, target_account))
                cursor.execute("INSERT INTO transactions(account_number, type, amount) VALUES (?, 'Transfer Sent', ?)", (account_number, amount))
                cursor.execute("INSERT INTO transactions(account_number, type, amount) VALUES (?, 'Transfer Received', ?)", (target_account, amount))
                conn.commit()
                print("Transfer successful!")
            else:
                print("Transfer failed. Check account number or balance.")

        elif choice == "5":
            cursor.execute("SELECT type, amount, date FROM transactions WHERE account_number=? ORDER BY date DESC LIMIT 5", (account_number,))
            transactions = cursor.fetchall()
            print("\n===== LAST 5 TRANSACTIONS =====")
            for t in transactions:
                print(f"{t[2]} | {t[0]} | ₹{t[1]:.2f}")

        elif choice == "6":
            print("Thank you for using Python Bank ATM. Goodbye!")
            break
        else:
            print("Invalid choice.")

# =========================
# MAIN FUNCTION
# =========================
def main():
    acc = login()
    if acc:
        menu(acc)

if __name__ == "__main__":
    main()
