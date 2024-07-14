from time import sleep

import app.logger as log
import app.settings as settings
from sqlalchemy import text


def wait(engine):
    if settings.SKIP_DATABASE_CONNECTION_TEST is False:
        success = 0
        for i in range(30):
            sleep(2)
            try:
                 with engine.connect() as connection:
                    connection.execute(text("select 1"))
            except Exception:
                log.info("Waiting for database.")
            else:
                success += 1
                log.info("Database connection tested.")
            if success == 3:
                log.info("Connection with database established.")
                break
