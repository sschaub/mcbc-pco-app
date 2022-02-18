import sys

from db import *
from const import *
import sqlalchemy

logging.info(f'Importing people...')

criteria = {
    'where[status]': 'active'
}

for person in pco.iterate('https://api.planningcenteronline.com/people/v2/people', include='emails,phone_numbers', per_page=100, **criteria):
    a = person['data']['attributes']
    incl = person['included']
    name = a['first_name'] + ' ' + a['last_name']
    email = ''
    phone_number = ''
    for incl in person['included']:
        if incl['type'] == 'Email':
            email = incl['attributes']['address']
        elif incl['type'] == 'PhoneNumber':
            phone_number = incl['attributes']['number']

    p = Person.query.filter_by(id=person['data']['id']).first()
    if p:
        p.name = name
        p.email = email
        p.phone_number = phone_number
    else:
        p = Person(id=person['data']['id'], name=name, email=email, phone=phone_number)
        db.session.add(p)

db.session.commit()

logging.info(f'People import complete.')
