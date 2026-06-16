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
    """,
    unsafe_allow_html=True,
)


_ = """
Top picks
"""
st.markdown(
    f"""
    <div class="page-caption">
    Figure 2.1: Top Albums
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
fig.update_layout(height=max(300, top_n * 28))
st.plotly_chart(fig, use_container_width=True)

# footer_nav(prev="1_toc.py", next="3_temp.py")
