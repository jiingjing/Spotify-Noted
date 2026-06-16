_ = """
7_timeline.py

Listening history 
"""

import streamlit as st
import base64, io
from PIL import Image
from utils import build_df, footer_nav, PERIOD_OPTIONS, filter_period
from styles import apply_styles
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Spotify Memoir | Chapter V",
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
    <div class="page-title">Chapter V</div>

    <div class="page-subtitle">The Years That Changed Me</div>
    
    <div class="page-text">
    Every year leaves behind its own unique soundtrack. As Heraclitus once said, change is the only constant in life.
    </div><br>
    """,
    unsafe_allow_html=True,
)


# footer_nav(prev="1_toc.py", next="3_temp.py")

df = build_df()

_ = """
section 1: memoir at a glance
- bar chart of songs per year
- caption: some years I hardly stopped listening, others were quieter
"""

st.markdown(
    """
    <div class="page-text">
    Some years I hardly stopped listening whilst others were quieter.
    </div><br>
    <div class="page-caption">
    Figure 5.1: Bar chart of frequency of plays per year
    </div><br>
    """,
    unsafe_allow_html=True,
)

plays_per_year = (
    df.groupby("year")
    .size()
    .reset_index(name="plays")
    .sort_values("plays", ascending=False)
)


fig = px.bar(
    plays_per_year.sort_values("year"),
    x="plays",
    y="year",
    orientation="h",
    labels={"plays": "Plays", "year": "Year"},
    color_discrete_sequence=["#f79d97"],
)
fig.update_layout(
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

_ = """
section 2: discoveries
- # new tracks discovered over time
- new tracks discovered in selected month, ranked by overall all-time plays
- caption: every year introduced something new
"""

st.markdown(
    """
    <div class="page-text">
    Each year introduced something new.
    </div><br>
    <div class="page-caption">
    Figure 5.2: Count of new tracks listened to per month
    </div><br>
    """,
    unsafe_allow_html=True,
)

st.caption("New tracks discovered per month")

# New tracks over time
first_plays = df.groupby("track_id")["time_stamp"].min().reset_index()
first_plays.columns = ["track_id", "first_play"]
first_plays = first_plays.set_index("first_play").sort_index()

new_tracks = first_plays.resample("ME").size().reset_index(name="new_tracks")
new_tracks["cumulative"] = new_tracks["new_tracks"].cumsum()

fig = px.bar(
    new_tracks,
    x="first_play",
    y="new_tracks",
    title="New tracks discovered",
    labels={"first_play": "", "new_tracks": "New tracks"},
    color_discrete_sequence=["#f79d97"],
)
fig.update_layout(
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
    <div class="page-caption">
    Figure 5.3: Cumulative frequency of new tracks listened to per month
    </div><br>
    """,
    unsafe_allow_html=True,
)

