import sqlite3

def get_conn():
    return sqlite3.connect("database.db", check_same_thread=False)