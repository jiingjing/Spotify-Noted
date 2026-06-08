"""
load Spotify extended streaming data into a MySQL database
"""

import json
import glob
from datetime import datetime
import mysql.connector

# Config

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "pass",  # replace with your MySQL password
    "database": "spotify_noted",
}

JSON_GLOB = (
    "raw_data/spotify/Spotify Extended Streaming History/Streaming_History_Audio_*.json"
)

#  Connect to MySQL database

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

#  Load JSON files

all_events = []
for path in glob.glob(JSON_GLOB):
    with open(path, encoding="utf-8") as f:
        all_events.extend(json.load(f))

print(f"Loaded {len(all_events)} total events")

#  Filter to tracks only

tracks = [
    e
    for e in all_events
    if e.get("spotify_track_uri")
    and e["spotify_track_uri"].startswith("spotify:track:")
    and e.get(
        "master_metadata_track_name"
    )  # excludes events where track name is null/missing
]

print(f"{len(tracks)} track events after filtering")

#  1. tracks_metadata

insert_metadata = """
    INSERT IGNORE INTO tracks_metadata
        (spotify_track_uri, track_name, artist_name, album_name)
    VALUES (%s, %s, %s, %s)
"""

seen_uris = set()
for e in tracks:
    uri = e["spotify_track_uri"]
    if uri not in seen_uris:
        cursor.execute(
            insert_metadata,
            (
                uri,
                e["master_metadata_track_name"],
                e["master_metadata_album_artist_name"],
                e.get("master_metadata_album_album_name"),
            ),
        )
        seen_uris.add(uri)

print(f"Inserted {len(seen_uris)} unique tracks into tracks_metadata")

#  2. listening_history

insert_history = """
    INSERT INTO listening_history
        (spotify_track_uri, time_stamp, ms_played,
         reason_start, reason_end, shuffle, skipped)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

for e in tracks:
    ts = datetime.fromisoformat(e["ts"].replace("Z", "+00:00"))

    cursor.execute(
        insert_history,
        (
            e["spotify_track_uri"],
            ts,
            e["ms_played"],
            e["reason_start"],
            e["reason_end"],
            bool(e["shuffle"]),
            bool(e["skipped"]),
        ),
    )

#  Commit & close

conn.commit()
print("Import complete.")
cursor.close()
conn.close()
