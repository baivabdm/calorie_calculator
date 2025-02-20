import sqlite3 as sql
import pandas as pd
from datetime import date, datetime as dt
from jinja2.filters import do_batch


class DbManagement:
    def __init__(self):
        self.connection = sql.connect(r".\planner.db")
        self.usersFetched = False
        self.cursor = self.connection.cursor()


    def fetch_users(self):
        self.userData = pd.read_sql("SELECT * FROM users", self.connection)
        self.user = self.userData["user"].tolist()
        self.names = self.userData["name"].tolist()

        self.usersFetched = True

    def get_user_list(self):
        if not self.usersFetched:
            self.fetch_users()

        return self.user

    def get_user_bio(self, user):
        sql = f"""
        SELECT * FROM users WHERE user = '{user}'
        """
        df = pd.read_sql(sql, self.connection)
        gender = df["gender"].iloc[0]
        dob = df["dob"].iloc[0]
        weight = df["weight"].iloc[0]
        height = df["height"].iloc[0]

        dob = dob.split("-")
        dob = date(int(dob[0]), int(dob[1]), int(dob[2]))
        age = int(((dt.today().date() - dob) / 365).days)

        gender = "Male" if gender == "M" else "Female"

        return gender, age, weight, height

    def update_user_weight_height(self, user, weight, height):
        sql = f"""
        UPDATE users
        SET weight = {weight},
            height = {height}
        WHERE
            user = '{user}'

        """
        self.cursor.execute(sql)

        self.connection.commit()


    def upload_dataframe(self, df: pd.DataFrame, table):
        df.to_sql(table, self.connection, if_exists="append", index=False)


    def close_connection(self):
        self.connection.close()