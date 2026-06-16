_ = """
3_top_artists.py

People I Kept Returning To
Top Artists
"""

import streamlit as st
import base64, io
from PIL import Image
from utils import build_df, footer_nav, PERIOD_OPTIONS, filter_period
from styles import apply_styles
import plotly.express as px

st.set_page_config(
    page_title="Spotify Memoir | Chapter I",
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
n_artists = df["artist_name"].nunique()

_ = """
Page Contents
"""

st.markdown(
    f"""
    <div class="page-title">Chapter I</div>

    <div class="page-subtitle">People I Kept Returning To</div>
    
    <div class="page-text">
    Over the years I have listened to {n_artists:,} different artists, yet there are some voices I keep going back to again and again.
    </div><br>
    <div class="page-text">
    These are the artists I reached for most often, the names that appear again and again throughout this memoir.
    </div><br>
    """,
    unsafe_allow_html=True,
)


_ = """
Section 1: Top aristis by play frequency
"""
st.markdown(
    f"""
    <div class="page-caption">
    Figure 1.1: Top Artists by Play Frequency
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

top_artists = (
    df_period.groupby("artist_name")
    .size()
    .reset_index(name="plays")
    .sort_values("plays", ascending=False)
    .head(top_n)
)

fig = px.bar(
    top_artists.sort_values("plays"),
    x="plays",
    y="artist_name",
    orientation="h",
    labels={"plays": "Plays", "artist_name": ""},
    color_discrete_sequence=["#f79d97"],
)
fig.update_layout(height=max(300, top_n * 28))

st.plotly_chart(fig, use_container_width=True)

st.divider()

_ = """
Section 2: Top aristis by time played
"""

st.markdown(
    f"""
    <div class="page-text">
    Every press of the play button only took a second, but staying to listen took much longer. These are the artists who occupied the greatest share of my listening life.
    </div><br>

    <div class="page-caption">
    Figure 1.2: Top Artists by Hours Played
    </div><br>
    """,
    unsafe_allow_html=True,
)

artist_time = (
    df_period.groupby("artist_name")["ms_played"]
    .sum()
    .reset_index()
    .assign(hours=lambda x: (x["ms_played"] / 3_600_000).round(1))
    .sort_values("hours", ascending=False)
    .head(top_n)
)
fig = px.bar(
    artist_time.sort_values("hours"),
    x="hours",
    y="artist_name",
    orientation="h",
    labels={"hours": "Hours", "artist_name": ""},
    color_discrete_sequence=["#f7e297"],
)
fig.update_layout(height=max(300, top_n * 28))
st.plotly_chart(fig, use_container_width=True)

st.divider()

_ = """
Section 3: Treemap
- Music Library Structure (Artist → Album → Track)
"""
st.markdown(
    f"""
    <div class="page-text">
    The artists I return to are rarely represented by a single song. They come with eras built from albums and tracks.
    </div><br>

    <div class="page-caption">
    Figure 1.3: Artist → Album → Track hierarchy for most-played artists
    </div>
    """,
    unsafe_allow_html=True,
)

df_top_artists = df.copy()
top_artists = df_top_artists["artist_name"].value_counts().head(top_n).index
df_treemap = (
    df[df["artist_name"].isin(top_artists)]
    .groupby(["artist_name", "album_name", "track_id", "track_name"])
    .agg(plays=("play_id", "count"))
    .reset_index()
)

fig = px.treemap(
    df_treemap,
    path=["artist_name", "album_name", "track_name"],
    values="plays",
)
fig.update_layout(
    margin=dict(l=0, r=0, t=20, b=0),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

# footer_nav(prev="1_toc.py", next="3_temp.py")
