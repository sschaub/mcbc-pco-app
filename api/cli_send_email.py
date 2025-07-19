import sys

from db import *
from config import SENDPULSE_CLIENT_ID, SENDPULSE_SECRET


import requests

resp = requests.post("https://api.sendpulse.com/oauth/access_token", json={
   "grant_type":"client_credentials",
   "client_id":SENDPULSE_CLIENT_ID,
   "client_secret":SENDPULSE_SECRET
})

access_token = resp.json()["access_token"]

resp = requests.post("https://api.sendpulse.com/smtp/emails", headers = {
    "Authorization": f"Bearer {access_token}"}, json={
  "email": {
    "text": "Example text",
    "subject": "Example subject",
    "from": {
      "name": "MCBC Music",
      "email": "admin@mcbcmusic.org"
    },
    "to": [
      {
        "name": "Stephen Schaub",
        "email": "sschaub@gmail.com"
      }
    ]
  }
})
print(resp.text)
resp.raise_for_status()