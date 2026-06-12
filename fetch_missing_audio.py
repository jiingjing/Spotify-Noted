"""
fetch_missing_audio.py
----------------------
Downloads audio for library tracks that are missing from tracks_audio,
and registers downloaded files in tracks_audio.

- Only targets tracks where in_library = TRUE and no entry in tracks_audio
- spotDL downloads as {track-id}.mp3, then renamed to {track_id}.mp3
- spotDL skips files that already exist, so re-running is safe
"""

import os
import subprocess

import mysql.connector

# Config

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",  # change this to your MySQL password
    "database": "spotify_noted",
}

AUDIO_DIR = "raw_data/audio"
OUTPUT_TEMPLATE = os.path.join(AUDIO_DIR, "{track-id}")
BATCH_SIZE = 10

# Fetch library tracks missing from tracks_audio

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

cursor.execute("""
    SELECT tm.track_id, tu.spotify_track_uri
    FROM tracks_metadata tm
    JOIN track_uris tu ON tm.track_id = tu.track_id
    LEFT JOIN tracks_audio ta ON tm.track_id = ta.track_id
    WHERE tm.in_library = TRUE
    AND ta.track_id IS NULL
""")
rows = cursor.fetchall()

# deduplicate by track_id, keeping first URI seen
seen = set()
track_rows = []
for track_id, uri in rows:
    if track_id not in seen:
        track_rows.append((track_id, uri))
        seen.add(track_id)

print(f"Found {len(track_rows)} library tracks missing audio")

if not track_rows:
    print("Nothing to download.")
    cursor.close()
    conn.close()
    exit()

# Convert URIs to Spotify URLs

urls = [f"https://open.spotify.com/track/{uri.split(':')[-1]}" for _, uri in track_rows]

# Download via spotDL

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

total_batches = (len(urls) - 1) // BATCH_SIZE + 1
for i in range(0, len(urls), BATCH_SIZE):
    batch = urls[i : i + BATCH_SIZE]
    print(f"Downloading batch {i // BATCH_SIZE + 1} of {total_batches}")
    subprocess.run(
        [
            "spotdl",
            "download",
            *batch,
            "--output",
            OUTPUT_TEMPLATE,
            "--format",
            "mp3",
            "--threads",
            "4",
            "--save-errors",
            "logs/spotdl_errors.txt",
        ],
    )

# Rename and register downloaded files in tracks_audio

insert_audio = """
    INSERT IGNORE INTO tracks_audio (track_id, audio_file_path)
    VALUES (%s, %s)
"""

registered = 0
missing = 0
total = len(track_rows)

for i, (track_id, uri) in enumerate(track_rows, start=1):
    song_id = uri.split(":")[-1]
    spotdl_path = os.path.join(AUDIO_DIR, f"{song_id}.mp3")
    final_name = f"{track_id}.mp3"
    final_path = os.path.join(AUDIO_DIR, final_name)

    if os.path.exists(spotdl_path):
        os.rename(spotdl_path, final_path)

    if os.path.exists(final_path):
        cursor.execute(insert_audio, (track_id, final_name))
        registered += 1
    else:
        missing += 1
        print(f"Missing: {song_id}.mp3")

    print(f"Registering: {i}/{total} — {registered} saved, {missing} missing", end="\r")

conn.commit()
print(f"\nDone. Registered {registered} tracks, {missing} missing.")

cursor.close()
conn.close()
