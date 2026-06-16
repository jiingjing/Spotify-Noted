_ = """
cover.py
--------------
Memoir-style cover page for the Spotify Noted app.
"""

import streamlit as st
import base64, io
from PIL import Image
from utils import build_df, footer_nav
from styles import apply_styles

st.set_page_config(
    page_title="Spotify Memoir | Cover",
    page_icon="📓",
    layout="centered",
)

df = build_df()

date_min = df["time_stamp"].min().date()
date_max = df["time_stamp"].max().date()


def fmt(d):
    return f"{d.day} {d.strftime('%B %Y')}"


span_str = f"{fmt(date_min)} — {fmt(date_max)}"

# Encode texture image as base64 for CSS background (full resolution)
img = Image.open("streamlit/white-paper-texture.png")
buf = io.BytesIO()
img.save(buf, format="JPEG", quality=85)
b64 = base64.b64encode(buf.getvalue()).decode()
bg_uri = f"data:image/jpeg;base64,{b64}"

apply_styles(bg_uri)

st.markdown(
    f"""
    <div class="cover-title">
        Spotify<br>
        Memoir
    </div>

    <div class="cover-byline">
        by Jane Doe
    </div>

    <div class="cover-dates">
        {span_str}
    </div>
    """,
    unsafe_allow_html=True,
)
