"""
load Spotify extended streaming data into a MySQL database

note: found inconsistent metadata capitalisation e.g.
spotify track uri                       track_name  artist_name  album_name
spotify:track:0IEVKWduAaMcZepZQVr80T	Likey	    TWICE	     Twicetagram
spotify:track:0Wf8czfSUf68GaqkgaeJY9	LIKEY	    TWICE	     twicetagram
spotify:track:4P66rfizAl2nIJCICSMymC	Likey	    TWICE	     Twicetagram

this is likely from Spotify relinking tracks over time (and not updating it when the song was added to a playlist and played from there)

these should be treated the same for my purposes and so should have the same id

so instead of using spotify_track_uri as the id, i decide to make an id that groups tracks as the same if the only difference is capitalisation in track/album name

---

There are still more incompatibilites this doesn't catch - but much fewer! 
e.g.
history 
    "master_metadata_track_name": "Who Knew - Edit",
    "master_metadata_album_artist_name": "P!nk",
    "master_metadata_album_album_name": "I'm Not Dead",
    "spotify_track_uri": "spotify:track:2hns6Dv29Yrg68AVTJiAyA",

library
    "artist" : "P!nk",
    "album" : "I'm Not Dead",
    "track" : "Who Knew",
    "uri" : "spotify:track:7FpoD2ZlcBSj05rEHSZoiB"
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

HISTORY_JSON_GLOB = (
    "raw_data/spotify/Spotify Extended Streaming History/Streaming_History_Audio_*.json"
)

LIBRARY_JSON = "raw_data/spotify/Spotify Account Data/YourLibrary.json"

#  Connect to MySQL database

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

#  Load JSON files

all_events = []
for path in glob.glob(HISTORY_JSON_GLOB):
    with open(path, encoding="utf-8") as f:
        all_events.extend(json.load(f))

print(f"Loaded {len(all_events)} total audio events")

with open(LIBRARY_JSON, encoding="utf-8") as f:
    library_data = json.load(f)

#  Filter to tracks only (for audio events)

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

#  Filter library to track uri's only

library_uris = {track["uri"] for track in library_data["tracks"]}
print(f"Loaded {len(library_uris)} tracks from library")


#  Report cases of tracks with multiple Spotify URIs:
#      when case-insensitive artist, case-insensitive track name and case-insensitive album name have multiple URIs
#      generate a canonical track id

from collections import defaultdict

groups = defaultdict(list)

for e in tracks:
    key = (
        e["master_metadata_track_name"].casefold().strip(),  # case-insensitive
        e["master_metadata_album_artist_name"].casefold().strip(),  # case-insensitive
        e["master_metadata_album_album_name"].casefold().strip(),  # case-insensitive
    )

    groups[key].append(
        (
            e["spotify_track_uri"],
            e["master_metadata_track_name"],
            e["master_metadata_album_artist_name"],
            e["master_metadata_album_album_name"],
        )
    )

print("Tracks with multiple Spotify URIs")
for key, values in groups.items():
    uris = {v[0] for v in values}
    if len(uris) > 1:
        print(key)
        for uri, track, artist, album in sorted(set(values)):
            print(f"  {uri}")
            print(f"    Track : {track}")
            print(f"    Artist: {artist}")
            print(f"    Album : {album}")
        print()

import hashlib


def generate_track_id(track, artist, album):
    raw = "|".join([track.casefold().strip(), artist.casefold().strip(), album.casefold().strip()])
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


for e in tracks:
    track_id = generate_track_id(
        e["master_metadata_track_name"],
        e["master_metadata_album_artist_name"],
        e["master_metadata_album_album_name"],
    )
    e["track_id"] = track_id

# Report tracks that have incompatibilites with metadata in library vs. when played from library 

unique_lib_ids = set([e['track_id'] for e in library_data["tracks"]])
unique_track_ids = set([t['track_id'] for t in tracks])
in_library_but_not_history=unique_lib_ids.difference(unique_track_ids)
temp=library_data['tracks']
for track_id in in_library_but_not_history:
    for t in temp:
    	if t['track_id']==track_id:
            print(t['track']+' '+t['artist'])


#  1. tracks_metadata

insert_metadata = """
    INSERT IGNORE INTO tracks_metadata
        (track_id, spotify_track_uri, track_name, artist_name, album_name, in_library)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

seen_track_ids = set()
for e in tracks:
    track_id = e["track_id"]
    uri = e["spotify_track_uri"]
    if track_id not in seen_track_ids:
        cursor.execute(
            insert_metadata,
            (
                track_id,
                uri,
                e["master_metadata_track_name"],
                e["master_metadata_album_artist_name"],
                e.get("master_metadata_album_album_name"),
                uri in library_uris,
            ),
        )
        seen_track_ids.add(track_id)

print(f"Inserted {len(seen_track_ids)} unique tracks into tracks_metadata")

#  2. listening_history

insert_history = """
    INSERT INTO listening_history
        (track_id, spotify_track_uri, time_stamp, ms_played,
         reason_start, reason_end, shuffle, skipped)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

for e in tracks:
    ts = datetime.fromisoformat(e["ts"].replace("Z", "+00:00"))

    cursor.execute(
        insert_history,
        (
            e["track_id"],
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
