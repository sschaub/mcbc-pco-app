#!/usr/bin/env python
import os

from flask import Response, request, jsonify, make_response, redirect
from flask_cors import cross_origin
from pypco import PCORequestException
from werkzeug.exceptions import HTTPException
import logging
import os.path
import json
import uuid
import jwt
from functools import wraps
from datetime import datetime, timedelta
from utils import *
from db import *
import schedule
import const
import config

@cross_origin()
@app.errorhandler(Exception)
def ise_handler(e):
    if isinstance(e, PCORequestException):
        # e.response_body is something like {"errors":[{"detail":"has already been taken","status":"422","title":"Validation Error","source":{"parameter":"title"},"meta":{"resource":"Song","associated_resources":[]}}]}
        logging.exception(f'PCO Request Exception: {e.status_code}\n-\n{e.message}\n-\n{e.response_body}')
        try:
            json_error = json.loads(e.response_body)
            error = json_error['errors'][0]
            msg = error['title'] + ': ' + error['source']['parameter'] + ' ' + error['detail']
        except:
            msg = e.response_body
        return { 'result': 'Error', 'error': msg }, e.status_code
    elif isinstance(e, HTTPException):
        return { 'result': 'Error', 'error': e.description }, e.code
    else:
        logging.exception(f'Unhandled Exception:')
        return { 'result': 'Error', 'error': str(e) }, 500



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


@app.route('/services')
def api_services():
    when = request.args.get('when', 'future')
    if when == 'past':
        after_date = datetime.today() - timedelta(days=62)
        after_date_str = after_date.strftime('%Y-%m-%d')
        when = f'after,past&after={after_date_str}'
    services = get_all_services(when)

    return jsonify(services)

