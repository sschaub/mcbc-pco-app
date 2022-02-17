import os

# PCO basic authentication credentials
PCO_APP_ID = os.environ['PCO_APP_ID']
PCO_SECRET = os.environ['PCO_SECRET']
FLASK_SECRET_KEY = os.environ['FLASK_SECRET_KEY']

PCO_WEBAPP_LOGIN_USERNAME = os.environ['PCO_WEBAPP_LOGIN_USERNAME']
PCO_WEBAPP_LOGIN_PASSWORD = os.environ['PCO_WEBAPP_LOGIN_PASSWORD']

DB_PATH = os.environ.get("DB_PATH", '/tmp/mcbcmusic.sqlite3')

SENDGRID_API_KEY=os.environ['SENDGRID_API_KEY']
EMAIL_LIST=os.environ.get("EMAIL_LIST", "sschaub@gmail.com").split(',') # Personnel to receive special entry submissions
FROM_EMAIL_ADDR='admin@mcbcmusic.org'