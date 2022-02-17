import json
import logging
from const import *
from db import *
import requests
import sqlalchemy.exc
from sqlalchemy import update, select, func

# def do_patch(uri: str, data: dict) -> requests.Response:
#     logging.debug("Posting to " + uri + ":" + json.dumps(data))
#     r = requests.patch(uri, auth=(PCO_APP_ID, PCO_SECRET), json=data)
#     logging.debug("Result: " + r.text)
#     r.raise_for_status()  # Check for good result
#     return r

def get_service_name(service_type_id):
    return SERVICE_TYPES.get(int(service_type_id), 'Unknown service type')


def get_plan(service_type_id: int, plan_id: int) -> dict:
    """
    returns a dict containing:
    * items - list of plan items in service
    * service - info about service { service_name, theme }
    """
    plan_url = BASE_SERVICE_URL.format(service_type_id, plan_id)
    plan = pco.get(plan_url)
    plan = plan['data']
    plan_theme = plan['attributes']['title'] or ''
    plan_time = plan['attributes']['sort_date']
    plan_date, plan_time = plan_time.split('T')
    plan_time = plan_time.strip('Z')

    service_name = '{} {}'.format(plan_date, get_service_name(service_type_id))

    team_members = list(member['data'] for member in pco.iterate(plan_url + "/team_members", per_page=50))

    rows = get_plan_items_with_team(plan_url, team_members)

    rows = [row for row in rows if row['description'] in EDITABLE_ITEMS]

    rows.sort(key=lambda entry: entry['item_seq'])

    return {
        'service': {
            'name': service_name,
            'theme': plan_theme
        },
        'items': rows
    }

def get_plan_item(service_type_id: int, plan_id: int, item_id: int) -> dict:
    """
    returns a dict containing:
    * item - list of plan items in service
    * service - info about service { service_name, theme }
    """

    data = get_plan(service_type_id, plan_id)
    item = next((item for item in data['items']
                        if int(item['id']) == item_id), None)
    if item:
        return {
            'service': data['service'],
            'item': item
        }

def get_plan_items_with_team(plan_url: str, team_members: list):
    rows = []
    items = pco.iterate(plan_url + "/items", include='arrangement,item_notes', per_page=100)

    for item in items:
        items_included = item['included']
        item = item['data']
        item_id = item['id']
        item_type = item['attributes']['item_type']
        item_title = item['attributes']['title']
        item_description = item['attributes']['description']
        item_seq = item['attributes']['sequence']
        item_arr_title = ''
        item_team = ''
        item_assigned_to = []
        arr_id = ''
        item_system = ''
        item_system_noteid = ''

    
        if 'data' in item['relationships']['arrangement'] and item['relationships']['arrangement']['data']:
            arr_id = item['relationships']['arrangement']['data']['id']
            for arr in items_included:
                if arr['type'] == 'Arrangement' and arr['id'] == arr_id:
                    item_arr_title = arr['attributes']['name']

        if 'data' in item['relationships']['item_notes']:
            notes = item['relationships']['item_notes']['data']
            for note in notes:
                note_id = note['id']
                for note in items_included:
                    if note['type'] == 'ItemNote' and note['attributes']['category_name'] == 'Service Order Team' and  note['id'] == note_id:
                        item_team = note['attributes']['content']
                    # TODO: Remove the following?
                    elif note['type'] == 'ItemNote' and note['attributes']['category_name'] == 'Person' and  note['id'] == note_id:
                        item_assigned_to.append({ 'name': note['attributes']['content'] })
                    elif note['type'] == 'ItemNote' and note['attributes']['category_name'] == 'System' and  note['id'] == note_id:
                        item_system = note['attributes']['content']
                        item_system_noteid = note['id']

        if item_team and len(item_assigned_to) == 0:
            for team_member in team_members:
                if team_member['attributes']['team_position_name'] == item_team:
                    person_name = team_member['attributes']['name']
                    person_id = ''
                    if 'data' in team_member['relationships']['person']:
                        person_id = team_member['relationships']['person']['data']['id']
                    person = Person.query.filter_by(id=person_id).first()
                    person_email = ''
                    if person:
                        person_email = person.email
                    item_assigned_to.append({
                        'id': person_id, 
                        'name': person_name, 
                        'email': person_email 
                    })

        rows.append({'id': item_id, 'item_seq': item_seq, 'description': item_description, 'title': item_title,
                        'arrangement': item_arr_title, 'arrangement_id': arr_id, 'assigned_to': item_assigned_to,
                        'item_type': item_type })
                        
    return rows

