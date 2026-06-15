_ = """
streamlit_app.py
--------------
Uses streamlit to display Spotify data

Home page with
- overview of stats
- time spent
- top picks
"""

import streamlit as st
from utils import build_df, filter_period, PERIOD_OPTIONS

st.set_page_config(
    page_title="Spotify Noted",
    page_icon="📝",
    layout="wide",
)

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

written_date = f"{date_max.day} {date_max.strftime('%b %Y')}".lower()
span_str = f"{date_min.strftime('%d %b %Y')} — {date_max.strftime('%d %b %Y')}"

_ = """
Hero
- Top section of page
"""
st.caption("spotify-noted")
st.title("Your listening, noted.")
st.caption(f"{n_tracks:,} tracks · {n_artists:,} artists · {n_albums:,} albums")
st.caption(span_str)

st.divider()

_ = """
Overview 
"""
st.subheader("Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Unique tracks", f"{n_tracks:,}")
col2.metric("Unique artists", f"{n_artists:,}")
col3.metric("Unique albums", f"{n_albums:,}")
col4.metric("Total plays", f"{n_plays:,}", help="Including skips")

st.divider()

_ = """
Time spent 
"""
st.subheader("Time spent")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Days", f"{total_days:,}")
col2.metric("Hours", f"{total_hours:,}")
col3.metric("Minutes", f"{total_minutes:,}")
col4.metric("Seconds", f"{total_seconds:,}")

st.caption(f"That's {avg_min_per_day} min a day, on average.")

st.divider()

_ = """
Top picks
"""
st.subheader("Top picks")

period = st.radio(
    label="Period",
    options=PERIOD_OPTIONS,
    horizontal=True,
    label_visibility="collapsed",
)

df_period = filter_period(df, period)

top_track = (
    df_period.groupby(["track_id", "track_name", "artist_name"])
    .agg(plays=("play_id", "count"))
    .reset_index()
    .sort_values("plays", ascending=False)
    .iloc[0]
)
top_artist = (
    df_period.groupby("artist_name")
    .agg(plays=("play_id", "count"))
    .reset_index()
    .sort_values("plays", ascending=False)
    .iloc[0]
)
top_album = (
    df_period.groupby(["album_name", "artist_name"])
    .agg(plays=("play_id", "count"))
    .reset_index()
    .sort_values("plays", ascending=False)
    .iloc[0]
)

col1, col2, col3 = st.columns(3)

with col1:
    st.caption("track")
    st.markdown(f"**{top_track['track_name']}**")
    st.caption(f"{top_track['artist_name']}  \n{top_track['plays']:,} plays")

with col2:
    st.caption("artist")
    st.markdown(f"**{top_artist['artist_name']}**")
    st.caption(f"{top_artist['plays']:,} plays")

with col3:
    st.caption("album")
    st.markdown(f"**{top_album['album_name']}**")
    st.caption(f"{top_album['artist_name']}  \n{top_album['plays']:,} plays")

st.divider()

_ = """
Footer
"""
col1, col2 = st.columns(2)
col1.caption("spotify-noted")
col2.caption(f"written {written_date}")
