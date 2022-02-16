import json
import logging
from const import *
from db import *
import sqlalchemy.exc
from sqlalchemy import update, select

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

def save_item(service_type_id, plan_id, item_id, version_no, song_id, arrangement_id, 
                arrangement_name, title, copyright_year, copyright_holder, author, composer, 
                arranger, genre_note, solo_instruments, accomp_instruments, other_performers,
                staging_notes, song_text, start_key, end_key):
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
            composer = composer,
            arranger = arranger,
            genre_note = genre_note,
            solo_instruments = solo_instruments,
            accomp_instruments = accomp_instruments,
            other_performers = other_performers,
            staging_notes = staging_notes,
            song_text = song_text,
            start_key = start_key,
            end_key = end_key))

    db.session.commit()
    return result.rowcount == 1

    # Send email:  curl --request POST \
    # >   --url https://api.sendgrid.com/v3/mail/send \
    # >   --header "Authorization: Bearer $SENDGRID_API_KEY" \
    # >   --header 'Content-Type: application/json' \
    # >   --data '{"personalizations": [{"to": [{"email": "sschaub88@outlook.com"}]}],"from": {"email": "admin@mcbcmusic.org"},"subject": "Sending with SendGrid is Fun","content": [{"type": "text/plain", "value": "and easy to do anywhere, even with cURL"}]}'

