import pprint
import re
from notion_client import Client
import os
import csv
from notion_client.helpers import iterate_paginated_api
import config
import os.path

# For some reason, logging output does not appear... maybe the notion_client is configuring logging
# in a way that prevents our output. So we use print here.
#import logging

if not config.NOTION_API_TOKEN:
    print("No NOTION_API_TOKEN defined")
    exit(1)

headers = ["Title", "Song #", "Arr #", "☀️🌙 AM/PM", "🎵Feel/Musical Character", "⭐️ Rating ⭐️", "❤️ Priority", "😰 Difficulty (Hard/Medium/Easy)"]
out_headers=["title", "song_num", "arr_num", "service", "characteristics", "rating", "priority", "difficulty"]



notion = Client(auth=config.NOTION_API_TOKEN)
def extract_data():

    print("Reading records from Notion")

    rows = []
    for page in iterate_paginated_api(
        notion.data_sources.query, data_source_id=config.NOTION_CHORAL_DATASOURCE_ID,
        filter={
            "property": "Arr #",
            "number": {
                "is_not_empty": True,
            },
        },
    ):
        properties = page["properties"]
        row = {}

        # pprint.pprint(properties)

        for key, prop in properties.items():
            # Normalize the key to match what we're looking for
            normalized_key = key.strip()

            try:
                loc = headers.index(normalized_key)
                normalized_key = out_headers[loc]
            except:
                # print(f"{normalized_key} not recognized")
                continue

            try:
                if prop["type"] == "title":
                    value = prop["title"][0]["plain_text"] if prop["title"] else ""
                elif prop["type"] == "rich_text":
                    value = prop["rich_text"][0]["plain_text"] if prop["rich_text"] else ""
                elif prop["type"] == "multi_select":
                    value = ", ".join([tag["name"] for tag in prop["multi_select"]])
                elif prop["type"] == "select":
                    value = prop["select"]["name"] if prop["select"] else ""
                elif prop["type"] == "date":
                    value = prop["date"]["start"] if prop["date"] else ""
                elif prop["type"] == "checkbox":
                    value = prop["checkbox"]
                elif prop["type"] == "number":
                    value = prop["number"]
                elif prop["type"] == "rollup":
                    value = prop["rollup"]["array"]
                else:
                    value = ""
            except Exception as e:
                value = f"[Error: {str(e)}]"

            row[normalized_key] = (str(value) or "").strip()

        rows.append(row)
    return rows


def export_to_csv(rows, filename):
    # Reorder: "Arr #", "Song #" first if present

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_headers)
        writer.writeheader()
        for row in rows:
            # pprint.pprint(row)
            writer.writerow({h: row.get(h, "") for h in out_headers})

    print(f"✅ Exported {len(rows)} records to {filename}")


filename = os.path.join(config.REPORT_PATH, 'notion_export.csv')

# Check if the file exists before deleting
if os.path.isfile(filename):
    os.remove(filename)
    print(f"{filename} has been removed.")

rows = extract_data()
export_to_csv(rows, filename)
