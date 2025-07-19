# This was used to copy one notion field to another and can probably be deleted

import pprint
import re
from notion_client import Client
import os
import csv
from notion_client.helpers import iterate_paginated_api

# STEP 1: Set up Notion API
NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")  # Or replace with your integration token directly
DATABASE_ID = "8d98d0622df14c1bb4e074004a81e3a3"  # Replace with your Notion database ID


notion = Client(auth=NOTION_API_TOKEN)
def copy_data():

    # db = notion.databases.retrieve(DATABASE_ID)
    # song_no_id = db["properties"]["Song # (updated)"]["id"]



    for page in iterate_paginated_api(
        notion.databases.query, database_id=DATABASE_ID,
    ):
        properties = page["properties"]
        page_id = page["id"]

        title = properties["Title"]["title"] and properties["Title"]["title"][0]["plain_text"]

        print(page_id, title)

        song_no_prop = properties.get("Song # (updated)")
        arr_no_prop = properties.get("Arr # (updated)")

        if song_no_prop and arr_no_prop:
            song_nos = song_no_prop["rollup"]["array"]
            arr_nos = arr_no_prop["rollup"]["array"]
            song_no = None
            arr_no = None
            
            if len(song_nos) == 1 and len(arr_nos) == 1:
                song_no = song_nos[0]['number']
                arr_no = arr_nos[0]['number']

            notion.pages.update(
                page_id=page_id,
                properties={
                    "Song # (outdated)": {"number": song_no},
                    "Arr # (outdated)": {"number": arr_no}
                }
            )


copy_data()
