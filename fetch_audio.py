"""
use spotDL to download audio for the track uris in tracks_metadata (by converting them to URLs and feeding to spotDL)
update tracks_audio with the filename for each track's downloaded audio
the filename is the spotify_track_uri with "spotify:track:" removed and ".mp3" appended

note: spotdl skips files that already exist in the output directory by default
"""

import mysql.connector
import subprocess
import os

# Config

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",  # change this to your MySQL password
    "database": "spotify_noted",
}

URLS_FILE = "urls.txt"
AUDIO_DIR = "raw_data\\audio"
OUTPUT_TEMPLATE = os.path.join(AUDIO_DIR, "{track-id}")

# Export URIs from MySQL database + dump URLs to a text file

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

cursor.execute("SELECT spotify_track_uri FROM tracks_metadata")
uris = [row[0] for row in cursor.fetchall()]

# Convert URIs "spotify:track:2U6RSyXFnDVNYoD9iUgi09"
# to URLs      "https://open.spotify.com/track/2U6RSyXFnDVNYoD9iUgi09"

urls = [f"https://open.spotify.com/track/{uri.split(':')[-1]}" for uri in uris]

with open(URLS_FILE, "w") as f:
    for url in urls:
        f.write(url + "\n")

# assert len(urls) == len(uris), "Mismatch between number of URIs and URLs"
print(f"Exported {len(urls)} URLs to {URLS_FILE}")

# Then feed the file to spotdl + run spotdl

os.makedirs(AUDIO_DIR, exist_ok=True)

BATCH_SIZE = 50

for i in range(0, len(urls), BATCH_SIZE):
    batch = urls[i : i + BATCH_SIZE]
    print(
        f"Downloading batch {i // BATCH_SIZE + 1} of {(len(urls) - 1) // BATCH_SIZE + 1}"
    )
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
        ],
        check=True,
    )

# Register downloaded files in tracks_audio database table

insert_audio = """
    INSERT IGNORE INTO tracks_audio (spotify_track_uri, audio_file_path)
    VALUES (%s, %s)
"""

registered = 0
for url, uri in zip(
    urls, uris
):  # e.g., "https://open.spotify.com/track/2U6RSyXFnDVNYoD9iUgi09", "spotify:track:2U6RSyXFnDVNYoD9iUgi09"
    filename = f"{uri.split(':')[-1]}.mp3"  # e.g., "2U6RSyXFnDVNYoD9iUgi09.mp3"
    full_path = os.path.join(AUDIO_DIR, filename)

    if os.path.exists(full_path):
        cursor.execute(insert_audio, (uri, filename))
        registered += 1
    else:
        print(f"Missing: {filename} -- spotdl may have skipped {url}")

conn.commit()
print(f"Registered {registered} files in tracks_audio")

cursor.close()
conn.close()
