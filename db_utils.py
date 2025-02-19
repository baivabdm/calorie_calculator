import sqlite3 as sql
import pandas as pd

class DbManagement:
    def __init__(self):
        self.connection = sql.connect(r".\planner.db")
        self.usersFetched = False


    def fetch_users(self):
        self.userData = pd.read_sql("SELECT * FROM users", self.connection)
        self.user = self.userData["user"].tolist()
        self.names = self.userData["name"].tolist()

        self.usersFetched = True

    def get_user_list(self):
        if not self.usersFetched:
            self.fetch_users()

        return self.user


    def upload_dataframe(self, df: pd.DataFrame, table):
        df.to_sql(table, self.connection, if_exists="append", index=False)


    def close_connection(self):
        self.connection.close()