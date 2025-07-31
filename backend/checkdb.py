import psycopg
import time
from service import settings


class DB:
    def __init__(self):
        self.dbinfo = dict(HOST="postgres", PORT="5432")
        self.dbinfo.update(settings.DATABASES["default"])

    def open(self):
        connection = psycopg.connect(
            host=self.dbinfo["HOST"],
            port=self.dbinfo["PORT"],
            dbname=self.dbinfo["NAME"],
            user=self.dbinfo["USER"],
            password=self.dbinfo["PASSWORD"],
        )
        return connection

    def query(self, query):
        with self.open() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                results = list(cursor.fetchall())
        return results

    def wait(self, attempts=10):
        for _ in range(attempts):
            try:
                assert self.query("select 1") == [(1,)]
                return
            except psycopg.OperationalError:
                print("waiting for database")
                time.sleep(10)


db = DB()
db.wait()
