import sqlite3

from flask import g


def get_connection():
    connection = sqlite3.connect("database.db")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def execute(sql, params=()):
    connection = get_connection()

    try:
        result = connection.execute(sql, params)
        connection.commit()
        g.last_insert_id = result.lastrowid
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def query(sql, params=()):
    connection = get_connection()

    try:
        result = connection.execute(sql, params).fetchall()
        return result
    finally:
        connection.close()


def last_insert_id():
    return g.last_insert_id