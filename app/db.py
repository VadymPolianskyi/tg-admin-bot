import uuid
from datetime import datetime

import pymysql

from app.config import config

connection = pymysql.connect(
    host=config.DB_HOST,
    port=config.DB_PORT,
    user=config.DB_USERNAME,
    passwd=config.DB_PASSWORD,
    database=config.DB_NAME,
    cursorclass=pymysql.cursors.DictCursor)


class Strike:
    def __init__(self, reported_user_id: int, from_user_id: int, reason: str, id: str = None, time: datetime = None):
        self.id = uuid.uuid4() if not id else id
        self.reported_user_id = reported_user_id
        self.from_user_id = from_user_id
        self.reason = reason
        self.time = time


class Dao:
    def select_one(self, query, parameters):
        with connection.cursor() as cursor:
            sql_query = query.replace("'", "")
            print(f"Execute 'select_one' query: {sql_query}")
            print(f'Parameters: {parameters}')
            cursor.execute(sql_query, parameters)
            print("Successfully selected")
            return cursor.fetchone()

    def select_list(self, query, parameters) -> list:
        with connection.cursor() as cursor:
            sql_query = query.replace("'", "")
            cursor.execute(sql_query, parameters)
            print("Successfully selected")
            return cursor.fetchall()

    def execute(self, query, parameters):
        with connection.cursor() as cursor:
            sql_query = query.replace("'", "")
            cursor.execute(sql_query, parameters)
        connection.commit()


class StrikeDao(Dao):
    def __init__(self):
        self.__table = config.DB_TABLE_STRIKE

    def save(self, strike: Strike):
        query = f"INSERT INTO `{self.__table}` (`id`, `reported_user_id`, `from_user_id`, `reason`) VALUES (%s, %s, %s, %s);"
        self.execute(query, (strike.id, strike.reported_user_id, strike.from_user_id, strike.reason))

    def delete(self, reported_user_id: int, from_user_id: int):
        query = f"DELETE FROM `{self.__table}` WHERE reported_user_id=%s AND from_user_id=%s"
        self.execute(query, (reported_user_id, from_user_id))

    def find_all_by_reported_user_id(self, reported_user_id: int):
        print(f"Select all strikes for reported_user_id '{reported_user_id}")

        query = f"SELECT * FROM `{self.__table}` WHERE reported_user_id=%s;"
        result = self.select_list(query, reported_user_id)

        return [Strike(id=r['id'], reported_user_id=r['reported_user_id'], from_user_id=r['from_user_id'],
                       reason=r['reason'], time=r['time']) for r in result]

    def find_all_by_from_user_id(self, from_user_id: int):
        print(f"Select all strikes for from_user_id '{from_user_id}")

        query = f"SELECT * FROM `{self.__table}` WHERE from_user_id=%s;"
        result = self.select_list(query, from_user_id)

        return [Strike(id=r['id'], reported_user_id=r['reported_user_id'], from_user_id=r['from_user_id'],
                       reason=r['reason'], time=r['time']) for r in result]

    def find(self, id: str):
        query = f"SELECT * FROM `{self.__table}` WHERE id=%s"
        r = self.select_one(query, id)
        return Strike(id=r['id'], reported_user_id=r['reported_user_id'], from_user_id=r['from_user_id'],
                      reason=r['reason'], time=r['time'])

    def find_by_user_ids(self, reported_user_id: int, from_user_id: int):
        query = f"SELECT * FROM `{self.__table}` WHERE reported_user_id=%s AND from_user_id=%s;"
        r = self.select_one(query, (reported_user_id, from_user_id))
        if r:
            return Strike(id=r['id'], reported_user_id=r['reported_user_id'], from_user_id=r['from_user_id'],
                          reason=r['reason'], time=r['time'])
        else:
            return None
