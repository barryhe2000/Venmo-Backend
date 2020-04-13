import os
import sqlite3
from datetime import datetime

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

class DatabaseDriver(object):
    """
    Database driver for the Users app.
    Handles with reading and writing data with the database.
    """
    def __init__(self):
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        #self.conn.execute("PRAGMA foreign_keys = 1")
        self.create_users_table()
        self.create_txn_table()

    def create_users_table(self):
        try:
            self.conn.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    balance INTEGER
                );
            """)
        except Exception as e:
            print(e)

    def create_txn_table(self):
        try:
            self.conn.execute("""
                CREATE TABLE txn (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    sender_id INTEGER SECONDARY KEY NOT NULL,
                    receiver_id INTEGER SECONDARY KEY NOT NULL,
                    amount INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    accepted
                );
            """)
        except Exception as e:
            print(e)

    def get_txns_of_user(self, user_id):
        cursor = self.conn.execute('SELECT * FROM txn WHERE sender_id = ? OR receiver_id = ?', (user_id, user_id))
        txns = []
        for row in cursor:
            txns.append({'id':row[0], 'timestamp':row[1], 'sender_id':row[2], 'receiver_id':row[3], 'amount':row[4], 'message':row[5], 'accepted':row[6]})
        return txns

    #wrong
    def update_user_transactions(self, id, txn_id):
        t = get_txn(txn_id)
        lst = get_user_by_id(id).get("transactions")
        lst.append(t)
        self.conn.execute("""
            UPDATE users
            SET transactions = ?
            WHERE id = ?;
        """, (lst, id))
        self.conn.commit()

    def insert_txn_table(self, sender_id, receiver_id, amount, message, accepted=None):
        cursor = self.conn.cursor()
        cursor.execute(
        "INSERT INTO txn (timestamp, sender_id, receiver_id, amount, message, accepted) VALUES (?, ?, ?, ?, ?, ?);", (datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), sender_id, receiver_id, amount, message, accepted)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_txn(self, id): #id is the transaction id
        cursor = self.conn.execute("SELECT * FROM txn WHERE id = ?;", (id,))
        for row in cursor: #this part might be unnecessary (if else)
            a = row[6]
            if a is not None:
                a = bool(row[6])
            return {'id':row[0],'timestamp':row[1],'sender_id':row[2],'receiver_id':row[3],'amount':row[4],'message':row[5],'accepted':a}
        return None

    def delete_users_table(self):
        self.conn.execute("DROP TABLE IF EXISTS users;")

    def get_all_users(self):
        cursor = self.conn.execute('SELECT * FROM users;')
        lst = []
        for row in cursor:
            lst.append({'id': row[0], 'name': row[1], 'username': row[2]})
        return lst

    def insert_users_table(self, name, username, balance=0):
        cursor = self.conn.cursor()
        cursor.execute(
        "INSERT INTO users (name, username, balance) VALUES (?, ?, ?);", (name, username, balance)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_user_by_id(self, id):
        cursor = self.conn.execute("SELECT * FROM users WHERE id = ?;", (id,))
        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[3]}
        return None

    def update_txn_by_id(self, id, accepted):
        self.conn.execute("""
            UPDATE txn
            SET accepted = ?
            WHERE id = ?;
        """, (accepted, id))
        self.conn.commit()

    def update_time(self, id):
        self.conn.execute("""
            UPDATE txn
            SET timestamp = ?
            WHERE id = ?;
        """, (datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), id))
        self.conn.commit()

    def update_user_by_id(self, id, balance):
        self.conn.execute("""
            UPDATE users
            SET balance = ?
            WHERE id = ?;
        """, (balance, id))
        self.conn.commit()

    def delete_user_by_id(self, id):
        self.conn.execute("""
            DELETE FROM users
            WHERE id = ?;
        """, (id,))
        self.conn.commit()

DatabaseDriver = singleton(DatabaseDriver)
