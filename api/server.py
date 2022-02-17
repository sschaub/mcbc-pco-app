#!/usr/bin/env python
import os

from flask import Flask, Response, escape, request, jsonify, make_response


import requests
import logging
import re
import os
import os.path
import json
import uuid
import jwt
from functools import wraps
from  werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from threading import Thread
from utils import *
from db import *

# From https://www.geeksforgeeks.org/using-jwt-for-user-authentication-in-flask/
# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            token = token.split(' ')[1]
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            current_user = Person.query\
                .filter_by(userid = data['public_id'])\
                .first()
        except Exception as e:
            logging.warning(f'Unable to decode token: {e}')
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users context to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated

@app.route('/login', methods =['POST'])
def api_login():
    # creates dictionary of form data
    auth = request.json
  
    if not auth or not auth.get('username') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
        )
  
    user = Person.query\
        .filter_by(email = auth.get('username'))\
        .first()
  
    if not user or not check_password_hash(generate_password_hash('mcbc'), auth.get('password')):
        # returns 401 if user does not exist
        return jsonify({'error': 'Could not verify'}), 401
  
    if not user.userid:
        user.userid = str(uuid.uuid4())
        db.session.commit()

    # generate the JWT Token
    token = jwt.encode({
        'public_id': user.userid,
        'exp' : datetime.utcnow() + timedelta(days = 30)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token' : token, 'user': { 'user_type': user.user_type, 'email': user.email }}), 201

def get_upcoming_plans():
    plans = []
    for service_type_id, service_type_name in SERVICE_TYPES.items():
        url = BASE_SERVICE_TYPE_URL.format(service_type_id)
        r = requests.get(url, auth=(PCO_APP_ID, PCO_SECRET))
        for plan in r.json()['data']:
            plans.append([service_type_name, plan])
            
    return sorted(plans, key=lambda plan_tuple: plan_tuple[1]['attributes']['sort_date'])

@app.route('/services')
def api_services():

    def get_plans(url, service_type_name, service_type_id):
        logging.info(f'Getting plans for {url}')
        for plan in pco.iterate(url):
            plans.append([service_type_id, service_type_name, plan['data']])
        logging.info(f'Finished getting plans for {url}')

    threads = []
    plans = []
    for service_type_id, service_type_name in SERVICE_TYPES.items():
        url = BASE_SERVICE_TYPE_URL.format(service_type_id)

        t = Thread(target=get_plans, args=[url, service_type_name, service_type_id])
        t.start()
        threads.append(t)
        
    for t in threads:
        t.join()
                    
    services = list(
        { 'id': f"{service_type_id}-{plan['id']}", 'name': service_type_name + ' ' + plan['attributes']['dates'] }
        for (service_type_id, service_type_name, plan) in sorted(plans, key=lambda plan_tuple: plan_tuple[2]['attributes']['sort_date']))

    return jsonify(services)

@app.route('/service/<id>')
def api_service(id: str):
    service_type_id, plan_id = id.split('-')
    
    data = get_plan(service_type_id, plan_id)
    return jsonify(data)

@app.route('/service/<service_id>/<item_id>', methods=['GET'])
def api_service_item(service_id: str, item_id: str):
    service_type_id, plan_id = service_id.split('-')
    data = get_plan_item(int(service_type_id), int(plan_id), int(item_id))

    if data:
        item = data['item']
        if item['title'] == item['description']:
            item['title'] = ''
        sched_special = get_sched_special(service_type_id, plan_id, item)
        return jsonify({
            'item': item,
            'sched_item': sqlorm_object_as_dict(sched_special),
            'service': data['service']
        })

    return '{}'

@app.route('/service/<service_id>/<item_id>/edit', methods=['POST'])
@token_required
def api_begin_edit_service_item(current_user: Person, service_id: str, item_id: str):
    print(current_user)
    service_type_id, plan_id = service_id.split('-')
    data = get_plan_item(int(service_type_id), int(plan_id), int(item_id))

    if data:
        item = data['item']
        sched_item = begin_edit_item(service_type_id, plan_id, item)
        if item['title'] == item['description']:
            item['title'] = ''
        return jsonify({
            'service': data['service'],
            'item': item,
            'sched_item': sqlorm_object_as_dict(sched_item)             
        })
    else:
        return '{}'

@app.route('/service/<service_id>/<item_id>/approve', methods=['POST'])
@token_required
def api_approve_service_item(current_user: Person, service_id: str, item_id: str):
    if current_user.user_type != Person.USER_TYPE_ADMIN:
        return { 'result': 'Unauthorized' }, 401

    service_type_id, plan_id = service_id.split('-')    

    sched_spec = SchedSpecial.query.filter_by(
            service_type_id=service_type_id,
            plan_id=plan_id,
            item_id=item_id).first()

    url = f'/services/v2/service_types/{service_type_id}/plans/{plan_id}/items/{item_id}'
    templ = pco.template('Item', {'title': sched_spec.title})
    templ['data']['relationships'] = { }
    if sched_spec.song_id:
        templ['data']['relationships']['song'] = {
            'data': {
                'type': 'Song',
                'id': sched_spec.song_id
            }
        }
    if sched_spec.arrangement_id:
        templ['data']['relationships']['arrangement'] = {
            'data': {
                'type': 'Song',
                'id': sched_spec.arrangement_id
            }
        }
    
    pco.patch(url, templ)
    
    sched_spec.status = SchedSpecial.STATUS_APPROVED
    db.session.commit()    
    
    return { 'result': 'OK' }

@app.route('/service/<service_id>/<item_id>', methods=['POST'])
@token_required
def api_update_service_item(current_user: Person, service_id: str, item_id: str):
    service_type_id, plan_id = service_id.split('-')
    
    item_data = get_plan_item(int(service_type_id), int(plan_id), int(item_id))
    data = request.json
    logging.info(data)    

    if save_item(current_user, item_data, int(service_type_id), int(plan_id), int(item_id), 
        version_no=data.get('version_no'),
        song_id=data.get('song_id'), 
        arrangement_id=data.get('arrangement_id'),
        arrangement_name=data.get('arrangement_name'),
        title=data.get('title'), 
        copyright_year=data.get('copyright_year'), 
        copyright_holder=data.get('copyright_holder'), 
        author=data.get('author'), 
        translator=data.get('translator'), 
        composer=data.get('composer'), 
        arranger=data.get('arranger'), 
        genre_note=data.get('genre_note'), 
        solo_instruments=data.get('solo_instruments'), 
        accomp_instruments=data.get('accomp_instruments'), 
        other_performers=data.get('other_performers'), 
        staging_notes=data.get('staging_notes'), 
        song_text=data.get('song_text'),
        start_key=data.get('start_key'),
        end_key=data.get('end_key')):

        return { 'result': 'OK' }
    else:
        return { 'result': 'Record Changed' }

@app.route('/song_search')
def api_song_search():
    title = request.args['title']
    params = {
        'where[title]': title
    }
    songs = pco.get('/services/v2/songs', **params)
    song_list = [{
        'id': song['id'],
        'title': song['attributes']['title'],
        'author': song['attributes']['author'],
        'copyright': song['attributes']['copyright'],
    } for song in songs['data']]

    # for song in song_list:
    #     song['last_used'] = get_song_last_used(song['id'])

    song_list.sort(key=lambda song: song['title'])
    
    return jsonify(song_list)

@app.route('/song/<song_id>/arrangements')
def api_arrangements(song_id):
    url = '/services/v2/songs/{}/arrangements'.format(song_id)
    arr_list = []
    for arr in pco.iterate(url, per_page=50):
        copyright = ''
        notes = arr['data']['attributes']['notes']
        if notes:
            # Scan for a line indicating copyright
            notes_lines = notes.split('\n')
            for line in notes_lines:
                if line.startswith('Copyright'):
                    copyright = line
        arr_id = arr['data']['id']
        rows = list(db.session.execute("""
            select max(service_date) 
            from service join service_item on service.id = service_item.service_id
            where arrangement_id = :arr_id
            """, { 'arr_id': arr_id }))
        last_used = ''
        if len(rows):
            last_used = rows[0][0]
        arr_list.append({
            'id': arr_id,
            'name': arr['data']['attributes']['name'],
            'copyright': copyright,
            'lyrics': arr['data']['attributes']['lyrics'],
            'last_used': last_used
        })
    

    return jsonify(arr_list)

@app.route('/song/<song_id>/arrangements/<arr_id>')
def api_arrangement(song_id, arr_id):
    arr = get_arrangement(int(song_id), int(arr_id))

    return jsonify(arr)


@app.route('/menu')
def index():
    logging.info('Serving menu')
    return HTML_INDEX

@app.route('/')
def generate_html_schedule():
    return generate_schedule('html')

@app.route('/<format>')
def generate_schedule(format):

    if format not in ['html', 'html-admin', 'pdf']:
        return f'Invalid format requested: {format}'

    logging.info('Beginning monthly schedule generation')
    plans = get_upcoming_plans()
    last_updated_at = ''
    report_url = BASE_MONTHLY_REPORT_URL_PDF if format == 'pdf' else BASE_MONTHLY_REPORT_URL_HTML
    for (service_type_name, plan) in plans:
        planid = plan['id']
        if plan['attributes']['updated_at'] > last_updated_at:
            last_updated_at = plan['attributes']['updated_at']
        report_url += f"&{planid}_plan=true"

    report_url = report_url.format(planid)

    if format == 'html-admin':
        return flask.redirect(report_url)

    file_path = f'/tmp/schedule.{format}'
    regenerate = True
    if os.path.exists(file_path):
        modTimesinceEpoc = os.path.getmtime(file_path)
        modificationTime = datetime.utcfromtimestamp(modTimesinceEpoc).strftime('%Y-%m-%dT%H:%M:%SZ')
        logging.info(f"modificationTime = {modificationTime}, last_updated_at = {last_updated_at}")
        regenerate = modificationTime < last_updated_at

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

        # Generate report
        r = s.get(report_url)

        if format == 'pdf':
            if not DEV_SCHEDULE:
                with open(file_path, "wb") as f:
                    f.write(r.content)
            return Response(r.content, mimetype='application/pdf')
        else:
            if not DEV_SCHEDULE:
                with open(file_path, "w") as f:
                    f.write(r.text)
            return r.text

    else:

        if format == 'pdf':
            with open(file_path, "rb") as f:
                data = f.read()
            return Response(data, mimetype='application/pdf')
        else:
            with open(file_path) as f:
                data = f.read()
            return data

HTML_INDEX = '''
<html>
<body>
<h2>MCBC Music Plan Reports</h2>
<p><a href="pdf">Current Schedule (PDF)</a></p>
<p><a href="html">Current Schedule (HTML)</a></p>
<p><a href="html-admin">Current Schedule (PCO Login Required)</a></p>
<p><a href="serviceorder">Generate Service Orders (PCO Login Required)</a></p>

</body>
</html>
'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get("FLASK_SERVER_PORT", 9091), debug=True)
