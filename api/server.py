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


        if not current_user:
            return jsonify({
                'message' : 'Token does not match record'
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
  
    valid_pw = user and (auth.get('password') == 'mcbc' or auth.get('password') == user.phone)
    if not valid_pw: # check_password_hash(generate_password_hash('mcbc'), auth.get('password')):
        # returns 401 if user does not exist
        return jsonify({'error': 'Could not verify'}), 401
  
    if not user.userid:
        user.userid = str(uuid.uuid4())
        db.session.commit()

    # generate the JWT Token
    token = jwt.encode({
        'public_id': user.userid,
        'exp' : datetime.utcnow() + timedelta(days = 365)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token' : token, 'user': { 'user_type': user.user_type, 'email': user.email }}), 201

@app.route('/password_reminder', methods =['POST'])
def api_password_reminder():
    username = request.json.get('username')
    if username:
        user = Person.query\
            .filter_by(email = username)\
            .first()

        if user:
            password = user.phone
            if not user.phone:
                password = 'mcbc'
            msg = f'''
            <html><body>
            Your password is: {password}<br>
            <a href="https://app.mcbcmusic.org/login">Login now</a>
            </body></html>
            '''
            send_email('Password Reminder', msg, toEmails=[user.email])
            return 'Check your email for a password reminder. You may need to check your junk folder.'

    return 'If your email was recognized, a password reminder was sent.'

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
        for plan in pco.iterate(url):
            plans.append([service_type_id, service_type_name, plan['data']])

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
        { 'id': f"{service_type_id}-{plan['id']}", 'name': service_type_name + ' ' + plan['attributes']['dates'], 
            'service_date': plan['attributes']['dates'], 'service_type': service_type_name, 'plan_theme': plan['attributes']['title'] }
        for (service_type_id, service_type_name, plan) in sorted(plans, key=lambda plan_tuple: plan_tuple[2]['attributes']['sort_date']))

    return jsonify(services)

@app.route('/services/<id>')
def api_service(id: str):
    service_type_id, plan_id = id.split('-')
    
    data = get_plan(service_type_id, plan_id)
    return jsonify(data)

@app.route('/services/<service_id>/recommended_songs', methods=['GET'])
def api_service_recommended_songs(service_id: str):
    service_type_id, plan_id = service_id.split('-')

    tag_ids = [str(tag.tag_id) for tag in ServiceTag.query.filter_by(service_type_id=service_type_id, plan_id=plan_id)]

    if len(tag_ids):
        data = get_songs({
            'where[song_tag_ids]': ','.join(tag_ids),        
        })
    else:
        data = []

    return jsonify(data)

@app.route('/services/<service_id>/tags', methods=['POST'])
@token_required
def api_update_service_tags(current_user: Person, service_id: str):
    if current_user.user_type != Person.USER_TYPE_ADMIN:
        return { 'result': 'Unauthorized' }, 401

    service_type_id, plan_id = service_id.split('-')

    tags = request.json['tags']

    db.session.execute('''delete from service_tag where service_type_id = :service_type_id and plan_id = :plan_id''',
        { 'service_type_id': service_type_id, 'plan_id': plan_id })

    for tag_id in tags:
        db.session.add(ServiceTag(service_type_id=service_type_id, plan_id=plan_id, tag_id=tag_id))

    db.session.commit()

    return { 'result': 'OK' }

@app.route('/services/<service_id>/<item_id>', methods=['GET'])
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

@app.route('/services/<service_id>/<item_id>', methods=['POST'])
@token_required
def api_update_service_item(current_user: Person, service_id: str, item_id: str):
    service_type_id, plan_id = service_id.split('-')
    
    item_data = get_plan_item(int(service_type_id), int(plan_id), int(item_id))
    data = request.json
    item_new_data = data['item']
    do_send_email = data['sendEmail']

    if save_item(current_user, item_data, int(service_type_id), int(plan_id), int(item_id), 
        version_no=item_new_data.get('version_no'),
        song_id=item_new_data.get('song_id'), 
        arrangement_id=item_new_data.get('arrangement_id'),
        arrangement_name=item_new_data.get('arrangement_name'),
        title=item_new_data.get('title'), 
        copyright_year=item_new_data.get('copyright_year'), 
        copyright_holder=item_new_data.get('copyright_holder'), 
        author=item_new_data.get('author'), 
        translator=item_new_data.get('translator'), 
        composer=item_new_data.get('composer'), 
        arranger=item_new_data.get('arranger'), 
        genre_note=item_new_data.get('genre_note'), 
        solo_instruments=item_new_data.get('solo_instruments'), 
        accomp_instruments=item_new_data.get('accomp_instruments'), 
        other_performers=item_new_data.get('other_performers'), 
        staging_notes=item_new_data.get('staging_notes'), 
        ministry_location=item_new_data.get('ministry_location'), 
        song_text=item_new_data.get('song_text'),
        start_key=item_new_data.get('start_key'),
        end_key=item_new_data.get('end_key'),
        do_send_email=do_send_email):

        return { 'result': 'OK' }
    else:
        return { 'result': 'Record Changed' }

@app.route('/services/<service_id>/<item_id>/edit', methods=['POST'])
@token_required
def api_begin_edit_service_item(current_user: Person, service_id: str, item_id: str):
    service_type_id, plan_id = service_id.split('-')
    data = get_plan_item(int(service_type_id), int(plan_id), int(item_id))

    if data:
        item = data['item']
        sched_item = begin_edit_item(service_type_id, plan_id, item)
        
        return jsonify({
            'service': data['service'],
            'item': item,
            'sched_item': sqlorm_object_as_dict(sched_item)             
        })
    else:
        return '{}'

@app.route('/services/<service_id>/<item_id>/approve_copyright', methods=['POST'])
@token_required
def api_approve_copyright(current_user: Person, service_id: str, item_id: str):
    if current_user.user_type != Person.USER_TYPE_ADMIN:
        return { 'result': 'Unauthorized' }, 401

    service_type_id, plan_id = service_id.split('-')    
    sched_spec = SchedSpecial.query.filter_by(
            service_type_id=service_type_id,
            plan_id=plan_id,
            item_id=item_id).first()

    sched_spec.copyright_license_status = SchedSpecial.COPYRIGHT_STATUS_APPROVED
    db.session.commit()

    return 'OK'

@app.route('/services/<service_id>/<item_id>/approve', methods=['POST'])
@token_required
def api_approve_service_item(current_user: Person, service_id: str, item_id: str):
    if current_user.user_type != Person.USER_TYPE_ADMIN:
        return { 'result': 'Unauthorized' }, 401

    service_type_id, plan_id = service_id.split('-')    

    sched_spec = SchedSpecial.query.filter_by(
            service_type_id=service_type_id,
            plan_id=plan_id,
            item_id=item_id).first()

    pco_assign_song_to_plan_item(item_id, service_type_id, plan_id, sched_spec)
    
    sched_spec.status = SchedSpecial.STATUS_APPROVED
    db.session.commit()    
    
    return { 'result': 'OK' }

def pco_assign_song_to_plan_item(item_id, service_type_id, plan_id, sched_spec):
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

@app.route('/services/<service_id>/<item_id>/import', methods=['POST'])
@token_required
def api_import_service_item(current_user: Person, service_id: str, item_id: str):
    if current_user.user_type != Person.USER_TYPE_ADMIN:
        return { 'result': 'Unauthorized' }, 401

    service_type_id, plan_id = service_id.split('-')    

    sched_spec = SchedSpecial.query.filter_by(
            service_type_id=service_type_id,
            plan_id=plan_id,
            item_id=item_id).first()

    if not sched_spec:
        return { 'result': 'Not found' }, 404

    data = request.json
    import_arrangement_name = data['import_arrangement_name']

    url = f'/services/v2/service_types/{service_type_id}/plans/{plan_id}/items/{item_id}'

    authors = []
    if sched_spec.author:
        authors.append(f"{sched_spec.author} (text)")
    if sched_spec.composer:
        authors.append(f"{sched_spec.composer} (tune)")
    author = ', '.join(authors)
    copyright = ''
    if sched_spec.copyright_year:
        copyright = f'Copyright {sched_spec.copyright_year} '
    if sched_spec.copyright_holder:
        copyright += sched_spec.copyright_holder

    song_attrs = {        
        'title': sched_spec.title,
        'author': author
    }
    if not sched_spec.song_id:
        # Only do copyright for a new song (don't want to override song-wide copyright for existing song)
        song_attrs['copyright'] = copyright
    payload = pco.template('Song', song_attrs)

    if sched_spec.song_id:
        new_song = False
        song = pco.patch(f'/services/v2/songs/{sched_spec.song_id}', payload)
    else:
        new_song = True
        song = pco.post('/services/v2/songs', payload)
        sched_spec.song_id = song['data']['id']
        arrangements = pco.get(f'/services/v2/songs/{sched_spec.song_id}/arrangements')
        arrangement = arrangements['data'][0]
        sched_spec.arrangement_id = arrangement['id']

    sched_spec.arrangement_name = import_arrangement_name
    if sched_spec.arrangement_id and not new_song:
        arrangement = pco.get(f'/services/v2/songs/{sched_spec.song_id}/arrangements/{sched_spec.arrangement_id}')
        notes = arrangement['data']['attributes']['notes'] or ''
    else:
        notes = ''
        
    arr_attrs = {
        'name': sched_spec.arrangement_name,
    }
    if sched_spec.song_text:
        arr_attrs['chord_chart'] = sched_spec.song_text
        arr_attrs['chord_chart_key'] = 'C'

    notes_lines = notes.split('\n')
    # Remove lines from notes that contain information we're going to add
    notes_lines = [line for line in notes_lines if line and not (
        line.startswith('Arranger:') or line.startswith('Copyright') or line.startswith('Translator:')
        or line.startswith('Author:') or line.startswith('Composer')
        )]
    if sched_spec.arranger:
        notes_lines.append(f'Arranger: {sched_spec.arranger}')
    if sched_spec.translator:
        notes_lines.append(f'Translator: {sched_spec.translator}')
    if sched_spec.author:
        notes_lines.append(f'Author: {sched_spec.author}')
    if sched_spec.composer:
        notes_lines.append(f'Composer: {sched_spec.composer}')
    if copyright:
        notes_lines.append(f'{copyright}')

    arr_attrs['notes'] = '\n'.join(notes_lines)    
    payload = pco.template('Arrangement', arr_attrs)

    if sched_spec.arrangement_id:
        pco.patch(f'/services/v2/songs/{sched_spec.song_id}/arrangements/{sched_spec.arrangement_id}', payload)
    else:
        arrangement = pco.post(f'/services/v2/songs/{sched_spec.song_id}/arrangements', payload)
        sched_spec.arrangement_id = arrangement['data']['id']

    db.session.commit()

    pco_assign_song_to_plan_item(item_id, service_type_id, plan_id, sched_spec)    

    return { 'result': 'OK', 'song_id': sched_spec.song_id, 'arrangement_id': sched_spec.arrangement_id, 'arrangement_name': sched_spec.arrangement_name }

@app.route('/song_search')
def api_song_search():

    song_list = get_songs({
        'where[title]': request.args['title']
    })
    
    return jsonify(song_list)

@app.route('/songs/<song_id>/arrangements')
def api_arrangements(song_id):
    url = '/services/v2/songs/{}/arrangements'.format(song_id)
    arr_list = []
    for arr in pco.iterate(url, per_page=50):
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
            'last_used': last_used
        })
    
    return jsonify(arr_list)

@app.route('/songs/<song_id>/arrangements/<arr_id>')
def api_arrangement(song_id, arr_id):
    arr = get_arrangement(int(song_id), int(arr_id))

    return jsonify(arr)

@app.route('/songs/<song_id>')
def api_song(song_id):
    song = get_song(int(song_id))

    return jsonify(song)

@app.route('/tags')
def api_tags():
    tags = [sqlorm_object_as_dict(tag) for tag in SongTag.query.all()]
    
    return jsonify(tags)


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
