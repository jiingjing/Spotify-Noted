_ = """
4_top_albums.py

Places I Call Home
Top Albums
"""

import streamlit as st
import base64, io
from PIL import Image
from utils import build_df, footer_nav, PERIOD_OPTIONS, filter_period
from styles import apply_styles
import plotly.express as px

st.set_page_config(
    page_title="Spotify Memoir | Chapter II",
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
n_albums = df["album_name"].nunique()

_ = """
Page Contents
"""

st.markdown(
    f"""
    <div class="page-title">Chapter II</div>

    <div class="page-subtitle">Places I Call Home</div>
    
    <div class="page-text">
    There are {n_albums:,} albums I have visited, but only some that feel like home. 
    </div><br>
    <div class="page-text">
    These are the albums I returned to most often, the places I couldn't resist revisiting.
    </div><br>
    """,
    unsafe_allow_html=True,
)


_ = """
Section 1: Top albums by play frequency
"""
st.markdown(
    f"""
    <div class="page-caption">
    Figure 2.1: Top Albums by Play Frequency
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

top_albums = (
    df_period.groupby(["album_name", "artist_name"])
    .size()
    .reset_index(name="plays")
    .sort_values("plays", ascending=False)
    .head(top_n)
)
top_albums["label"] = top_albums["album_name"] + " · " + top_albums["artist_name"]

fig = px.bar(
    top_albums.sort_values("plays"),
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
Section 2: Top albums by time played
"""

st.markdown(
    f"""
    <br>
    <div class="page-text">
    Stopping by is one thing; settling in is another. These are the albums where I said yes to the house tour.
    </div><br>

    <div class="page-caption">
    Figure 2.2: Top Albums by Hours Played
    </div><br>
    """,
    unsafe_allow_html=True,
)

album_time = (
    df_period.groupby(["album_name", "artist_name"])["ms_played"]
    .sum()
    .reset_index()
    .assign(hours=lambda x: (x["ms_played"] / 3_600_000).round(1))
    .sort_values("hours", ascending=False)
    .head(top_n)
)
album_time["label"] = album_time["album_name"] + " · " + album_time["artist_name"]
fig = px.bar(
    album_time.sort_values("hours"),
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

footer_nav("4_top_albums.py")
