import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

CREATE_ALL_EACH_RUN = True if os.getenv("CREATE_ALL_EACH_RUN", "True") == "True" else False

DROP_ALL_EACH_RUN = True if os.getenv("DROP_ALL_EACH_RUN", "False") == "True" else False

DEBUG = True if os.getenv("DEBUG", "False") == "True" else False

SKIP_DATABASE_CONNECTION_TEST = True if os.getenv("SKIP_DATABASE_CONNECTION_TEST", "False") == "True" else False

CLOUD_ACCOUNT_ID = os.getenv("CLOUD_ACCOUNT_ID")

CLOUD_TOKEN = os.getenv("CLOUD_TOKEN")
