_ = """
1_toc.py

Table of contents

| Dashboard         | Memoir                       | Content                                                                                                |
| ----------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------ |
| Overview          | Prologue                     | n days/songs/albums/artists/hours, first/last song + datetime, avg mins a day                          |
| Top Artists       | People I Kept Returning To   | bar chart top n artists by plays/time of PERIOD_OPTIONS, treemap artist → album → track                |
| Top Albums        | Places I Called Home         | bar chart top n albums by plays/time of PERIOD_OPTIONS                                                 |
| Most Played Songs | Now That's What I Call Music | bar chart top n tracks by plays/time of PERIOD_OPTIONS, bar chart greatest revisits by days            |
| Listening Habits  | Daily Rituals                | play count 5min intervals in 24h all-time/year-on-year, hour×day-of-week heatmap of plays per hour     |
| Timeline          | The Years That Changed Me    | bar chart of freq of plays per year, bar chart of freq/cumfreq new tracks per month,                   |
|                   |                              | most played tracks discovered in selected month, donut chart top artists in selected year, on this day |
| Summary           | Epilogue                     | n tracks/albums/artists/days/hours/plays                                                               |
| Statistics        | Appendix                     |

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