def get_sched_special(service_type_id: int, plan_id: int, item: dict) -> SchedSpecial:
    sched_spec = SchedSpecial.query.filter_by(
            service_type_id=service_type_id,
            plan_id=plan_id,
            item_id=item['id']).first()

    return sched_spec

def begin_edit_item(service_type_id: int, plan_id: int, item: dict) -> SchedSpecial:
    try:
        title = item['title'] if item['title'] != item['description'] else ''

        genre_note = ''
        solo_instruments = ''
        if 'Vocal' in item['description']:
            genre_note = 'Vocal solo'
            solo_instruments = 'Voice'
        accomp_instruments = 'Piano'
        sched_spec = SchedSpecial(
            service_type_id=service_type_id,
            plan_id=plan_id,
            item_id=item['id'],
            title=title,
            description=item['description'],
            genre_note=genre_note,
            solo_instruments=solo_instruments,
            accomp_instruments=accomp_instruments
        )
        db.session.add(sched_spec)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        # Failed to create; now try to look up
        db.session.rollback()
        sched_spec = get_sched_special(service_type_id, plan_id, item)

    return sched_spec

def save_item(current_user: Person, item_data, service_type_id, plan_id, item_id, version_no, song_id, arrangement_id, 
                arrangement_name, title, copyright_year, copyright_holder, author, translator, composer, 
                arranger, genre_note, solo_instruments, accomp_instruments, other_performers,
                staging_notes, song_text, start_key, end_key):

    def row(header, new_value, old_value, link='', extra_text=''):
        if new_value or old_value:
            content = f'''<tr><th style="text-align: right; vertical-align: top">{header}</th>'''
            color = 'black'
            if new_value != old_value:
                color = 'blue'
            if not new_value:
                color = 'red'
                new_value = '(Deleted)'
            if link:
                link = f'''<a href="https://services.planningcenteronline.com{link}" target="_blank">[pco]</a>'''
            content += f'''<td style='color: {color}'>{new_value} {link} {extra_text}</td>'''
            content += '</tr>'
        else:
            content = ''
        return content + '\n'

    # note_url = (BASE_SERVICE_URL + "/items/{}/item_notes/{}").format(service_type_id, plan_id, item['id'], item['system_id'])
    # content = json.dumps({
    #     'title': title,
    #     'song_text': song_text
    # })
    # update_payload = pco.template('ItemNote', {'content': content })
    # pco.patch(note_url, payload=update_payload)
    sched_spec = SchedSpecial.query.filter_by(
            service_type_id=service_type_id,
            plan_id=plan_id,
            item_id=item_id).first()
    if sched_spec.title != title or sched_spec.song_id != song_id or sched_spec.arrangement_id != arrangement_id:
        sched_spec.status = SchedSpecial.STATUS_PENDING

    copyright_license_status = sched_spec.copyright_license_status
    if copyright_holder and copyright_holder != sched_spec.copyright_holder:
        if LicensedPublishers.query.filter(func.lower(LicensedPublishers.publisher_name)==copyright_holder.lower()).count() > 0:
            copyright_license_status = SchedSpecial.COPYRIGHT_STATUS_APPROVED
        else:
            copyright_license_status = SchedSpecial.COPYRIGHT_STATUS_UNKNOWN

    # Generate email body
    msg = f'''<html><body>
            <p><a href="https://services.planningcenteronline.com/plans/{plan_id}" target="_blank">Link to PCO Service</a> |
            <a href="https://app.mcbcmusic.org/service/{service_type_id}-{plan_id}/{item_id}" target="_blank">Edit Special</a> | 
            <a href="https://schedule.mcbcmusic.org" target="_blank">MCBC Monthly Schedule</a>
            </p>
            <h2>{sched_spec.description}</h2>
            <table>'''
            
    service_name = item_data['service']['name']
    assigned_to_list = ','.join(item['name'] + " &lt;" + item.get('email') + "&gt;<br>" for item in item_data['item']['assigned_to'])
    link = f'/songs/{song_id}' if song_id else ''
    title_approval = '<span style="color: red">Approval Pending</span>' if sched_spec.status == SchedSpecial.STATUS_PENDING else '<span style="color: green">Approved</span>'
    msg += row('Assigned To', assigned_to_list, assigned_to_list)
    msg += row('Title', title, sched_spec.title, link, extra_text=title_approval)
    link = f'/songs/{song_id}/arrangements/{arrangement_id}' if arrangement_id else ''
    msg += row('Arrangement', arrangement_name, sched_spec.arrangement_name, link)
    msg += '</table>\n<h3>Instrumentation / Personnel</h3>\n<table>\n'    
    msg += row('Special type', genre_note, sched_spec.genre_note)
    msg += row('Solo instrument(s)', solo_instruments, sched_spec.solo_instruments)
    msg += row('Accompaniment instrument(s)', accomp_instruments, sched_spec.accomp_instruments)
    msg += row('Other performers', other_performers, sched_spec.other_performers)

    msg += '</table>\n<h3>Song Details</h3>\n<table>\n'

    orig_copyright = f'{sched_spec.copyright_year or ""} by {sched_spec.copyright_holder or "?"}'

    copyright = f'{copyright_year or ""} by {copyright_holder or "?"}'
    copyright_status_html = ''
    if copyright_license_status == SchedSpecial.COPYRIGHT_STATUS_UNKNOWN:
        copyright_status_html = ' <span style="color:red">(Unknown approval status)</span>'
    msg += row('Author', author, sched_spec.author)
    msg += row('Translator', translator, sched_spec.translator)
    msg += row('Composer', composer, sched_spec.composer)
    msg += row('Arranger', arranger, sched_spec.arranger)
    msg += row('Copyright', copyright, orig_copyright, extra_text=copyright_status_html)

    msg += '</table>\n<h3>Other Details</h3>\n'

    if song_text:
        style = 'style="color:blue"' if song_text != sched_spec.song_text else ''
        song_text_html = song_text.replace('\n', '<br>\n')
        msg += f'''<h4>Song Text</h4><div {style}>{song_text_html}</div>'''

    if staging_notes:
        style = 'style="color:blue"' if staging_notes != sched_spec.staging_notes else ''
        staging_notes_html = staging_notes.replace('\n', '<br>\n')
        msg += f'''<h4>Staging Notes</h4><div {style}>{staging_notes_html}</div>'''

    msg += '<p style="color: blue">New information is in blue</p>'
    msg += '</body></html>'

    # Version number check to detect multiuser conflict
    result = db.session.execute(
        update(SchedSpecial).
        where(SchedSpecial.id == sched_spec.id, SchedSpecial.version_no == version_no).
        values(version_no = version_no + 1, 
            status = sched_spec.status,
            song_id = song_id,
            arrangement_id = arrangement_id,
            arrangement_name = arrangement_name,
            title = title,
            copyright_holder = copyright_holder,
            copyright_year = copyright_year,
            author = author,
            translator = translator,
            composer = composer,
            arranger = arranger,
            genre_note = genre_note,
            solo_instruments = solo_instruments,
            accomp_instruments = accomp_instruments,
            other_performers = other_performers,
            staging_notes = staging_notes,
            song_text = song_text,
            start_key = start_key,
            copyright_license_status = copyright_license_status,
            end_key = end_key))

    db.session.commit()
    success = result.rowcount == 1

    if success:
        
        send_email(replyEmail=current_user.email, replyName=current_user.name,
            subject=f'{service_name} {sched_spec.description}',
            msg=msg,
            ccEmails = [current_user.email]
        )

    return success

def send_email(replyEmail: str, replyName: str, subject: str, msg: str, ccEmails: list = None):
    if not ccEmails:
        ccEmails = []

    dest_email_list = [{"email": email} for email in EMAIL_LIST]
    cc_email_list = [{"email": email} for email in ccEmails if email not in EMAIL_LIST]
    personalizations = {"to": dest_email_list, "subject": subject}
    
    if len(cc_email_list):
        personalizations["cc"] = cc_email_list

    r = None
    try:
        r = requests.post('https://api.sendgrid.com/v3/mail/send', 
            headers={
                'Authorization': f'Bearer {SENDGRID_API_KEY}'
                },
            json={
                "personalizations": [personalizations],
                "content": [{"type": "text/html", "value": msg}],
                "from":{"email":FROM_EMAIL_ADDR,"name":"MCBC Music"},
                "reply_to":{"email":replyEmail,"name":replyName}}
            )
        r.raise_for_status()
    except:
        status_code = r.status_code if r else 'unknown'
        logging.exception(f'Problem sending email with reply address {replyEmail}: status {status_code}')

