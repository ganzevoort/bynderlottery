import os
import psycopg
import subprocess
import time
from service import settings


def find_pgdump_file(dumpdir="/pgdumps"):
    try:
        dumpfiles = [
            os.path.join(dumpdir, f)
            for f in os.listdir(dumpdir)
            if f.endswith(".dump")
        ]
        if dumpfiles:
            return max(dumpfiles, key=lambda f: os.stat(f).st_mtime)
    except FileNotFoundError:
        print(f"Dump directory {dumpdir} not found, skipping dump restoration")
        return None


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

    def restore(self, dumpfile):
        restorecmd = """
            pg_restore
                --host={HOST} --port={PORT} --user={USER}
                --dbname={NAME}
                --no-owner --no-acl --single-transaction
                --schema=public
                {dumpfile}
            """
        argv = [
            w.format(dumpfile=dumpfile, **self.dbinfo)
            for w in restorecmd.split()
        ]
        print("pg_restore ... {dumpfile}".format(dumpfile=dumpfile))
        os.environ["PGPASSWORD"] = self.dbinfo["PASSWORD"]
        subprocess.run(argv, check=True)


db = DB()
db.wait()
try:
    db.query("select count(*) from auth_user")
except psycopg.errors.UndefinedTable:
    dumpfile = find_pgdump_file()
    if dumpfile:
        db.restore(dumpfile)
