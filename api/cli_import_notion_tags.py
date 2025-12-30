from pprint import pprint
from const import pco
import csv
import re
import os.path
import config
from pypco.exceptions import PCORequestException
import logging

PCO_BASE_SERVICES_URL = '/services/v2'

TAG_GROUPS = ['characteristics', 'service', 'priority', 'rating', 'difficulty']

PCO_GROUP_NAMES = { 'characteristics': 'Characteristics (Musical)' }

tag_id_to_group = {}
tag_id_to_name = {}
# { group_name -> { tag_name -> tag_id }}
all_tags = {}

def normalize_title(title) -> str:
     title = re.sub(r'[^a-zA-Z ]', '', title)
     return ' '.join(title.lower().split())

def get_pco_arr_by_id(song_num, arr_num) -> tuple[dict, dict]:
    pco_song = pco.get(f'{PCO_BASE_SERVICES_URL}/songs/{song_num}')
    tags = pco.get(f'{PCO_BASE_SERVICES_URL}/songs/{song_num}/arrangements/{arr_num}/tags')
    return pco_song, tags

for tag_group in pco.iterate(f'{PCO_BASE_SERVICES_URL}/tag_groups', include='tags', per_page=100):
    group_name = tag_group['data']['attributes']['name'].lower()
    all_tags[group_name] = all_tags.get(group_name, {})
    for tag in tag_group['included']:
        tag_name = tag['attributes']['name'].lower()
        tag_id = tag['id']
        all_tags[group_name][tag_name] = tag_id
        tag_id_to_group[tag_id] = group_name
        tag_id_to_name[tag_id] = tag_name

filename = os.path.join(config.REPORT_PATH, 'notion_export.csv')
with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for tag_group in TAG_GROUPS:
            if tag_group not in reader.fieldnames:
                logging.error(f"ERROR: tag group '{tag_group}' is not one of the CSV fields.")
                exit(1)
        for row in reader:
            # pprint(row)
            title = row["title"]
            song_number = row["song_num"].strip()
            arr_number = row["arr_num"].strip()
            # tags = [tag.strip() for tag in row["Tags"].split(",") if tag.strip()]
            logging.info(f"Processing Song #{song_number}, Arr #{arr_number} - {title}")

            try:
                pco_song, pco_tags = get_pco_arr_by_id(song_number, arr_number)
                pco_song_title = pco_song['data']['attributes']['title']

                # We decided to remove this check because PCO song titles don't always match Notion song titles
                # if normalize_title(pco_song_title) != normalize_title(title):
                #      print(f'SKIPPING Song {song_number} Arr {arr_number}: title "{title}" does not match PCO title "{pco_song_title}"')
                #      continue
                
                orig_arr_tag_ids = []
                arr_tag_ids = [] # a list of tags for this arrangement
            
                # First, we iterate over the existing arrangement tags and retain any tags that are in
                # tag groups that we are not syncing
                for tag in pco_tags['data']:
                    tag_name = tag['attributes']['name']
                    tag_id = tag['id']
                    orig_arr_tag_ids.append(tag_id)
                    if not tag_id_to_group[tag_id] in TAG_GROUPS:
                        # This is not one of the tag groups we update; keep the tag
                        arr_tag_ids.append(tag_id)
            
                for tag_group in TAG_GROUPS:
                    tag_names = row[tag_group].split(', ')
                    pco_group_name = PCO_GROUP_NAMES.get(tag_group, tag_group.lower())
                    tag_names = [tn.strip() for tn in tag_names if tn.strip()]
                    for tag_name in tag_names:
                        tag_id = all_tags.get(pco_group_name.lower(), {}).get(tag_name.lower())
                        if tag_id:
                            arr_tag_ids.append(tag_id)
                        else:
                            logging.warning(f'Song {song_number} Arr {arr_number}: tag "{tag_name}" not defined in group "{tag_group}"')

                if list(sorted(orig_arr_tag_ids)) != list(sorted(arr_tag_ids)):
                    # print(f"Song {song_number} Arr {arr_number}: tags = {arr_tag_ids}")
                    tag_data = [{
                        'type': 'Tag', 'id': tag_id 
                    } for tag_id in arr_tag_ids]
                    # Tried to use pco.post() for this, but this endpoint returns no body and the
                    # pco post() method tries to decode a json() response and fails
                    pco.request_response("post", f"{PCO_BASE_SERVICES_URL}/songs/{song_number}/arrangements/{arr_number}/assign_tags", payload={
                        'data': {
                            'type': 'TagAssignment',
                            'attributes': {},
                            'relationships': {
                                'tags': {
                                    'data': tag_data
                                }
                            }
                        }
                    })
            except PCORequestException as ex:
                if ex.status_code == 404:
                    logging.warning(f"SKIPPING Song {song_number} Arr {arr_number}: No PCO arrangement found for song '{title}'")
                    continue
                else:
                    raise
                
            