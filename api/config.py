import os

# PCO basic authentication credentials
PCO_APP_ID = os.environ['PCO_APP_ID']
PCO_SECRET = os.environ['PCO_SECRET']
FLASK_SECRET_KEY = os.environ['FLASK_SECRET_KEY']

PCO_WEBAPP_LOGIN_USERNAME = os.environ['PCO_WEBAPP_LOGIN_USERNAME']
PCO_WEBAPP_LOGIN_PASSWORD = os.environ['PCO_WEBAPP_LOGIN_PASSWORD']

DB_PATH = os.environ.get("DB_PATH", '/tmp/mcbcmusic.sqlite3')
REPORT_PATH = os.environ.get("REPORT_PATH", '/tmp')

ALL_EMAIL_LIST = os.environ.get("ALL_EMAIL_LIST", "sschaub@gmail.com").split(',') # Personnel to receive special entry submissions
INITIAL_EMAIL_LIST = os.environ.get("INITIAL_EMAIL_LIST", "sschaub@gmail.com").split(',') # Personnel to receive initial special entry submissions
FROM_EMAIL_ADDR = 'admin@mcbcmusic.org'
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

SENDPULSE_SMTP_SERVER = "smtp-pulse.com"
SENDPULSE_SMTP_PORT = 465
SENDPULSE_SMTP_USERNAME = os.environ['SENDPULSE_SMTP_USERNAME']
SENDPULSE_SMTP_PASSWORD = os.environ['SENDPULSE_SMTP_PASSWORD']
