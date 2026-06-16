_ = """
1_toc.py

Table of contents
"""

import streamlit as st
import base64, io
from PIL import Image
from utils import build_df, footer_nav
from styles import apply_styles

st.set_page_config(
    page_title="Spotify Memoir | Table of Contents",
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

st.markdown(
    """
    <div class="page-title">Table of Contents</div>

    <div class="page-subtitle">Table of Contents</div>
    
    <div class="page-text">

    <ul>
    <li><strong>Prologue</strong></li>

    <li><strong>Chapters</strong>
    <ul>
    <li>I. People I kept returning to</li>
    <li>II. Places I called home</li>
    <li>III. Now that's what I call music</li>
    <li>IV. Daily rituals</li>
    <li>V. The years that changed me</li>
    </ul>
    </li>

    <li><strong>Epilogue</strong></li>
    <li><strong>Appendix</strong></li>

    </ul>

    </div>
    """,
    unsafe_allow_html=True,
)
