"""
load_spotify.py
---------------
Loads Spotify extended streaming history and library data into MySQL.

Schema notes:
- track_id: SHA1 of casefold(track)|casefold(artist)|casefold(album)
             groups tracks that differ only in capitalisation or URI relinking
- track_uris: maps spotify URIs to track_id (many URIs → one track_id)
- in_library: matched by track_id, not URI, to handle relinking edge cases
"""

import hashlib
import json
import glob
import os
from collections import defaultdict
from datetime import datetime

import mysql.connector
from dotenv import dotenv_values

# Config

config = dotenv_values(".env")

DB_CONFIG = {
    "host": config["DB_HOST"],
    "user": config["DB_USER"],
    "password": config["DB_PASS"],
    "database": config["DB_NAME"],
}

HISTORY_JSON_GLOB = config["HISTORY_JSON_GLOB"]
LIBRARY_JSON = config["LIBRARY_JSON"]
IDENTITY_JSON = config["IDENTITY_JSON"]
LOG_DIR = config["LOG_DIR"]
REPORT_PATH = os.path.join(LOG_DIR, "import_report.txt")

# Helpers


def generate_track_id(track, artist, album):
    raw = "|".join(
        [
            track.casefold().strip(),
            artist.casefold().strip(),
            album.casefold().strip(),
        ]
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


# Load data

all_events = []
for path in glob.glob(HISTORY_JSON_GLOB):
    with open(path, encoding="utf-8") as f:
        all_events.extend(json.load(f))

print(f"Loaded {len(all_events)} total audio events")

with open(LIBRARY_JSON, encoding="utf-8") as f:
    library_data = json.load(f)

with open(IDENTITY_JSON, encoding="utf-8") as f:
    identity_data = json.load(f)

# Filter history to tracks only
# drops podcasts, audiobooks, local files (no spotify_track_uri or track name)

tracks = [
    e
    for e in all_events
    if e.get("spotify_track_uri")
    and e["spotify_track_uri"].startswith("spotify:track:")
    and e.get("master_metadata_track_name")
]

print(f"{len(tracks)} music track events after filtering")

# Generate track_id for every history event

for e in tracks:
    e["track_id"] = generate_track_id(
        e["master_metadata_track_name"],
        e["master_metadata_album_artist_name"],
        e["master_metadata_album_album_name"] or "",
    )

# Generate track_id for every library track

for t in library_data["tracks"]:
    t["track_id"] = generate_track_id(
        t["track"],
        t["artist"],
        t["album"] or "",
    )

library_track_ids = {t["track_id"] for t in library_data["tracks"]}
print(f"Loaded {len(library_track_ids)} tracks from library")

# Reports

os.makedirs(LOG_DIR, exist_ok=True)

with open(REPORT_PATH, "w", encoding="utf-8") as report:

    # Report: tracks with multiple Spotify URIs (capitalisation duplicates)

    groups = defaultdict(set)
    for e in tracks:
        key = (
            e["master_metadata_track_name"].casefold().strip(),
            e["master_metadata_album_artist_name"].casefold().strip(),
            (e["master_metadata_album_album_name"] or "").casefold().strip(),
        )
        groups[key].add(e["spotify_track_uri"])

    multi_uri = {k: v for k, v in groups.items() if len(v) > 1}
    if multi_uri:
        report.write(f"Tracks with multiple Spotify URIs ({len(multi_uri)} cases):\n")
        for (track, artist, album), uris in multi_uri.items():
            report.write(f"  {track} — {artist} — {album}\n")
            for uri in sorted(uris):
                report.write(f"    {uri}\n")
    else:
        report.write("No capitalisation duplicate URIs found\n")

    report.write("\n")

    # Report: library tracks not matched in history

    history_track_ids = {e["track_id"] for e in tracks}
    unmatched = library_track_ids - history_track_ids

    if unmatched:
        report.write(f"Library tracks not found in history ({len(unmatched)} cases):\n")
        for t in library_data["tracks"]:
            if t["track_id"] in unmatched:
                report.write(f"  {t['track']} — {t['artist']}\n")
    else:
        report.write("All library tracks matched in history\n")

print(f"Report written to {REPORT_PATH}")

# Connect to MySQL

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# 1. tracks_metadata
# one row per unique track_id
# in_library matched by track_id to handle URI relinking edge cases

insert_metadata = """
    INSERT IGNORE INTO tracks_metadata
        (track_id, track_name, artist_name, album_name, in_library)
    VALUES (%s, %s, %s, %s, %s)
"""

seen_track_ids = set()
for e in tracks:
    track_id = e["track_id"]
    in_library = track_id in library_track_ids
    if track_id not in seen_track_ids:
        cursor.execute(
            insert_metadata,
            (
                track_id,
                e["master_metadata_track_name"],
                e["master_metadata_album_artist_name"],
                e.get("master_metadata_album_album_name"),
                in_library,
            ),
        )
        seen_track_ids.add(track_id)

print(f"\nInserted {len(seen_track_ids)} unique tracks into tracks_metadata")

# 2. track_uris
# maps every URI seen in history to its track_id
# INSERT IGNORE handles the same URI appearing in multiple play events

insert_uri = """
    INSERT IGNORE INTO track_uris (spotify_track_uri, track_id)
    VALUES (%s, %s)
"""

seen_uris = set()
for e in tracks:
    uri = e["spotify_track_uri"]
    if uri not in seen_uris:
        cursor.execute(insert_uri, (uri, e["track_id"]))
        seen_uris.add(uri)

print(f"Inserted {len(seen_uris)} URIs into track_uris")

# 3. listening_history
# one row per play event
# ts is stream END time in UTC per Spotify documentation

insert_history = """
    INSERT INTO listening_history
        (track_id, time_stamp, ms_played,
         reason_start, reason_end, shuffle, skipped)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

for e in tracks:
    ts = datetime.fromisoformat(e["ts"].replace("Z", "+00:00"))
    cursor.execute(
        insert_history,
        (
            e["track_id"],
            ts,
            e["ms_played"],
            e["reason_start"],
            e["reason_end"],
            bool(e["shuffle"]),
            bool(e["skipped"]),
        ),
    )

# 4. display name
insert_display_name = """
    INSERT INTO display_name
        (name)
    VALUES (%s)
"""

display_name = identity_data["displayName"]
cursor.execute(
    insert_display_name,
    [display_name],
)

# Commit & close

conn.commit()
print("Import complete.")
cursor.close()
conn.close()
