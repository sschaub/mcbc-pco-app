import sys

from datetime import date, datetime, timedelta
import logging
import time
import argparse

from db import db, Person, Service, ServiceItem, ServiceItemPerson
from const import *
from utils import *
import config

FEATURE_POSITIONS = ('Instrumental Special', 'Offertory', 'Service Opener', 'Vocal Special')

def genhistory(after_date_str):
    if not after_date_str:
        after_date = datetime.today() - timedelta(days=365)
        after_date_str = after_date.strftime('%Y-%m-%d')
    logging.info(f'Generating history after {after_date_str}')

    all_people = Person.query.all()

    report_rows = []
    position_check = {} # { person_id -> name }
    num = 0
    person_to_last_feature = {} # { person_id -> date person was last featured }
    service_types_url ='https://api.planningcenteronline.com/services/v2/service_types'
    for service_type in pco.iterate(service_types_url):
        service_type_id = service_type['data']['id']

        teams_url = f"/services/v2/service_types/{service_type_id}/team_positions" 
        for pos in pco.iterate(teams_url):
            pos_name = pos['data']['attributes']['name']
            if pos_name in FEATURE_POSITIONS:
                pos_id = pos['data']['id']
                assignments_url = f"{teams_url}/{pos_id}/person_team_position_assignments?include=person"
                for asmt in pco.iterate(assignments_url):
                    person = asmt['included'][0]
                    person_id = person['id']
                    position_check[person_id] = person['attributes']['full_name']

        #/22615714/person_team_position_assignments?include=person"

        plans_url = f"{service_types_url}/{service_type_id}/plans"
        for plan in pco.iterate(plans_url, filter='after', per_page=50, after=after_date_str): # filter='after,past'
            plan = plan['data']
            plan_id = plan['id']
            plan_url = f'{plans_url}/{plan_id}'
            plan_theme = plan['attributes']['title'] or ''
            plan_time = plan['attributes']['sort_date']
            service_dt = datetime.strptime(plan_time, '%Y-%m-%dT%H:%M:%SZ') 
            if service_dt > datetime.today():
                # Skip future plans
                continue

            plan_date_str, plan_time_str = plan_time.split('T')
            plan_time_str = plan_time_str.strip('Z')
                
            logging.info(f'Processing plan at {plan_time}...')
            
            team_members = list(member['data'] 
                                for member in pco.iterate(f"{plan_url}/team_members", per_page=50) 
                                if member['data']['attributes']['status'] != 'D')

            service = Service.query.filter_by(service_type_id=service_type_id, plan_id=plan_id).first()
            if service:
                # Record already exists - remove it so we can recreate
                db.session.execute('''
                    delete from service_item_person
                    where service_item_id in (select id from service_item where service_item.service_id = :service_id)
                ''', { 'service_id': service.id }) 
                db.session.execute('''
                    delete from service_item
                    where service_id = :service_id
                ''', { 'service_id': service.id })
                db.session.execute('''
                    delete from service_team_person
                    where service_id = :service_id
                ''', { 'service_id': service.id })
                db.session.delete(service) 
                db.session.commit()

            rows = get_plan_items_with_team(plan_url, team_members)
            s = Service(service_type_id=service_type_id, plan_id=plan_id, service_date=service_dt.date(),
                        service_time=service_dt.time(), theme=plan_theme)
            db.session.add(s)

            for team_member in team_members:
                team_name = team_member['attributes']['team_position_name']
                if 'data' in team_member['relationships']['person']:
                    person_id = team_member['relationships']['person']['data']['id']
                    p = Person.query.filter_by(id=person_id).first()
                    db.session.add(ServiceTeamPerson(service=s, person=p, team_name=team_name))

                    if team_name in FEATURE_POSITIONS:
                        last_date = person_to_last_feature.get(person_id)
                        if not last_date or last_date < s.service_date:
                            person_to_last_feature[person_id] = s.service_date

            for row in rows:
                if row['item_type'] == 'song':
                    si = ServiceItem(service=s, event=row['description'], title=row['title'],
                            arrangement_id=row['arrangement_id'],
                            arrangement=row['arrangement'],
                            song_id=row['song_id'])
                    db.session.add(si)
                    person_names = []
                    for person in row['assigned_to']:
                        if person.get('id'):
                            person_id = int(person['id'])
                            p = next((p for p in all_people if p.id == int(person_id)), None)
                            if not p:
                                logging.warning(f'Cannot find person {person_id}')
                            else:
                                person_names.append(p.name)
                                sip = ServiceItemPerson(service_item=si, person=p)                        
                                db.session.add(sip)
                    si.person_names = ', '.join(person_names)
                    report_rows.append([plan_date_str, plan_time_str, row['item_seq'], plan_theme, row['description'], row['title'], row['arrangement'], si.person_names]) 
            db.session.commit()
            num += 1
            
    report_rows.sort(key=lambda entry: (entry[0], entry[1], entry[2]))

    return report_rows, position_check, person_to_last_feature

