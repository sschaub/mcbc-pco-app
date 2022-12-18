import json
import logging
from const import *
from db import *
import requests
import sqlalchemy.exc
import re
from threading import Thread
from datetime import datetime
from sqlalchemy import update, select, func

def get_service_type_name(service_type_id: str):
    return SERVICE_TYPES.get(int(service_type_id), 'Unknown service type')

def str_to_date(s: str) -> datetime:
    """Converts a string in "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SS form to a date"""

    plan_date_str = s.split('T')[0]
    return datetime.strptime(plan_date_str, '%Y-%m-%d')

def get_service_name(service_type_id: str, plan_sortdate_str: str):
    plan_date = str_to_date(plan_sortdate_str)
    plan_date_formatted = plan_date.strftime('%b %d, %Y')
    return '{} - {}'.format(get_service_type_name(service_type_id), plan_date_formatted)

def get_all_services():
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
        { 'id': f"{service_type_id}-{plan['id']}", 'name': get_service_name(service_type_id, plan['attributes']['sort_date']), 
            'service_date': plan['attributes']['dates'], 'service_type': service_type_name, 'plan_theme': plan['attributes']['title'],
            'plan_id': plan['id'], 'updated_at': plan['attributes']['updated_at'] }
        for (service_type_id, service_type_name, plan) in sorted(plans, key=lambda plan_tuple: plan_tuple[2]['attributes']['sort_date']))

    return services

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
    plan_datetime_str = plan['attributes']['sort_date']

    service_name = get_service_name(service_type_id, plan_datetime_str)

    team_members = list(member['data'] for member in pco.iterate(plan_url + "/team_members", per_page=50))

    positions = {}
    for member in team_members:
        if member['attributes']['team_position_name'] in SERVICE_POSITIONS:
            positions[member['attributes']['team_position_name'].lower()] = member['attributes']['name']

    rows = get_plan_items_with_team(plan_url, team_members)

    rows.sort(key=lambda entry: entry['item_seq'])

    all_songs = [{ 'id': row['id'], 'title': row['title'], 'description': row['description'], 'arrangement': row['arrangement'] } for row in rows 
        if (row['arrangement'] or (row['description'] in EDITABLE_ITEMS)) and row['title'] != row['description']]
    rows = [row for row in rows if row['description'] in EDITABLE_ITEMS]

    specials = SchedSpecial.query.filter(SchedSpecial.item_id.in_([
        row['id'] for row in rows
    ])).all()
    specials = { spec.item_id: spec for spec in specials }

    for row in rows:
        special = specials.get(int(row['id']))
        if special:
            row['details_provided'] = special.details_provided
            row['status'] = special.status
            row['copyright_status'] = special.copyright_license_status
            row['genre_note'] = special.genre_note
            row['solo_instruments'] = special.solo_instruments
            row['accomp_instruments'] = special.accomp_instruments
            row['ministry_location'] = special.ministry_location
            row['staging_notes'] = special.staging_notes
        else:
            row['details_provided'] = SchedSpecial.DETAILS_NO
            row['status'] = SchedSpecial.STATUS_NOT_SUBMITTED
            row['copyright_status'] = SchedSpecial.COPYRIGHT_STATUS_UNKNOWN

    tags = [{
        'id': tag.tag_id,
        'tag_group_name': tag.song_tag.tag_group_name,
        'tag_name': tag.song_tag.tag_name
     } for tag in ServiceTag.query.filter_by(service_type_id=service_type_id, plan_id=plan_id) if tag.song_tag]

    return {
        'service': {
            'service_id': f'{service_type_id}-{plan_id}',
            'name': service_name,
            'theme': plan_theme,
            'songs': all_songs,
            'personnel': positions,
            'tags': tags
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
        item_data = item['data']
        item_id = item_data['id']
        item_type = item_data['attributes']['item_type']
        item_title = item_data['attributes']['title']
        item_description = item_data['attributes']['description']
        item_seq = item_data['attributes']['sequence']
        item_arr_title = ''
        item_team = ''
        item_assigned_to = []
        arr_id = ''
        song_id = ''

        if item_data['relationships']['song'].get('data'):
            song_id = item_data['relationships']['song']['data']['id']

        if item_data['relationships']['arrangement'].get('data'):
            arr_id = item_data['relationships']['arrangement']['data']['id']
            for arr in items_included:
                if arr['type'] == 'Arrangement' and arr['id'] == arr_id:
                    item_arr_title = arr['attributes']['name']

        for note in item_data['relationships']['item_notes'].get('data', []):
            note_id = note['id']
            for note in items_included:
                if note['type'] == 'ItemNote' and note['attributes']['category_name'] == 'Service Order Team' and  note['id'] == note_id:
                    item_team = note['attributes']['content']
                # TODO: Remove the following?
                elif note['type'] == 'ItemNote' and note['attributes']['category_name'] == 'Person' and  note['id'] == note_id:
                    item_assigned_to.append({ 'name': note['attributes']['content'] })

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
                    if person_name.endswith(' Ensemble'):
                        person_name = person_name[:-9]
                    item_assigned_to.append({
                        'id': person_id, 
                        'name': person_name, 
                        'email': person_email 
                    })

        if item_title == item_description:
            item_title = '' 

        rows.append({'id': item_id, 'item_seq': item_seq, 'description': item_description, 'title': item_title,
                        'song_id': song_id,
                        'arrangement': item_arr_title, 'arrangement_id': arr_id, 'assigned_to': item_assigned_to,
                        'item_type': item_type })
                        
    return rows

def get_sched_special(service_type_id: int, plan_id: int, item: dict) -> SchedSpecial:
    sched_spec = SchedSpecial.query.filter_by(
            service_type_id=service_type_id,
            plan_id=plan_id,
            item_id=item['id']).first()

    return sched_spec

def parse_author(author: str) -> tuple:
    composer = ''
    m = re.match(r'(.+) \(text\)[,;] (.+) \(tune\)', author)
    if m:
        author = m.group(1)
        composer = m.group(2)
    return author, composer

def is_not_copyrighted(copyright: str) -> bool:
    return copyright == 'Public Domain' or copyright == 'Improvised'
    
def parse_copyright(copyright: str) -> tuple:
    copyright_year = None
    copyright_holder = None
    m = re.match(r'[Cc]opyright (\d+) (by +)?([^.]+)', copyright)
    if m:
        copyright_year = m.group(1)
        copyright_holder = m.group(3)
    elif is_not_copyrighted(copyright):
        copyright_year = ''
        copyright_holder = copyright
    else:
        copyright = ''
    return copyright_year, copyright_holder, copyright

def get_arrangement_history(arrangement_id: int) -> list:
    history_list = list(dict(row) for row in db.session.execute("""
        select service_item.id, service_type_id, service_date, event, person_names
        from service join service_item on service.id = service_item.service_id 
        where arrangement_id = :arr_id
        order by service_date desc
        """, { 'arr_id': arrangement_id }))
    for hi in history_list:
        hi['service_name'] = get_service_name(hi['service_type_id'], hi['service_date'])
        hi['is_future'] = str_to_date(hi['service_date']) > datetime.now()

    return history_list

def get_arrangement(song_id: int, arrangement_id: int) -> dict:
    song_url = f'/services/v2/songs/{song_id}'
    song_data = pco.get(song_url)
    song_data = song_data['data']['attributes']
    author, composer = parse_author(song_data['author'] or '')
    copyright = ''
    lyrics = ''
    starting_key = ''
    ending_key = ''
    arranger = ''
    translator = ''
    ccli_num = ''
    
    arr_url = f'/services/v2/songs/{song_id}/arrangements'
    for arr in pco.iterate(arr_url, include='keys'):
        included = arr['included']
        arr_data = arr['data']        

        # Try to find some lyrics in at least one of the arrangements
        if arr_data['attributes']['lyrics'] and not lyrics:
            lyrics = arr_data['attributes']['lyrics']

        if arr_data['id'] == str(arrangement_id):
            arr_name = arr_data['attributes']['name']

            # Override any found lyrics with those of this arrangement
            if arr_data['attributes']['lyrics']:
                lyrics = arr_data['attributes']['lyrics']

            # Extract additional info from arrangement notes
            notes = arr_data['attributes']['notes']
            if notes:
                # Scan for a line indicating copyright or arranger
                notes_lines = notes.split('\n')
                for line in notes_lines:
                    copyright_data = parse_copyright(line)
                    if copyright_data[1]:
                        _, _, copyright = copyright_data
                    m = re.match(r'arr. (by )?(.+)', line)
                    if m:
                        arranger = m.group(2)
                    m = re.match(r'Arranger:[ ]*(.+)', line)
                    if m:
                        arranger = m.group(1)
                    m = re.match(r'Translator:[ ]*(.+)', line)
                    if m:
                        translator = m.group(1)
                    m = re.match(r'Author:[ ]*(.+)', line)
                    if m:
                        author = m.group(1)
                    m = re.match(r'Composer:[ ]*(.+)', line)
                    if m:
                        composer = m.group(1)
                    m = re.match(r'CCLI#:[ ]*(.+)', line)
                    if m:
                        ccli_num = m.group(1)

            for incl in included:
                if incl['type'] == 'Key':
                    starting_key = incl['attributes']['starting_key']
                    if incl['attributes']['starting_minor']:
                        starting_key = starting_key.lower()
                    ending_key = incl['attributes']['ending_key']
                    if not ending_key:
                        ending_key = starting_key
                    else:
                        if incl['attributes']['ending_minor']:
                            ending_key = ending_key.lower()

    history = get_arrangement_history(arrangement_id)

    return {
        'id': arrangement_id,
        'name': arr_name,
        'lyrics': lyrics,
        'start_key': starting_key,
        'end_key': ending_key,
        'author': author,
        'composer': composer,
        'translator': translator,
        'arranger': arranger,
        'copyright': copyright,
        'ccli_num': ccli_num,
        'history': history  # see get_arrangement_history
    }

def get_song_history(song_id: int) -> list:
    history_list = list(dict(row) for row in db.session.execute("""
        select service_item.id, service_type_id, service_date, event, person_names, arrangement
        from service join service_item on service.id = service_item.service_id 
        where song_id = :song_id
        order by service_date desc
        """, { 'song_id': song_id }))

    for hi in history_list:
        hi['service_name'] = get_service_name(hi['service_type_id'], hi['service_date'])
        hi['is_future'] = str_to_date(hi['service_date']) > datetime.now()
        
    return history_list


def get_song(song_id: int) -> dict:
    song_url = f'/services/v2/songs/{song_id}'
    song_data = pco.get(song_url)
    song_data = song_data['data']['attributes']
    song_title = song_data['title']
    author, composer = parse_author(song_data['author'] or '')

    any_lyrics = ''
    hymnal_lyrics = ''

    # Try to find some lyrics in at least one of the arrangements
    arr_url = f'/services/v2/songs/{song_id}/arrangements'
    for arr in pco.iterate(arr_url):
        arr_data = arr['data']        

        if arr_data['attributes']['lyrics'] and (('HGG' in arr_data['attributes']['name']) or ('PG' in arr_data['attributes']['name'])):
            hymnal_lyrics = arr_data['attributes']['lyrics']
        if arr_data['attributes']['lyrics'] and not any_lyrics:
            any_lyrics = arr_data['attributes']['lyrics']

    history = get_song_history(song_id)

    return {
        'id': song_id,
        'title': song_title,
        'lyrics': hymnal_lyrics or any_lyrics,
        'author': author,
        'composer': composer,
        'copyright': (song_data['copyright'] or '').strip(),
        'history': history  # See get_song_history
    }

def get_songs(params):
    params["where[hidden]"] = "false"
    songs = pco.get('/services/v2/songs', **params)
    song_list = [{
        'id': song['id'],
        'title': song['attributes']['title'],
        'author': song['attributes']['author'],
        'copyright': (song['attributes']['copyright'] or '').strip()
    } for song in songs['data']]

    song_list.sort(key=lambda song: song['title'])

    return song_list

def begin_edit_item(service_type_id: int, plan_id: int, item: dict) -> SchedSpecial:
    try:
        title = item['title'] if item['title'] != item['description'] else ''

        genre_note = ''
        solo_instruments = ''
        ministry_location = 'Piano well'
        if 'Vocal' in item['description']:
            genre_note = 'Vocal solo'
            ministry_location = 'Pulpit'
        accomp_instruments = 'Piano'
        if 'Organ' in item['description']:
            genre_note = 'Organ solo'
            accomp_instruments = ''
            ministry_location = 'Other'

        status = SchedSpecial.STATUS_APPROVED if item['song_id'] else SchedSpecial.STATUS_NOT_SUBMITTED

        sched_spec = SchedSpecial(
            service_type_id=service_type_id,
            plan_id=plan_id,
            item_id=item['id'],
            title=title,
            song_id=item['song_id'],
            arrangement_id=item['arrangement_id'],
            arrangement_name=item['arrangement'],
            description=item['description'],
            genre_note=genre_note,
            ministry_location=ministry_location,
            solo_instruments=solo_instruments,
            accomp_instruments=accomp_instruments,
            status=status
        )
        db.session.add(sched_spec)
        db.session.commit()

        if item['arrangement_id']:
            arr = get_arrangement(item['song_id'], item['arrangement_id'])
            sched_spec.song_text = arr['lyrics']
            sched_spec.copyright = arr['copyright']
            sched_spec.author = arr['author']
            sched_spec.composer = arr['composer']
            sched_spec.translator = arr['translator']
            sched_spec.arranger = arr['arranger']
            sched_spec.start_key = arr['start_key']
            sched_spec.end_key = arr['end_key']
            db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        # Failed to create; now try to look up
        db.session.rollback()
        sched_spec = get_sched_special(service_type_id, plan_id, item)

    return sched_spec

def pco_assign_song_to_plan_item(item_id, service_type_id, plan_id, sched_spec):
    url = f'/services/v2/service_types/{service_type_id}/plans/{plan_id}/items/{item_id}'

    templ = pco.template('Item', { 'title': sched_spec.title })

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

    found_notes = False
    found_location = False
    item_notes = pco.get(f'{url}/item_notes')
    for item_note in item_notes['data']:
        if item_note['attributes']['category_name'] == 'Service Order Note' and sched_spec.solo_instruments:
            item_note_id = item_note['id']
            pco.patch(f'{url}/item_notes/{item_note_id}', pco.template('ItemNote', { 'content': sched_spec.solo_instruments }))
            found_notes = True
        if item_note['attributes']['category_name'] == 'Location' and sched_spec.ministry_location:
            item_note_id = item_note['id']
            loc_url = f'{url}/item_notes/{item_note_id}'
            pco.patch(loc_url, pco.template('ItemNote', { 'content': sched_spec.ministry_location }))
            found_location = True

    if sched_spec.solo_instruments and not found_notes:
        service_order_category_id = SERVICE_ORDER_NOTE_CATEGORIES[int(service_type_id)]
        pco.post(f'{url}/item_notes', pco.template("ItemNote", {
                    "content": sched_spec.solo_instruments,
                    "item_note_category_id": service_order_category_id
                }))

    if sched_spec.ministry_location and not found_location:
        service_order_category_id = LOCATION_NOTE_CATEGORIES[int(service_type_id)]
        pco.post(f'{url}/item_notes', pco.template("ItemNote", {
                    "content": sched_spec.ministry_location,
                    "item_note_category_id": service_order_category_id
                }))


def save_item(current_user: Person, item_data, service_type_id, plan_id, item_id, details_provided, version_no, song_id, arrangement_id, 
                arrangement_name, title, copyright, copyright_year, copyright_holder, ccli_num, author, translator, composer, 
                arranger, genre_note, solo_instruments, accomp_instruments, other_performers, ministry_location,
                staging_notes, song_text, start_key, end_key, email_type=0):

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

    def to12hour(timestr: str) -> str:
        try:
            timestr = datetime.strptime(timestr[:5], "%H:%M").strftime("%I:%M %p")
        except:
            pass
        return timestr

    if copyright:
        copyright_year, copyright_holder, _ = parse_copyright(copyright)
    elif is_not_copyrighted(copyright_holder):
        copyright = copyright_holder
    elif copyright_holder and copyright_year:
        copyright = f'Copyright {copyright_year} {copyright_holder}.'

    sched_spec = SchedSpecial.query.filter_by(
            service_type_id=service_type_id,
            plan_id=plan_id,
            item_id=item_id).first()
    if sched_spec.title != title or sched_spec.song_id != song_id or sched_spec.arrangement_id != arrangement_id:
        sched_spec.status = SchedSpecial.STATUS_PENDING

    copyright_license_status = sched_spec.copyright_license_status
    if copyright_holder and copyright_holder != sched_spec.copyright_holder:
        if (is_not_copyrighted(copyright_holder) or 
            LicensedPublishers.query.filter(func.lower(LicensedPublishers.publisher_name)==copyright_holder.lower()).count() > 0):
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

    if details_provided:

        msg += '</table>\n<h3>Instrumentation / Personnel</h3>\n<table>\n'    
        msg += row('Special type', genre_note, sched_spec.genre_note)
        msg += row('Instrument(s)', solo_instruments, sched_spec.solo_instruments)
        msg += row('Accompaniment', accomp_instruments, sched_spec.accomp_instruments)
        msg += row('Other musicians', other_performers, sched_spec.other_performers)

        msg += '</table>\n<h3>Song Details</h3>\n<table><tr><td><table>\n'

        if is_not_copyrighted(sched_spec.copyright_holder):
            orig_copyright = sched_spec.copyright_holder
        else:
            orig_copyright = f'{sched_spec.copyright_year or ""} by {sched_spec.copyright_holder or "?"}'

        copyright_status_html = ''
        if copyright_license_status == SchedSpecial.COPYRIGHT_STATUS_UNKNOWN:
            copyright_status_html = ' <span style="color:red">(Unknown approval status)</span>'
        msg += row('Author', author, sched_spec.author)
        msg += row('Translator', translator, sched_spec.translator)
        msg += row('Composer', composer, sched_spec.composer)
        msg += row('Arranger', arranger, sched_spec.arranger)
        msg += row('Copyright', copyright, orig_copyright, extra_text=copyright_status_html)

    msg += '</table></td><td>\n'

    msg += f'<p>Words by {author}<br>'
    if translator:
        msg += f'Translated by {translator}<br>'
    if composer:
        msg += f'Music by {composer}<br>'
    if arranger:
        msg += f'Arranged by {arranger}<br>'
    if copyright:
        msg += f'{copyright}'
    msg += '</p></td></tr></table>'

        
    if details_provided:

        msg += '<h3>Other Details</h3>\n'

        if song_text:
            style = 'style="color:blue"' if song_text != sched_spec.song_text else ''
            song_text_html = song_text.replace('\n', '<br>\n')
            msg += f'''<h4>Song Text</h4><div {style}>{song_text_html}</div>'''

        if ministry_location:
            style = 'style="color:blue"' if ministry_location != sched_spec.ministry_location else ''
            msg += f'''<h4>Ministry Location</h4><div {style}>{ministry_location}</div>'''

        if staging_notes:
            style = 'style="color:blue"' if staging_notes != sched_spec.staging_notes else ''
            staging_notes_html = staging_notes.replace('\n', '<br>\n')
            msg += f'''<h4>Staging Notes</h4><div {style}>{staging_notes_html}</div>'''

    if song_id:
        history = get_song_history(song_id)
        if len(history):
            msg += '\n<h3>Song Usage</h3>'
            for hi in history:
                msg += f'''<p>{hi['service_name']}: {hi['event']} - {hi['arrangement']} [{hi['person_names']}]</p>'''

    if arrangement_id:
        history = get_arrangement_history(arrangement_id)
        if len(history):
            msg += '\n<h3>Arrangement Usage</h3>'
            for hi in history:
                msg += f'''<p>{hi['service_name']}: {hi['event']} [{hi['person_names']}]</p>'''

    msg += '<p style="color: blue">New information is in blue</p>'
    msg += '</body></html>'

    # Version number check to detect multiuser conflict
    result = db.session.execute(
        update(SchedSpecial).
        where(SchedSpecial.id == sched_spec.id, SchedSpecial.version_no == version_no).
        values(version_no = version_no + 1, 
            status = sched_spec.status,
            details_provided = details_provided,
            song_id = song_id,
            arrangement_id = arrangement_id,
            arrangement_name = arrangement_name,
            title = title,
            copyright_holder = copyright_holder,
            copyright_year = copyright_year,
            copyright = copyright,
            ccli_num = ccli_num,
            author = author,
            translator = translator,
            composer = composer,
            arranger = arranger,
            genre_note = genre_note,
            solo_instruments = solo_instruments,
            accomp_instruments = accomp_instruments,
            other_performers = other_performers,
            staging_notes = staging_notes,
            ministry_location = ministry_location,
            song_text = song_text,
            start_key = start_key,
            copyright_license_status = copyright_license_status,
            end_key = end_key))

    db.session.commit()
    success = result.rowcount == 1

    if success and email_type:
        if details_provided:
            to_list = ALL_EMAIL_LIST
        else:
            to_list = INITIAL_EMAIL_LIST
        
        send_email(replyEmail=current_user.email, replyName=current_user.name,
            subject=f'{service_name} {sched_spec.description}',
            msg=msg,
            toEmails = to_list,
            ccEmails = [current_user.email]
        )

    return success

def send_email(subject: str, msg: str, replyEmail: str = '', replyName: str = '',  toEmails: list = None, ccEmails: list = None):
    if not ccEmails:
        ccEmails = []
    if not toEmails:
        toEmails = INITIAL_EMAIL_LIST
    
    cc_email_list = [{"email": email} for email in ccEmails if email not in toEmails]
    to_email_list = [{"email": email} for email in toEmails]
    personalizations = {"to": to_email_list, "subject": subject}
    
    if len(cc_email_list):
        personalizations["cc"] = cc_email_list

    json={
                "personalizations": [personalizations],
                "content": [{"type": "text/html", "value": msg}],
                "from":{"email":FROM_EMAIL_ADDR,"name":"MCBC Music"},
    }
    if replyEmail:
        reply_to = {"email":replyEmail}
        if replyName:
            reply_to["name"] = replyName
        json['reply_to'] = reply_to

    r = None
    try:
        r = requests.post('https://api.sendgrid.com/v3/mail/send', 
            headers={
                'Authorization': f'Bearer {SENDGRID_API_KEY}'
                },
            json=json)
        r.raise_for_status()
    except:
        status_code = r.status_code if r else 'unknown'
        logging.exception(f'Problem sending email with reply address {replyEmail}: status {status_code}')
        logging.info(json)

