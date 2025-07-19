import pprint
import re
from notion_client import Client
import os
import csv
from notion_client.helpers import iterate_paginated_api

# STEP 1: Set up Notion API
NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")  # Or replace with your integration token directly
DATABASE_ID = "8d98d0622df14c1bb4e074004a81e3a3"  # Replace with your Notion database ID

headers = ["Title", "Song # (outdated)", "Arr # (outdated)", "☀️🌙 AM/PM", "🎵Feel/Musical Character", "⭐️ Rating ⭐️", "❤️ Priority", "😰 Difficulty (Hard/Medium/Easy)", "Arr # (Updated)"]
out_headers=["title", "song_num", "arr_num", "service", "characteristics", "rating", "priority", "difficulty", "arr_updated"]


notion = Client(auth=NOTION_API_TOKEN)
def extract_data():

    rows = []
    for page in iterate_paginated_api(
        notion.databases.query, database_id=DATABASE_ID,
        filter={
            "property": "Arr # (outdated)",
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


def export_to_csv(rows, filename="notion_export.csv"):
    # Reorder: "Arr #", "Song #" first if present

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_headers)
        writer.writeheader()
        for row in rows:
            pprint.pprint(row)
            writer.writerow({h: row.get(h, "") for h in out_headers})

    print(f"✅ Exported {len(rows)} pages to {filename}")

rows = extract_data()
export_to_csv(rows)
