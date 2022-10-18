""" Module with Database functions """

import sqlite3
import pathlib
import sys

import module_log


class DBHelper:
    """ DBHelper Class """

    def __init__(self, table: str):
        str_table = table + ".db"
        db_path = pathlib.Path(pathlib.Path(__file__).parent.absolute() / str_table)
        self.db_connection = sqlite3.connect(db_path)
        self.db_cursor = self.db_connection.cursor()
        self.table = table

    def select(self, command: str):
        """ Run a SELECT command on database """
        return self.db_cursor.execute(command)

    def create_table(self):
        """ Create a specific table in database """
        self.db_cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.table} (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    last_update_id
                                )""")

    def update_table(self, tbl_name: str):
        """ Update a specific table in database """

    def update_last_id(self, index: int):
        """ Update last message id in database """
        self.db_cursor.execute(f"UPDATE {self.table} SET last_update_id='{index}' WHERE id=1")

    def insert_last_id(self, index: int):
        """ Insert last message id in database """
        self.db_cursor.execute(f"INSERT INTO {self.table} (last_update_id) VALUES ({index})")

    def set_last_update_id(self, update_id):
        """ To set last requested message id in the database """
        try:
            # Build up the database connection and set the cursor to the current database
            module_log.log("Setting last update id in database...")

            if update_id is None:
                module_log.log("ID is None")
                update_id = 0

            # If there is no table in the database then create it first
            self.create_table()

            # Write the last update id into the database.
            # If the value already exists just update the value of the field
            for row in self.select(f"SELECT EXISTS (SELECT last_update_id FROM "
                                   f"{self.table} WHERE id=1)"):
                if row[0] == 1:
                    self.update_last_id(update_id)
                    module_log.log(f"DB Update successful! ID: {update_id}")
                else:
                    self.insert_last_id(update_id)
                    module_log.log(f"DB Insert successful! ID: {update_id}")

            return True

        except sqlite3.Error as exc:
            module_log.log(exc)
        except Exception:
            module_log.log(sys.exc_info()[0] + ": " + sys.exc_info()[1])
        finally:
            self.commit()

        return False

    def get_last_update_id(self):
        """
        To only receive the newest message since the last request it's necessary to send
        an offset id in the request.
        This information is stored in the database and will be gathered by this function.
        """
        try:
            module_log.log("Getting last update id from database...")
            update_id = None

            # Get last update id from database
            for row in self.select("SELECT last_update_id FROM telegram_bot WHERE id=1"):
                update_id = row[0]

            if update_id is not None:
                module_log.log(f"Done. Last Update ID is: {update_id}")
                return update_id

        except sqlite3.Error as exc:
            module_log.log(exc)
            if "no such table" in str(exc):
                self.set_last_update_id(0)
        except sqlite3.OperationalError as exc:
            module_log.log(exc)
        else:
            module_log.log("Failed!")

        return False

    def commit(self):
        """ Commit changes in database """
        self.db_connection.commit()

    def close_connection(self):
        """ Close connection to database """
        if self.db_connection:
            self.db_connection.commit()
            self.db_connection.close()