@app.route('/my-services')
@token_required
def api_my_services(current_user: Person):
    all_services = get_all_services('future')

    my_plan_persons = pco.get(f'/services/v2/people/{current_user.id}/plan_people?include=plan')

    plan_ids = [plan_person['relationships']['plan']['data']['id'] for plan_person in my_plan_persons['data']]

    my_services = [service for service in all_services if service['plan_id'] in plan_ids]
    
    return jsonify(my_services)    

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
    email_type = int(data['emailType'])
    copyright_holder=item_new_data.get('copyright_holder')
    if copyright_holder == 'Other':
        copyright_holder=item_new_data.get('copyright_holder_other')

    if save_item(current_user, item_data, int(service_type_id), int(plan_id), int(item_id), 
        version_no=item_new_data.get('version_no'),
        details_provided=item_new_data.get('details_provided'),
        song_id=item_new_data.get('song_id'), 
        arrangement_id=item_new_data.get('arrangement_id'),
        arrangement_name=item_new_data.get('arrangement_name'),
        title=item_new_data.get('title'), 
        copyright=item_new_data.get('copyright'), 
        copyright_year=item_new_data.get('copyright_year'), 
        copyright_holder=copyright_holder,
        ccli_num=item_new_data.get('ccli_num'), 
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
        email_type=email_type):

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

        copyright_holders = sorted(pub.publisher_name for pub in LicensedPublishers.query.all())
        
        return jsonify({
            'service': data['service'],
            'item': item,
            'sched_item': sqlorm_object_as_dict(sched_item),
            'copyright_holders': copyright_holders
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

@app.route('/services/<service_id>/<item_id>/reset', methods=['POST'])
@token_required
def api_reset_service_item(current_user: Person, service_id: str, item_id: str):
    if current_user.user_type != Person.USER_TYPE_ADMIN:
        return { 'result': 'Unauthorized' }, 401

    service_type_id, plan_id = service_id.split('-')

    sched_spec = SchedSpecial.query.filter_by(
            service_type_id=service_type_id,
            plan_id=plan_id,
            item_id=item_id).first()

    db.session.delete(sched_spec)
    db.session.commit()

    url = f'/services/v2/service_types/{service_type_id}/plans/{plan_id}/items/{item_id}'

    templ = pco.template('Item', { 'title': sched_spec.description })

    templ['data']['relationships'] = { }
    if sched_spec.song_id:
        templ['data']['relationships']['song'] = {
            'data': None
        }
    if sched_spec.arrangement_id:
        templ['data']['relationships']['arrangement'] = {
            'data': None
        }
    
    pco.patch(url, templ)    

    return { 'result': 'OK' }


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
        return { 'result': 'Fail', 'error': 'Unexpected error: Invalid scheduled special ID' }, 404

    # A new song has no song id
    new_song = not sched_spec.song_id

    data = request.json
    import_arrangement_name = data['import_arrangement_name']
    import_service_order_note = data['import_service_order_note']

    sched_spec.solo_instruments = import_service_order_note

    copyright = sched_spec.copyright    

    song_attrs = {        
        'title': sched_spec.title,
    }

    if new_song:
        # Only do copyright and author info for a new song 
        # (don't want to override song-wide copyright/author for existing song)
        
        if copyright:
            song_attrs['copyright'] = copyright

        authors = []
        if sched_spec.author:
            authors.append(f"{sched_spec.author} (text)")
        if sched_spec.composer:
            authors.append(f"{sched_spec.composer} (tune)")
        author = ', '.join(authors)

        if author:
            song_attrs['author'] = author

    payload = pco.template('Song', song_attrs)

    if sched_spec.song_id:
        song = pco.patch(f'/services/v2/songs/{sched_spec.song_id}', payload)
    else:
        song = pco.post('/services/v2/songs', payload)
        sched_spec.song_id = song['data']['id']
        arrangements = pco.get(f'/services/v2/songs/{sched_spec.song_id}/arrangements')
        arrangement = arrangements['data'][0]
        sched_spec.arrangement_id = arrangement['id']

    force_new_arrangement = False
    if sched_spec.arrangement_name != import_arrangement_name:
        sched_spec.arrangement_name = import_arrangement_name
        if not new_song:
            force_new_arrangement = True
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
        or line.startswith('Author:') or line.startswith('Composer:') or line.startswith('CCLI#:') or line.startswith('Improvised')
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
    if sched_spec.ccli_num:
        notes_lines.append(f'CCLI#: {sched_spec.ccli_num}')

    arr_attrs['notes'] = '\n'.join(notes_lines)    
    if new_song or force_new_arrangement or not sched_spec.arrangement_id:
        arr_attrs['length'] = 180   # 3 minute default length

    payload = pco.template('Arrangement', arr_attrs)

    if sched_spec.arrangement_id and not force_new_arrangement:
        pco.patch(f'/services/v2/songs/{sched_spec.song_id}/arrangements/{sched_spec.arrangement_id}', payload)
    else:
        arrangement = pco.post(f'/services/v2/songs/{sched_spec.song_id}/arrangements', payload)
        sched_spec.arrangement_id = arrangement['data']['id']

    db.session.commit()

    pco_assign_song_to_plan_item(item_id, service_type_id, plan_id, sched_spec)

    try:
        keys = pco.get(f'/services/v2/songs/{sched_spec.song_id}/arrangements/{sched_spec.arrangement_id}/keys')

        key_attrs = {}
        if sched_spec.start_key:
            key_attrs['starting_key'] = sched_spec.start_key
            if sched_spec.start_key[0].islower():
                key_attrs['starting_key'] = sched_spec.start_key[0].upper() + sched_spec.start_key[1:].lower() + 'm'
            if sched_spec.end_key:
                key_attrs['ending_key'] = sched_spec.end_key
                if sched_spec.end_key[0].islower():
                    key_attrs['ending_key'] = sched_spec.end_key[0].upper() + sched_spec.end_key[1:].lower() + 'm'
            pco.post(f'/services/v2/songs/{sched_spec.song_id}/arrangements/{sched_spec.arrangement_id}/keys', pco.template('Key', key_attrs))
            for key in keys['data']:
                key_id = key['id']
                pco.delete(f'/services/v2/songs/{sched_spec.song_id}/arrangements/{sched_spec.arrangement_id}/keys/{key_id}')
    except:
        logging.exception('Problem updating key')

    return { 'result': 'OK', 'song_id': sched_spec.song_id, 'arrangement_id': sched_spec.arrangement_id, 'arrangement_name': sched_spec.arrangement_name }

@app.route('/song_search')
def api_song_search():
    search_type = request.args['search_type']
    keywords = request.args['keywords']
    if search_type == 'T':
        search_attrs = {
            'where[title]': keywords
        }
    else:
        search_attrs = {
            'where[lyrics]': keywords
        }
    song_list = get_songs(search_attrs)

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
    
    return jsonify(sorted(arr_list, key=lambda arr: arr['name']))

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

@app.route('/pdf')
def generate_pdf():
    return schedule.generate_pdf()

@app.route('/schedule-report-url')
def api_schedule_report_url():
    plans = get_all_services('future')
    report_url = const.BASE_MONTHLY_REPORT_URL_HTML 
    for plan in plans:
        planid = plan['plan_id']
        report_url += f"&{planid}_plan=true"

    report_url = report_url.format(planid)

    return report_url

@app.route('/history')
def history():
    history_filename = os.path.join(config.REPORT_PATH, 'history.html')
    if not os.path.exists(history_filename):
        return "No history available. Please try again later."
        
    with open(history_filename) as f:
        return Response(f.read(), mimetype='text/html')

@app.route('/last_featured')
def last_featured():
    history_filename = os.path.join(config.REPORT_PATH, 'last_featured.html')
    if not os.path.exists(history_filename):
        return "No report available. Please try again later."
        
    with open(history_filename) as f:
        return Response(f.read(), mimetype='text/html')

@app.route('/')
def home():
    return redirect("https://app.mcbcmusic.org")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get("FLASK_SERVER_PORT", 9091), debug=True)
