import sys

from db import *
from const import *
import sqlalchemy

logging.info(f'Importing songs...')

db.session.execute('''
    delete from song_tag
''')

for tag_group in pco.iterate('/services/v2/tag_groups', include='tags'):
    group_name = tag_group['data']['attributes']['name']
    group_id = tag_group['data']['id']
    if tag_group['data']['attributes']['tags_for'] == 'song':
        # print(f'Importing tags for {group_name}')
        for tag in tag_group['included']:
            tag_id = tag['id']
            tag_name = tag['attributes']['name']
            songTag = SongTag(id=tag_id, tag_group_id=group_id, tag_group_name=group_name, tag_name=tag_name)
            db.session.add(songTag)
            print(f'* Tag: {tag_id} {tag_name}')

# criteria = {
#     'where[hidden]': 'false'
# }

# for song in pco.iterate('/services/v2/songs', per_page=100, **criteria):
#     song_id = song['data']['id']
#     for tag in pco.iterate('/services/v2/songs/{song_id}/tags'):

db.session.commit()

logging.info(f'Song import complete.')
