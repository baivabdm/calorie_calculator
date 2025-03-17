import sqlite3 as sql
import pandas as pd
import numpy as np
from datetime import date, datetime as dt


class DbManagement:


    def __init__(self):
        self.connection = sql.connect(r".\planner.db")
        self.usersFetched = False
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
        user blob,
        name text,
        gender text,
        dob blob,
        weight real,
        height real
        )
        """)
        self.connection.commit()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
        user blob,
        date blob,
        food text,
        qty real,
        unit text,
        calorie real,
        carbs real,
        protein real,
        fat real,
        bmr real,
        weight real
        )
        """)
        self.connection.commit()


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
        name = df["name"].iloc[0]
        gender = df["gender"].iloc[0]
        dob = df["dob"].iloc[0]
        weight = df["weight"].iloc[0]
        height = df["height"].iloc[0]

        dob2 = dob.split("-")
        dob2 = date(int(dob2[0]), int(dob2[1]), int(dob2[2]))
        age = int(((dt.today().date() - dob2) / 365).days)

        gender = "Male" if gender == "M" else "Female"

        return name, gender, dob, age, weight, height


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


    def get_user_history(self, user, startDate=None, endDate=None):
        startDateCondition = ""
        endDateCondition = ""

        if startDate is not None:
            startDateCondition = f"AND date >= '{startDate}'"

        if endDate is not None:
            endDateCondition = f"AND date <= '{endDate}'"

        sql = f"""
        SELECT *
        FROM history
        WHERE user = '{user}'
        {startDateCondition}
        {endDateCondition}
        """

        datefoodlevel = pd.read_sql(sql, self.connection)
        datelevel = datefoodlevel.groupby(by=["date"], as_index=False).agg({"calorie": "sum",
                                                                            "carbs": "sum",
                                                                            "protein": "sum",
                                                                            "fat": "sum",
                                                                            "bmr":"mean",
                                                                            "weight":"mean"})
        value_cols = ["calorie", "carbs", "protein", "fat", "bmr", "weight"]
        for col in value_cols:
            datelevel[col] = datelevel[col].round(2)

        datefoodlevel = pd.melt(datefoodlevel, id_vars=["date", "food"],
                                value_vars=value_cols)
        datefoodlevel.rename(columns={"variable": "kpi"}, inplace=True)
        datefoodlevel["food"] = np.where(datefoodlevel["kpi"].isin(["bmr", "weight"]), pd.NaT, datefoodlevel["food"])

        datelevel["delta"] = (datelevel["calorie"]-datelevel["bmr"]).round(2)
        datelevelmelt = pd.melt(datelevel, id_vars=["date"],
                                value_vars=["calorie", "carbs", "protein", "fat", "bmr", "weight", "delta"])
        datelevelmelt.rename(columns={"variable": "kpi"}, inplace=True)

        return datefoodlevel.to_dict("records"), datelevel.to_dict("records"), datelevelmelt.to_dict("records")


    def add_user(self, username, name, gender, dob, weight, height):

        sql = f"""
        INSERT INTO users (user, name, gender, dob, weight, height)
        VALUES ('{username}', '{name}', '{gender}', '{dob}', {weight}, {height})
        """

        self.cursor.execute(sql)
        self.connection.commit()

    def modify_user(self, username, name, gender, dob, weight, height):

        sql = f"""
                UPDATE users
                SET 
                    name = '{name}',
                    gender = '{gender}',
                    dob = '{dob}',
                    weight = {weight},
                    height = {height}
                WHERE
                    user = '{username}'

                """
        self.cursor.execute(sql)

        self.connection.commit()

    def check_username_exists(self, username):

        sql = f"SELECT count(*) as user_count FROM users WHERE user = '{username}'"
        df = pd.read_sql(sql, self.connection)
        count = df["user_count"][0]

        if count == 1:
            return True
        else:
            return False

    def close_connection(self):
        self.connection.close()