import sqlite3
import pathlib


class DBHelper:
    def __init__(self):
        db_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "telegram_bot.db")
        self.db_connection = sqlite3.connect(db_path)
        self.db_cursor = self.db_connection.cursor()
        self.table = "telegram_bot"

    def select(self):
        pass

    def create_table(self, tbl_name):
        self.db_cursor.execute(f"""CREATE TABLE IF NOT EXISTS {tbl_name} (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    last_update_id
                                )""")

    def update_table(self, tbl_name):
        pass

    def update_last_id(self, id):
        self.db_cursor.execute(f"UPDATE {self.table} SET last_update_id='{id}' WHERE id=1")

    def insert_last_id(self, id):
        self.db_cursor.execute(f"INSERT INTO {self.table} (last_update_id) VALUES ({id})")

    def commit(self):
        self.db_connection.commit()

