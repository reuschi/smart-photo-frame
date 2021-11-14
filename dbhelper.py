import sqlite3
import pathlib
import module_log


class DBHelper:
    def __init__(self):
        db_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / "telegram_bot.db")
        self.db_connection = sqlite3.connect(db_path)
        self.db_cursor = self.db_connection.cursor()
        self.table = "telegram_bot"

    def select(self, command: str):
        return self.db_cursor.execute(command)

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

    def set_last_update_id(self, update_id, table):
        # To set last requested message id in the database
        try:
            # Build up the database connection and set the cursor to the current database
            module_log.log("Setting last update id in database...")

            if update_id is None:
                module_log.log("ID is None")
                update_id = 0

            # If there is no table in the database then create it first
            self.create_table(table)

            # Write the last update id into the database. If the value already exists just update the value of the field
            for row in self.select("SELECT EXISTS (SELECT last_update_id FROM telegram_bot WHERE id=1)"):
                if row[0] == 1:
                    self.update_last_id(update_id)
                    module_log.log(f"DB Update successful! ID: {update_id}")
                else:
                    self.insert_last_id(update_id)
                    module_log.log(f"DB Insert successful! ID: {update_id}")

            return True

        except sqlite3.Error as e:
            module_log.log(e)
        except Exception as e:
            module_log.log(sys.exc_info()[0] + ": " + sys.exc_info()[1])
        finally:
            self.commit()

    def commit(self):
        self.db_connection.commit()

    def close_connection(self):
        if self.db_connection:
            self.db_connection.commit()
            self.db_connection.close()