def gen_history_report(rows):
    report_html = ["""
    <html>
    <head>
        <title>MCBC Music Schedule History</title>
        <style>
            .service_header {
                background-color: lightgray
            }
        </style>    
    </head>
    <body>
        <h2>MCBC Music Schedule History</h2>
        <table>
            <tr>
                <th width="20">Service</th>
                <th>Event</th>
                <th>Title</th>
                <th>Setting</th>
                <th>Person</th>
            </tr>
    """]
    last_datetime = ""
    for row in rows:
        cur_datetime = row[0] + row[1]
        if cur_datetime != last_datetime:
            t = time.strptime(row[1], "%H:%M:%S")
            timevalue_12hour = time.strftime( "%I:%M %p", t )
            report_html.append(f"""<tr><td colspan="5" class="service_header">{row[0]} {timevalue_12hour} {row[3]}</td></tr>\n""")
            last_datetime = cur_datetime
        report_html.append(f"""<tr><td><td>{row[4]}<td>{row[5]}<td>{row[6]}<td>{row[7]}</tr>\n""")

    report_html.append("""
</body>
</html>
""")

    report_content = '\n'.join(report_html)

    report_filename = os.path.join(config.REPORT_PATH, 'history.html')
    logging.info(f"Writing report to {report_filename} ...")
    with open(report_filename, 'w') as f:
        f.write(report_content)

    return report_content

def gen_last_featured_report(position_check: dict, person_to_last_feature: dict):

    report_html = ["""
    <html>
    <head>
        <title>MCBC Music Last Featured Report</title>
        <style>
            .service_header {
                background-color: lightgray
            }
        </style>    
    </head>
    <body>
        <h2>MCBC Music Last Featured Report</h2>
        <ul>
    """]
    people = ((person_to_last_feature.get(person_id, date(1970,1,1)), person_name) for (person_id, person_name) in position_check.items())
    for last_date, person_name in sorted(people):
        date_fmt = 'not featured in last year' if last_date.year == 1970 else last_date.strftime("%m/%d/%Y")
        report_html.append(f"""<li>{person_name} - {date_fmt}""")

    report_html.append("""
</ul>
</body>
</html>
""")

    report_content = '\n'.join(report_html)

    report_filename = os.path.join(config.REPORT_PATH, 'last_featured.html')
    logging.info(f"Writing report to {report_filename} ...")
    with open(report_filename, 'w') as f:
        f.write(report_content)

def main():
    parser = argparse.ArgumentParser(description='Import PCO service history.')
    # parser.add_argument('logfile', nargs='?', help='Log file')
    # parser.add_argument('--debug', help='Debug logging', action='store_true')
    # parser.add_argument('--no-email', help='No email', action='store_true')
    parser.add_argument('--after', help='yyyy-mm-dd')

    args = parser.parse_args()

    rows, position_check, person_to_last_feature = genhistory(args.after)
    gen_history_report(rows)

    gen_last_featured_report(position_check, person_to_last_feature)

    logging.info('History generation complete')

main()