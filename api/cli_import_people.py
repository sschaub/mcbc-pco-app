import sys

from db import *
from const import *

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
        if incl['type'] == 'Email' and incl['attributes']['primary']:
            email = incl['attributes']['address']
        elif incl['type'] == 'PhoneNumber':
            phone_number = incl['attributes']['number']
            if phone_number:
                phone_number = ''.join(digit for digit in phone_number if digit.isdigit())

    p = Person.query.filter_by(id=person['data']['id']).first()
    if p:
        if p.name != name or p.email != email or p.phone != phone_number:
            logging.info(f'Updating {p.name} to email {email} phone {phone_number}')
        p.name = name
        p.email = email
        p.phone = phone_number
    else:
        p = Person(id=person['data']['id'], name=name, email=email, phone=phone_number)
        logging.info(f'Adding new person {p.name} with email {email} phone {phone_number}')
        db.session.add(p)

db.session.commit()

logging.info(f'People import complete.')
