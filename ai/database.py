import sqlite3
import time

class FallDatabase:

    def __init__(self):
        self.conn = sqlite3.connect("fall_history.db", check_same_thread=False)
        self.create_table()

    def create_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS falls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            posture TEXT,
            score REAL,
            image_path TEXT
        )
        """)
        self.conn.commit()

    def insert_fall(self, posture, score, image_path):
        self.conn.execute("""
        INSERT INTO falls (timestamp, posture, score, image_path)
        VALUES (?, ?, ?, ?)
        """, (
            time.strftime("%Y-%m-%d %H:%M:%S"),
            posture,
            score,
            image_path
        ))
        self.conn.commit()