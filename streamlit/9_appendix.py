_ = """
2_prologue.py

Prologue - overview
"""

import streamlit as st
import base64, io
import plotly.express as px
import plotly.graph_objects as go

from PIL import Image
from utils import build_df, footer_nav, PERIOD_OPTIONS, filter_period
from styles import apply_styles
import pandas as pd

st.set_page_config(
    page_title="Spotify Memoir | Appendix",
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

df = build_df()

_ = """
Appendix A
summary statistics
"""

st.markdown(
    """
    <div class="page-title">Appendix</div>

    <div class="page-subtitle">Appendix A: Summary Statistics</div>
    """,
    unsafe_allow_html=True,
)
