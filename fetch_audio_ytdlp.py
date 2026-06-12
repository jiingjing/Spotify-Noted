import yt_dlp
import os
import mysql.connector

# Config

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",  # change this to your MySQL password
    "database": "spotify_noted",
}

AUDIO_DIR = "raw_data/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Fetch library tracks missing audio

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

cursor.execute("""
    SELECT tm.track_id, tm.track_name, tm.artist_name, tu.spotify_track_uri
    FROM tracks_metadata tm
    JOIN track_uris tu ON tm.track_id = tu.track_id
    LEFT JOIN tracks_audio ta ON tm.track_id = ta.track_id
    WHERE tm.in_library = TRUE
    AND ta.track_id IS NULL
""")
rows = cursor.fetchall()

# deduplicate by track_id
seen = set()
track_rows = []
for track_id, track_name, artist_name, uri in rows:
    if track_id not in seen:
        track_rows.append((track_id, track_name, artist_name, uri))
        seen.add(track_id)

print(f"Found {len(track_rows)} library tracks missing audio")

# Download via yt-dlp

insert_audio = """
    INSERT IGNORE INTO tracks_audio (track_id, audio_file_path)
    VALUES (%s, %s)
"""

registered = 0
missing = 0
errors = []
total = len(track_rows)

for i, (track_id, track_name, artist_name, uri) in enumerate(track_rows, start=1):
    final_name = f"{track_id}.mp3"
    final_path = os.path.join(AUDIO_DIR, final_name)

    # skip if already downloaded
    if os.path.exists(final_path):
        cursor.execute(insert_audio, (track_id, final_name))
        registered += 1
        print(
            f"Registering: {i}/{total} — {registered} saved, {missing} missing",
            end="\r",
        )
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
            errors.append(f"{query}")

    except Exception as e:
        missing += 1
        errors.append(f"{query} — {e}")

    print(f"Registering: {i}/{total} — {registered} saved, {missing} missing", end="\r")

# Write error log

if errors:
    with open("logs/yt_dlp_errors.txt", "w", encoding="utf-8") as f:
        for line in errors:
            f.write(line + "\n")

conn.commit()
print(f"\nDone. Registered {registered} tracks, {missing} missing.")
print(f"Errors written to logs/yt_dlp_errors.txt" if errors else "No errors.")

cursor.close()
conn.close()
