"""
fetch_audio.py
--------------
Downloads audio for library tracks in three stages:

1. spotDL (Spotify URL)        - has the best metadata matching
2. spotDL retry (missing only) - second attempt for spotDL failures (e.g. due to host blocks)
3. yt-dlp (still missing)      - fallback using "track - artist" search

- Only downloads tracks where in_library = TRUE in tracks_metadata
- spotDL downloads as {track-id}.mp3, which is then renamed to {track_id}.mp3
- yt-dlp downloads directly to {track_id}.mp3
- Re-running is safe as existing files and DB rows are skipped
"""

import os
import subprocess
import mysql.connector
import yt_dlp
from dotenv import dotenv_values

# Config

config = dotenv_values(".env")

DB_CONFIG = {
    "host": config["DB_HOST"],
    "user": config["DB_USER"],
    "password": config["DB_PASS"],
    "database": config["DB_NAME"],
}

AUDIO_DIR = config["AUDIO_DIR"]
OUTPUT_TEMPLATE = os.path.join(AUDIO_DIR, "{track-id}")
BATCH_SIZE = int(config["SPOTDL_BATCH_SIZE"])
LOG_DIR = config["LOG_DIR"]

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

YTDLP_LOG_PATH = os.path.join(LOG_DIR, "yt_dlp_errors.txt")
SPOTDL_LOG_PATH = os.path.join(LOG_DIR, "spotdl_errors.txt")

# Helpers

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

insert_audio = """
    INSERT IGNORE INTO tracks_audio (track_id, audio_file_path)
    VALUES (%s, %s)
"""


def fetch_missing():
    """fetch library tracks with no entry in tracks_audio, deduplicated by track_id"""
    cursor.execute("""
        SELECT tm.track_id, tm.track_name, tm.artist_name, tu.spotify_track_uri
        FROM tracks_metadata tm
        JOIN track_uris tu ON tm.track_id = tu.track_id
        LEFT JOIN tracks_audio ta ON tm.track_id = ta.track_id
        WHERE tm.in_library = TRUE
        AND ta.track_id IS NULL
    """)
    rows = cursor.fetchall()
    seen = set()
    track_rows = []
    for track_id, track_name, artist_name, uri in rows:
        if track_id not in seen:
            track_rows.append((track_id, track_name, artist_name, uri))
            seen.add(track_id)
    return track_rows


def run_spotdl(urls):
    """run spotDL in batches for a list of Spotify URLs"""
    total_batches = (len(urls) - 1) // BATCH_SIZE + 1
    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i : i + BATCH_SIZE]
        print(f"Batch {i // BATCH_SIZE + 1} of {total_batches}")
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
                SPOTDL_LOG_PATH,  # saves failed URLs to a file
            ]
        )


def rename_and_register(track_rows):
    """rename spotDL {track-id}.mp3 → {track_id}.mp3 and register in DB"""
    registered = 0
    missing = 0
    for track_id, _, _, uri in track_rows:
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

    conn.commit()
    return registered, missing


# Stage 1: spotDL

print("Stage 1: spotDL")
track_rows = fetch_missing()
print(f"Found {len(track_rows)} library tracks missing audio")

if track_rows:
    urls = [
        f"https://open.spotify.com/track/{uri.split(':')[-1]}"
        for _, _, _, uri in track_rows
    ]
    run_spotdl(urls)
    registered, missing = rename_and_register(track_rows)
    print(f"Stage 1 done - {registered} saved, {missing} missing\n")
    print(f"Errors written to {SPOTDL_LOG_PATH}\n")

# Stage 2: spotDL retry

print("Stage 2: spotDL retry")
track_rows = fetch_missing()
print(f"Found {len(track_rows)} tracks still missing")

if track_rows:
    urls = [
        f"https://open.spotify.com/track/{uri.split(':')[-1]}"
        for _, _, _, uri in track_rows
    ]
    run_spotdl(urls)
    registered, missing = rename_and_register(track_rows)
    print(f"Stage 2 done - {registered} saved, {missing} missing\n")
    print(f"Errors written to {SPOTDL_LOG_PATH}\n")

# Stage 3: yt-dlp fallback

print("Stage 3: yt-dlp fallback")
track_rows = fetch_missing()
print(f"Found {len(track_rows)} tracks still missing")

yt_errors = []
registered = 0
missing = 0
total = len(track_rows)

for i, (track_id, track_name, artist_name, _) in enumerate(track_rows, start=1):
    final_name = f"{track_id}.mp3"
    final_path = os.path.join(AUDIO_DIR, final_name)

    if os.path.exists(final_path):
        cursor.execute(insert_audio, (track_id, final_name))
        registered += 1
        print(f"  {i}/{total} - {registered} saved, {missing} missing", end="\r")
        continue

    query = f"{track_name} - {artist_name}"
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": final_path.replace(".mp3", ".%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{query}"])

        if os.path.exists(final_path):
            cursor.execute(insert_audio, (track_id, final_name))
            registered += 1
        else:
            missing += 1
            yt_errors.append(query)

    except Exception as e:
        missing += 1
        yt_errors.append(f"{query} - {e}")

    print(f"  {i}/{total} - {registered} saved, {missing} missing", end="\r")

if yt_errors:
    with open(YTDLP_LOG_PATH, "w", encoding="utf-8") as f:
        for line in yt_errors:
            f.write(line + "\n")

conn.commit()
print(f"\nStage 3 done - {registered} saved, {missing} missing")
if yt_errors:
    print(f"\nErrors written to {YTDLP_LOG_PATH}")

# Summary

remaining = fetch_missing()
print(f"\nComplete. {len(remaining)} tracks still missing audio.")

cursor.close()
conn.close()
