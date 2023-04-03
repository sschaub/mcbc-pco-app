from flask import Flask, Response, escape, request
import flask

import requests
import logging
import time
import re
import os
import json
from datetime import datetime
from config import PCO_WEBAPP_LOGIN_USERNAME, PCO_WEBAPP_LOGIN_PASSWORD, REPORT_PATH
from utils import *
import const
import tempfile

REPORT_ID_SERVICE_ORDER = '117209'
REPORT_ID_SCHEDULE = '116671'

DEV_FORCE_REGENERATE_SCHEDULE = int(os.environ.get('DEV_FORCE_REGENERATE_SCHEDULE', 0))
DEV_SCHEDULE = int(os.environ.get('DEV_SCHEDULE', 0))

if DEV_SCHEDULE:
    REPORT_ID_SCHEDULE = '118339'  # Dev schedule


def generate_pdf():
    logging.info('Beginning monthly schedule generation')
    plans = get_all_services('future')
    last_updated_at = ''
    report_url = const.BASE_MONTHLY_REPORT_URL_PDF 
    for plan in plans:
        planid = plan['plan_id']
        if plan['updated_at'] > last_updated_at:
            last_updated_at = plan['updated_at']
        report_url += f"&{planid}_plan=true"

    report_url = report_url.format(planid)

    filename = os.path.join(REPORT_PATH, 'mcbcschedule.pdf')
    regenerate = True
    if os.path.exists(filename):
        mt = os.path.getmtime(filename)
        utc = datetime.utcfromtimestamp(mt)
        filename_date = utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        regenerate = filename_date < last_updated_at

    if DEV_FORCE_REGENERATE_SCHEDULE:
        regenerate = True
    if regenerate:
        logging.info("Schedule has changed, regenerating...")
        s = requests.Session()
        r = s.get('https://login.planningcenteronline.com/login/new')
        m = re.search(r'''name="authenticity_token" value="([^"]*)"''', r.text)
        auth_tok = m.group(1)

        # Login to planningcenter
        r = s.post('https://login.planningcenteronline.com/login', data={
            'authenticity_token': auth_tok,
            'login': PCO_WEBAPP_LOGIN_USERNAME,
            'password': PCO_WEBAPP_LOGIN_PASSWORD,
            'commit': 'Log In'
        })

        logging.info(report_url)
        # Generate report
        r = s.get(report_url)

        if not DEV_SCHEDULE:
            with open(filename, 'wb') as f:
                f.write(r.content)
        return Response(r.content, mimetype='application/pdf')

    else:
        with open(filename, 'rb') as f:
            data = f.read()

        return Response(data, mimetype='application/pdf')

