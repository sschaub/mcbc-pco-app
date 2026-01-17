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

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
# To get the DATASOURCE_ID, in Notion, go to the database > View Settings > Manage Data sources > Copy DataSource ID
NOTION_CHORAL_DATASOURCE_ID = "14c7a5a5-9ce8-4987-b31b-568e5700cb68"
NOTION_INSTRUMENTAL_DATASOURCE_ID = "b6cfbb85-9eb6-425c-8295-8bff55bb8487"
