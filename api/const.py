import pypco
import logging
import os
from config import PCO_APP_ID, PCO_SECRET, PCO_WEBAPP_LOGIN_USERNAME, PCO_WEBAPP_LOGIN_PASSWORD, LOG_LEVEL

pco = pypco.PCO(PCO_APP_ID, PCO_SECRET)

REPORT_ID_SERVICE_ORDER = '117209'
REPORT_ID_SCHEDULE = '116671'

DEV_FORCE_REGENERATE_SCHEDULE = int(os.environ.get('DEV_FORCE_REGENERATE_SCHEDULE', 0))
DEV_SCHEDULE = int(os.environ.get('DEV_SCHEDULE', 0))

if DEV_SCHEDULE:
    REPORT_ID_SCHEDULE = '118339'  # Dev schedule

# URL's
BASE_SERVICE_TYPE_URL = '/services/v2/service_types/{}/plans?filter=future'
BASE_SERVICE_URL = '/services/v2/service_types/{}/plans/{}'
BASE_MONTHLY_REPORT_URL_HTML = f'https://services.planningcenteronline.com/reports/{REPORT_ID_SCHEDULE}.html?utf8=%E2%9C%93&print_to=&print_page_size=US-Letter&print_orientation=Portrait&print_margin=0.25in&plan_id={{}}'
BASE_MONTHLY_REPORT_URL_PDF = f'https://services.planningcenteronline.com/reports/{REPORT_ID_SCHEDULE}.pdf?utf8=%E2%9C%93&print_to=pdf&print_page_size=US-Letter&print_orientation=Portrait&print_margin=0.25in&plan_id={{}}'
PLAN_DETAIL_URL = '/services/v2/service_types/{}/plans/{}'
ITEM_DETAIL_URL = '/services/v2/service_types/{}/plans/{}/items/{}'
# The ID numbers in the following come from the PCO API https://api.planningcenteronline.com/services/v2/service_types
SERVICE_TYPES = { 1060129: 'Sunday AM', 1060132: 'Sunday PM', 1060133: 'Wednesday', 1243611: 'Special Service' }
# The note categories come from PCO API https://api.planningcenteronline.com/services/v2/service_types/(service_type_id)/item_note_categories
SERVICE_ORDER_NOTE_CATEGORIES = { 
    # service_order_id: item_note_category_id
    1060129: 3987812, # Sunday AM
    1060132: 3993389, # Sunday PM
    1060133: 3993728, # Wednesday
    1243611: 4717356  # Special service
    }
LOCATION_NOTE_CATEGORIES = { 
    1060129: 3992309,  # Sunday AM
    1060132: 3993388,  # Sunday PM
    1060133: 3993729,  # Wednesday
    1243611: 4717357   # Special service
    }
EDITABLE_ITEMS = ['Prelude Opener', 'Vocal Special', 'Service Opener', 'Instrumental Special', 'Organ Special', 'Offertory', 'Choir Special']
SERVICE_POSITIONS = ['Songleader', 'Organ', 'Piano', 'Piano 2']


# Configure log message format
logging.basicConfig(format='%(asctime)s %(message)s', level=getattr(logging, LOG_LEVEL.upper()))