st.caption("Cumulative tracks discovered")
fig = px.line(
    new_tracks,
    x="first_play",
    y="cumulative",
    labels={"first_play": "", "cumulative": "Total tracks"},
)
fig.update_traces(line_color="#7F77DD")
fig.update_layout(
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

_ = """
section 3: discoveries in a selected month
- new tracks discovered in selected month, ranked by overall all-time plays
- caption: each month brought in a new favorite
"""

st.markdown(
    """
    <div class="page-text">
    Each month brought with it a new future favourite.
    </div><br>
    <div class="page-caption">
    Figure 5.4: Overall most played tracks discovered in the selected month
    </div><br>
    """,
    unsafe_allow_html=True,
)

# Month selector
df["year_month"] = df["time_stamp"].dt.to_period("M").astype(str)

selected_month = st.selectbox(
    "Month",
    sorted(df["year_month"].unique(), reverse=True),
)

# First play per track
first_seen = df.groupby("track_id")["time_stamp"].min().dt.to_period("M").astype(str)

# Track IDs first discovered in selected month
track_ids = first_seen[first_seen == selected_month].index

# Top new tracks in that month
# Rank by by plays over all-time
top_new_tracks = (
    df[df["track_id"].isin(track_ids)]
    .groupby(["track_id", "track_name", "artist_name"])
    .size()
    .reset_index(name="plays")
    .sort_values("plays", ascending=False)
)

# Display
if top_new_tracks.empty:
    st.caption("No new tracks discovered this month.")
else:
    for _, row in top_new_tracks.head(10).iterrows():
        st.markdown(
            f"""
            <div class="plot-text">
            <strong>{row['track_name']}</strong> | {row['artist_name']} | {row['plays']} plays
            </div><br>""",
            unsafe_allow_html=True,
        )

st.divider()

_ = """
section 4: changes over years
- top artists played by month 
- caption: no two years sounded quite the same
"""

st.markdown(
    """
    <div class="page-text">
    Looking back, each year had its own feel. No two years sounded quite the same.
    </div><br>
    <div class="page-caption">
    Figure 5.5: Most played artists in selected year
    </div><br>
    """,
    unsafe_allow_html=True,
)

# Year selector
selected_year = st.selectbox(
    "Year",
    sorted(df["year"].unique(), reverse=True),
)


# Top N artists by plays
top_n = 20

artist_counts = (
    df[df["year"] == selected_year]
    .groupby("artist_name")
    .size()
    .reset_index(name="plays")
    .sort_values("plays", ascending=False)
)

# Keep top N and combine the rest as "Other"/"Everyone Else"
top = artist_counts.head(top_n)
other = pd.DataFrame(
    {
        "artist_name": ["Everyone Else"],
        "plays": [artist_counts.iloc[top_n:]["plays"].sum()],
    }
)

pie_df = pd.concat([top, other], ignore_index=True)

fig = px.pie(
    pie_df,
    names="artist_name",
    values="plays",
    hole=0.4,  # donut chart
)

fig.update_traces(
    # textinfo="percent+label",
    texttemplate="%{label} • %{percent}",
    sort=False,
)

n_labels = len(pie_df)

fig.update_layout(
    height=500,
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)

st.plotly_chart(fig, use_container_width=True)


st.divider()

_ = """
section 5: time capsule
- track and artist played the same day as current date and # of plays on that day
- caption: on this day
"""

st.markdown(
    """
    <div class="page-text">
    On this day, these were the songs keeping me company.
    </div><br>
    <div class="page-caption">
    Figure 5.6: Most played tracks on this date in previous years
    </div><br>
    """,
    unsafe_allow_html=True,
)

today = pd.Timestamp.now().normalize()

on_this_day = df[
    (df["time_stamp"].dt.month == today.month)
    & (df["time_stamp"].dt.day == today.day)
    & (df["time_stamp"].dt.year < today.year)
]

if on_this_day.empty:
    st.caption("No plays recorded on this date in previous years.")
else:
    # track_id-based aggregation
    otd_summary = (
        on_this_day.groupby(["year", "track_id"])
        .agg(
            track_name=("track_name", "first"),
            artist_name=("artist_name", "first"),
            plays=("play_id", "count"),
        )
        .reset_index()
        .sort_values(["year", "plays"], ascending=[False, False])
        .groupby("year")
        .head(3)
    )

    # full year range
    all_years = range(today.year - 1, df["year"].min() - 1, -1)

    for year in all_years:
        st.markdown(
            f"""
            <div class="plot-text"><u>
            {year}
            </u></div><br>
            """,
            unsafe_allow_html=True,
        )

        group = otd_summary[otd_summary["year"] == year]

        if group.empty:
            st.markdown(
                f"""
                <div class="plot-text">
                No tracks played.
                </div><br>
                """,
                unsafe_allow_html=True,
            )
        else:
            for _, row in group.iterrows():
                st.markdown(
                    f"""
                    <div class="plot-text">
                    <strong>{row['track_name']}</strong> | {row['artist_name']} | {row['plays']} plays
                    </div><br>""",
                    unsafe_allow_html=True,
                )
