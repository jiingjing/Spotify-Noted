_ = """
5_top_tracks.py

Now That's What I Call Music!
Top Tracks
"""

import streamlit as st
import base64, io
from PIL import Image
from utils import build_df, footer_nav, PERIOD_OPTIONS, filter_period
from styles import apply_styles
import plotly.express as px

st.set_page_config(
    page_title="Spotify Memoir | Chapter III",
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
n_tracks = df["track_name"].nunique()

_ = """
Page Contents
"""

st.markdown(
    f"""
    <div class="page-title">Chapter III</div>

    <div class="page-subtitle">Now That's What I Call Music!</div>
    
    <div class="page-text">
    If I could make a 'NOW That’s What I Call Music' compilation, I'd have {n_tracks:,} tracks to pick from. These are the songs I'd reach for first.
    </div><br>
    """,
    unsafe_allow_html=True,
)


_ = """
Section 1: Top tracks by play frequency
"""
st.markdown(
    f"""
    <div class="page-caption">
    Figure 3.1: Top Tracks by Play Frequency
    </div><br>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([2, 1])
with col1:
    period = st.radio(
        "Period", PERIOD_OPTIONS, horizontal=True, label_visibility="collapsed"
    )
with col2:
    top_n = st.slider("Show top", min_value=5, max_value=50, value=10, step=5)

df_period = filter_period(df, period)

top_tracks = (
    df_period.groupby("track_id")
    .agg(
        track_name=("track_name", "first"),
        artist_name=("artist_name", "first"),
        plays=("play_id", "count"),
    )
    .reset_index()
    .sort_values("plays", ascending=False)
    .head(top_n)
)

top_tracks["label"] = top_tracks["track_name"] + " · " + top_tracks["artist_name"]

fig = px.bar(
    top_tracks.sort_values("plays"),
    x="plays",
    y="label",
    orientation="h",
    labels={"plays": "Plays", "label": ""},
    color_discrete_sequence=["#f79d97"],
)
fig.update_layout(
    height=max(300, top_n * 28),
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

_ = """
Section 2: Top tracks by time played
"""

st.markdown(
    f"""
    <br>
    <div class="page-text">
    Some songs only got a single spin, but these tracks stayed on repeat.
    </div><br>

    <div class="page-caption">
    Figure 3.2: Top Tracks by Hours Played
    </div><br>
    """,
    unsafe_allow_html=True,
)

track_time = (
    df_period.groupby("track_id")["ms_played"]
    .sum()
    .reset_index()
    .merge(
        df_period[["track_id", "track_name", "artist_name"]].drop_duplicates(),
        on="track_id",
    )
    .assign(hours=lambda x: (x["ms_played"] / 3_600_000).round(1))
    .sort_values("hours", ascending=False)
    .head(top_n)
)
track_time["label"] = track_time["track_name"] + " · " + track_time["artist_name"]
fig = px.bar(
    track_time.sort_values("hours"),
    x="hours",
    y="label",
    orientation="h",
    labels={"hours": "Hours", "label": ""},
    color_discrete_sequence=["#f7e297"],
)
fig.update_layout(
    height=max(300, top_n * 28),
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

_ = """
Section 3: Most returned to tracks 
- Tracks played across the most separate days (measure of loyalty over time)
"""

st.markdown(
    f"""
    <div class="page-text">
    Many songs are just a fad, these are the ones that I have been loyal to.
    </div><br>

    <div class="page-caption">
    Figure 3.3: Tracks revisited across the greatest number of days
    </div><br>
    """,
    unsafe_allow_html=True,
)


returned_to = (
    df_period.groupby("track_id")
    .agg(
        track_name=("track_name", "first"),
        artist_name=("artist_name", "first"),
        total_plays=("play_id", "count"),
        days_played=("time_stamp", lambda x: x.dt.date.nunique()),
    )
    .reset_index()
    .sort_values("days_played", ascending=False)
    .head(top_n)
)
returned_to["label"] = returned_to["track_name"] + " · " + returned_to["artist_name"]

fig = px.bar(
    returned_to.sort_values("days_played"),
    x="days_played",
    y="label",
    orientation="h",
    labels={"days_played": "Days played", "label": ""},
    hover_data={"total_plays": True},
    color_discrete_sequence=["#7F77DD"],
)
fig.update_layout(
    height=max(300, top_n * 28),
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

# footer_nav(prev="1_toc.py", next="3_temp.py")
