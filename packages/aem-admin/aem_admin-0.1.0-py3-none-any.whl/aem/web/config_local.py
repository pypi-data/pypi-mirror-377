import os
import logging

# Change pgAdmin data directory
DATA_DIR = 'C:\\Users\\talha\\Workspace\\AEM\\AEM Code\\.pgadmin_dev'

#Change pgAdmin server and port
DEFAULT_SERVER = '127.0.0.1'
DEFAULT_SERVER_PORT = 5051

# Switch between server and desktop mode
SERVER_MODE = True

#Change pgAdmin config DB path in case external DB is used.
CONFIG_DATABASE_URI="postgresql://postgres:admin@localhost:5432/postgres"

#Setup SMTP
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'user@gmail.com'
MAIL_PASSWORD = 'xxxxxxxxxx'

# Change log level
CONSOLE_LOG_LEVEL = logging.ERROR
FILE_LOG_LEVEL = logging.INFO

# Use a different config DB for each server mode.
if SERVER_MODE == False:
    SQLITE_PATH = os.path.join(
        DATA_DIR,
        'pgadmin4-desktop.db'
    )
else:
    SQLITE_PATH = os.path.join(
        DATA_DIR,
        'pgadmin4-server.db'
    )