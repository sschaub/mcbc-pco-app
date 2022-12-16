import sys

from datetime import datetime, timedelta
import logging
import threading
import time
import argparse

from db import *
from const import *
from utils import *
import config

def genhistory(after_date_str):
    if not after_date_str:
        after_date = datetime.today() - timedelta(days=30)
        after_date_str = after_date.strftime('%Y-%m-%d')
    logging.info(f'Generating history after {after_date_str}')

    all_people = Person.query.all()

    report_rows = []
    num = 0
    service_types_url ='https://api.planningcenteronline.com/services/v2/service_types'
    for service_type in pco.iterate(service_types_url):
        service_type_id = service_type['data']['id']
        plans_url = f"{service_types_url}/{service_type_id}/plans"
        for plan in pco.iterate(plans_url, filter='after,past', per_page=50, after=after_date_str): # filter='after,past'
            plan = plan['data']
            plan_id = plan['id']
            plan_url = f'{plans_url}/{plan_id}'
            plan_theme = plan['attributes']['title'] or ''
            plan_time = plan['attributes']['sort_date']
            service_dt = datetime.strptime(plan_time, '%Y-%m-%dT%H:%M:%SZ') 
            plan_date_str, plan_time_str = plan_time.split('T')
            plan_time_str = plan_time_str.strip('Z')
                
            print(f'Processing plan at {plan_time}...')
            
            team_members = list(member['data'] for member in pco.iterate(f"{plan_url}/team_members", per_page=50))

            service = Service.query.filter_by(service_type_id=service_type_id, plan_id=plan_id).first()
            if service:
                # Record already exists
                db.session.execute('''
                    delete from service_item_person
                    where service_item_id in (select service_item_id from service_item where service_item.service_id = :service_id)
                ''', { 'service_id': service.id }) 
                db.session.execute('''
                    delete from service_item
                    where service_id = :service_id
                ''', { 'service_id': service.id })
                db.session.delete(service) 
                db.session.commit()

            rows = get_plan_items_with_team(plan_url, team_members)
            service_dt = datetime.strptime(plan_time, '%Y-%m-%dT%H:%M:%SZ') 
            s = Service(service_type_id=service_type_id, plan_id=plan_id, service_date=service_dt.date(),
                        service_time=service_dt.time(), theme=plan_theme)
            db.session.add(s)

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
                                print(f'Cannot find person {person_id}')
                            else:
                                person_names.append(p.name)
                                sip = ServiceItemPerson(service_item=si, person=p)                        
                                db.session.add(sip)
                    si.person_names = ', '.join(person_names)
                    if service_dt < datetime.today():
                        report_rows.append([plan_date_str, plan_time_str, row['item_seq'], plan_theme, row['description'], row['title'], row['arrangement'], si.person_names]) 
            db.session.commit()
            num += 1
            
    report_rows.sort(key=lambda entry: (entry[0], entry[1], entry[2]))

    return report_rows

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
    with open(report_filename, 'w') as f:
        f.write(report_content)

    return report_content

def main():
    parser = argparse.ArgumentParser(description='Import PCO service history.')
    # parser.add_argument('logfile', nargs='?', help='Log file')
    # parser.add_argument('--debug', help='Debug logging', action='store_true')
    # parser.add_argument('--no-email', help='No email', action='store_true')
    parser.add_argument('--after', help='yyyy-mm-dd')

    args = parser.parse_args()

    rows = genhistory(args.after)
    gen_history_report(rows)

    logging.info(f'History generation complete')

main()