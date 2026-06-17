_ = """
8_epilogue.py

Epilogue - reflection
"""

import streamlit as st
import base64, io
from PIL import Image
from utils import build_df, footer_nav
from styles import apply_styles

st.set_page_config(
    page_title="Spotify Memoir | Epilogue",
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

st.markdown(
    f"""
    <div class="page-title">Epilogue</div>

    <div class="page-text">
    {n_tracks:,} tracks,<br>
    {n_albums:,} albums,<br>
    {n_artists:,} artists,<br>
    {total_days:,} days of listening,<br>
    {total_hours:,} hours of music, and<br>
    {n_plays:,} times I pressed play.<br>
    </div>
    """,
    unsafe_allow_html=True,
)


footer_nav("8_epilogue.py")
