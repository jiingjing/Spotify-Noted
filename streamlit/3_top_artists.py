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
    """,
    unsafe_allow_html=True,
)


_ = """
Top picks
"""
st.markdown(
    f"""
    <div class="page-caption">
    Figure 1.1: Top Artists
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

# footer_nav(prev="1_toc.py", next="3_temp.py")
