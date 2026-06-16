_ = """
2_prologue.py

Prologue - overview of the entire history

- n tracks/artists
- first song
- last/most recent song
"""

import streamlit as st
from datetime import datetime
import base64, io
from PIL import Image
from utils import build_df, footer_nav, format_full_time
from styles import apply_styles

st.set_page_config(
    page_title="Spotify Memoir | Prologue",
    page_icon="📓",
    layout="centered",
)


# Encode texture image as base64 for CSS background (full resolution)
img = Image.open("streamlit/white-paper-texture.png")
buf = io.BytesIO()
img.save(buf, format="JPEG", quality=85)
b64 = base64.b64encode(buf.getvalue()).decode()
bg_uri = f"data:image/jpeg;base64,{b64}"

apply_styles(bg_uri)

_ = """
Data loading + merge
"""
df = build_df()

_ = """
Overview stats 
"""
n_tracks = df["track_id"].nunique()
n_artists = df["artist_name"].nunique()
n_albums = df["album_name"].nunique()
n_plays = len(df)

total_ms = df["ms_played"].sum()
total_seconds = int(total_ms / 1_000)
total_minutes = int(total_seconds / 60)
total_hours = int(total_minutes / 60)
total_days = int(total_hours / 24)

date_min = df["time_stamp"].min().date()
date_max = df["time_stamp"].max().date()
n_calendar_days = (date_max - date_min).days + 1
avg_min_per_day = round(total_minutes / n_calendar_days)

# First + last played
df_sorted = df.sort_values("time_stamp")

first_row = df_sorted.iloc[0]
last_row = df_sorted.iloc[-1]

first_track = first_row["track_name"]
first_artist = first_row["artist_name"]

last_track = last_row["track_name"]
last_artist = last_row["artist_name"]

first_time = format_full_time(first_row["time_stamp"])
last_time = format_full_time(last_row["time_stamp"])

_ = """
Page Contents
"""

st.markdown(
    f"""
    <div class="page-title">Prologue</div>

    <div class="page-text">
    Over {n_calendar_days:,} days this story unfolded across {n_tracks:,} songs, {n_albums:,} albums, {n_artists:,} artists, and {total_hours:,} hours of listening.
    </div><br>
    
    <div class="page-text">
    The first song I listened to was {first_track} by {first_artist} on {first_time}.
    </div><br>

    <div class="page-text">
    The last song I listened to was {last_track} by {last_artist} on {last_time}.
    </div><br>

    <div class="page-text">
    I typically listened to music for {avg_min_per_day:,} minutes a day.
    </div>
    """,
    unsafe_allow_html=True,
)


# footer_nav(prev="1_toc.py", next="3_temp.py")
