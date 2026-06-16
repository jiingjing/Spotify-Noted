_ = """
6_habits.py

Daily Rituals
Listening habits
"""

import streamlit as st
import base64, io
from PIL import Image
from utils import build_df, footer_nav, PERIOD_OPTIONS, filter_period
from styles import apply_styles
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Spotify Memoir | Chapter IV",
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
pct_days_listened = 86  # todo: get % of days listened to music for out of total span of days in spotify history

_ = """
Section 1: Page Contents
"""

st.markdown(
    f"""
    <div class="page-title">Chapter IV</div>

    <div class="page-subtitle">Daily Rituals</div>
    
    <div class="page-text">
    After listening to music on {pct_days_listened}% of my days spent with Spotify, a few patterns begin to emerge. 
    </div><br>

    <div class="page-text">
    No matter the year, there are moments of the day when I'm far more likely to press play.
    </div><br>
    """,
    unsafe_allow_html=True,
)


_ = """
Section 2: Daily pattern - All-time
"""
st.markdown(
    f"""
    <div class="page-caption">
    Figure 4.1: Number of all-time plays per 5-minute window across 24 hours
    </div><br>
    """,
    unsafe_allow_html=True,
)

# Bin plays into 5-min intervals across 24h
df["minute_of_day"] = df["time_stamp"].dt.hour * 60 + df["time_stamp"].dt.minute
df["bin"] = (df["minute_of_day"] // 5) * 5

all_bins = pd.DataFrame({"bin": range(0, 1440, 5)})
tickvals = list(range(0, 1440, 120))
ticktext = [f"{h:02d}:00" for h in range(0, 24, 2)]

BAR_COLOR = "#7F77DD"
BAR_HEIGHT = 1  # fixed normalised height for opacity chart


def make_bin_df(source: pd.DataFrame) -> pd.DataFrame:
    bins = source.groupby("bin").size().reset_index(name="plays")
    bins = all_bins.merge(bins, on="bin", how="left").fillna(0)
    bins["plays"] = bins["plays"].astype(int)
    bins["time_label"] = pd.to_datetime(bins["bin"], unit="m").dt.strftime("%H:%M")
    return bins


def make_frequency_chart(bins: pd.DataFrame, height: int = 280) -> go.Figure:
    """Standard chart: bar height = play count."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=bins["bin"],
            y=bins["plays"],
            marker_color=BAR_COLOR,
            marker_line_width=0,
            width=4,
            hovertemplate="%{customdata}<br>%{y:,} plays<extra></extra>",
            customdata=bins["time_label"],
        )
    )
    fig.update_layout(
        xaxis=dict(
            tickvals=tickvals,
            ticktext=ticktext,
            range=[-5, 1440],
            showgrid=False,
            title="",
        ),
        yaxis=dict(title="Plays", showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
        bargap=0,
        height=height,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def make_opacity_chart(bins: pd.DataFrame, height: int = 180) -> go.Figure:
    """Fixed-height bars: opacity encodes play frequency."""
    max_plays = bins["plays"].max()
    # Normalise to [0.05, 1.0] so zero-play bins are invisible, max is fully opaque
    opacities = (
        (bins["plays"] / max_plays).clip(lower=0).tolist()
        if max_plays > 0
        else [0] * len(bins)
    )

    # One bar per bin with individual opacity via marker colors as rgba strings
    colors = [f"rgba(127,119,221,{round(o, 3)})" for o in opacities]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=bins["bin"],
            y=[BAR_HEIGHT] * len(bins),
            marker_color=colors,
            marker_line_width=0,
            width=4,
            hovertemplate="%{customdata[0]}<br>%{customdata[1]:,} plays<extra></extra>",
            customdata=list(zip(bins["time_label"], bins["plays"])),
        )
    )
    fig.update_layout(
        xaxis=dict(
            tickvals=tickvals,
            ticktext=ticktext,
            range=[-5, 1440],
            showgrid=False,
            title="",
        ),
        yaxis=dict(visible=False, range=[0, 1.2]),
        bargap=0,
        height=height,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def peak_metrics(bins: pd.DataFrame):
    peak = bins.loc[bins["plays"].idxmax()]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-label">Peak window</div>
            <div class="metric-value">{peak["time_label"]}</div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-label">Plays in that window</div>
            <div class="metric-value">{int(peak['plays']):,}</div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-label">Windows with plays</div>
            <div class="metric-value">{(bins['plays'] > 0).sum()} / 288</div>
            """,
            unsafe_allow_html=True,
        )


bins_all = make_bin_df(df)

st.markdown(
    f"""
    <br>
    <div class="plot-label">
    Play count
    </div><br>
    """,
    unsafe_allow_html=True,
)
st.plotly_chart(make_frequency_chart(bins_all, height=320), use_container_width=True)

st.markdown(
    f"""
    <br>
    <div class="plot-label">
    Relative frequency
    </div><br>
    """,
    unsafe_allow_html=True,
)
st.plotly_chart(make_opacity_chart(bins_all), use_container_width=True)

peak_metrics(bins_all)

_ = """
Section 3: Daily pattern - Year by year
"""

st.markdown(
    f"""
    <br>
    <div class="page-text">
    Life moves on and routines change. Here's how the story changed from year to year.
    </div><br>
    """,
    unsafe_allow_html=True,
)

years = sorted(df["year"].unique())

st.markdown(
    f"""
</div>
<div class="page-caption">
Figure 4.2: Number of plays in a year per 5-minute window across 24 hours
</div><br>
""",
    unsafe_allow_html=True,
)

for year in years:
    bins_year = make_bin_df(df[df["year"] == year])
    st.markdown(
        f"""
    <div class="plot-label">
    {year}
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.plotly_chart(make_opacity_chart(bins_year, height=120), use_container_width=True)

_ = """
Section 4: all hour-of-day and calendar plots
"""
st.markdown(
    f"""
    <div class="page-text">
    Some routines belong to weekdays, others only appear at the weekend.
    </div><br>
    <div class="page-caption">
    Figure 4.3: Hour x Day heatmap of plays per hour
    </div><br>
    """,
    unsafe_allow_html=True,
)

DOW_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

heatmap_data = df.groupby(["dow", "hour"]).size().reset_index(name="plays")
heatmap_pivot = (
    heatmap_data.pivot(index="dow", columns="hour", values="plays")
    .reindex(DOW_ORDER)
    .fillna(0)
)

fig = px.imshow(
    heatmap_pivot,
    labels={"x": "Hour of day", "y": "", "color": "Plays"},
    aspect="auto",
    color_continuous_scale="Purples",
)
fig.update_layout(
    coloraxis_showscale=False,
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)
