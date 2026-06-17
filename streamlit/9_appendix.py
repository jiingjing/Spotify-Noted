_ = """
9_appendix.py

Appendix

A. Complete Listening History Catalogue
| Track | Artist | Album | First Played | Last Played | Days Returned To | Plays | Skip % | Shuffle % |
| ----- | ------ | ----- | ------------ | ----------- | ---------------- | ----- | ------ | --------- |

B. Complete Listening Calendar

- Calendar heatmap (github style)

C. Distribution of Listening

- Plays over all-time with month intervals
- Ridgeline plot of top n artists' plays over all-time with month intervals
- Line plot of top n artists ' plays over all-time with month intervals with a slider for months shown

D. Notes & Additional Figures

- shuffle vs non-shuffle
- skipped vs non-skipped
- most songs played in a day
- fun facts
"""

import streamlit as st
import base64, io
import plotly.express as px
import plotly.graph_objects as go

from PIL import Image
from utils import build_df, footer_nav, PERIOD_OPTIONS, filter_period
from styles import apply_styles
import pandas as pd
import numpy as np

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
- Complete Listening History Catalogue
- dataframe
| Track | Artist | Album | First Played | Last Played | Days Returned To | Plays | Skip % | Shuffle % |
| ----- | ------ | ----- | ------------ | ----------- | ---------------- | ----- | ------ | --------- |
"""

st.markdown(
    """
    <div class="page-title">Appendix</div>

    <div class="page-subtitle">Appendix A: Complete Listening History Catalogue</div>
    """,
    unsafe_allow_html=True,
)

# st.caption("When you first listened to a track, and how many times since.")

discovery = (
    df.groupby("track_id")
    .agg(
        track_name=("track_name", "first"),
        artist_name=("artist_name", "first"),
        album_name=("album_name", "first"),
        first_play=("time_stamp", "min"),
        last_play=("time_stamp", "max"),
        days_played=("time_stamp", lambda x: x.dt.date.nunique()),
        total_plays=("play_id", "count"),
        skipped_pct=("skipped", lambda x: x.sum() / x.count()),
        shuffle_pct=("shuffle", lambda x: x.sum() / x.count()),
    )
    .reset_index()
    .sort_values("total_plays", ascending=False)
)
discovery["first_play"] = discovery["first_play"].dt.strftime("%d %b %Y")
discovery["last_play"] = discovery["last_play"].dt.strftime("%d %b %Y")

st.dataframe(
    discovery.rename(
        columns={
            "track_name": "Track",
            "artist_name": "Artist",
            "album_name": "Album",
            "first_play": "First listened",
            "last_play": "Last listened",
            "days_played": "Days Returned To",
            "total_plays": "Total plays",
            "skipped_pct": "Skip %",
            "shuffle_pct": "Shuffle %",
        }
    ).drop("track_id", axis=1),
    use_container_width=True,
    hide_index=True,
)

st.divider()

_ = """
Appendix B
- Complete Listening Calendar
- github style calendar heatmap
"""

st.markdown(
    """
    <div class="page-subtitle">Appendix B: Complete Listening Calendar</div>
    """,
    unsafe_allow_html=True,
)

# year selection
year_options = sorted(df["year"].unique(), reverse=True)
selected_year = st.selectbox("Year", year_options, label_visibility="collapsed")

df_year = df[df["year"] == selected_year].copy()

# build full daily series (fill missing days)
full_range = pd.date_range(
    start=f"{selected_year}-01-01", end=f"{selected_year}-12-31", freq="D"
)

daily = (
    df_year.set_index("time_stamp")
    .resample("D")
    .size()
    .reindex(full_range, fill_value=0)
    .rename("plays")
    .reset_index()
    .rename(columns={"index": "time_stamp"})
)

# anchor grid to Monday of first week
start = pd.Timestamp(f"{selected_year}-01-01")
grid_start = start - pd.Timedelta(days=start.weekday())

daily["dow"] = daily["time_stamp"].dt.weekday  # Mon=0

# correct week index relative to grid start
daily["week"] = (daily["time_stamp"] - grid_start).dt.days // 7

# build matrix (7 rows x weeks)
max_week = daily["week"].max() + 1

z = np.zeros((7, max_week))
hover = np.empty((7, max_week), dtype=object)

for _, row in daily.iterrows():
    w = int(row["week"])
    d = int(row["dow"])
    z[d, w] = row["plays"]
    hover[d, w] = row["time_stamp"].strftime("%d %b %Y")

# plot heatmap
fig = go.Figure(
    go.Heatmap(
        z=z,
        colorscale="Blues",
        showscale=False,
        xgap=3,
        ygap=3,
        customdata=hover,
        hovertemplate="%{customdata}<br>%{z} plays<extra></extra>",
    )
)

# y-axis (days of week)
fig.update_yaxes(
    scaleanchor="x",
    scaleratio=2,
    tickvals=[0, 1, 2, 3, 4, 5, 6],
    ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    autorange="reversed",
    showgrid=False,
)

# month labels (aligned to first week appearance)
monthly_ticks = daily.groupby(daily["time_stamp"].dt.month)["week"].min()

month_labels = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

fig.update_xaxes(
    tickmode="array",
    tickvals=monthly_ticks.values,
    ticktext=month_labels[: len(monthly_ticks)],
    showgrid=False,
    showticklabels=True,
)
fig.update_layout(
    height=220,
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()


_ = """
Appendix C
Distribution of Listening
- Plays over all-time with month intervals
- Ridgeline plot of top n artists' plays over all-time with month intervals
- Line plot of top n artists ' plays over all-time with month intervals with a slider for months shown
"""

st.markdown(
    """
    <div class="page-subtitle">Appendix C: Distribution of Listening</div>
    """,
    unsafe_allow_html=True,
)

# Section C.1: Plays over all-time with month intervals

granularity = st.radio(
    "Granularity",
    ["Daily", "Weekly", "Monthly", "Yearly"],
    horizontal=True,
    label_visibility="collapsed",
)

freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "ME", "Yearly": "YE"}
plays_over_time = (
    df.set_index("time_stamp")
    .resample(freq_map[granularity])
    .size()
    .reset_index(name="plays")
)

fig = px.bar(
    plays_over_time,
    x="time_stamp",
    y="plays",
    labels={"time_stamp": "", "plays": "Plays"},
    color_discrete_sequence=["#f79d97"],
)
fig.update_layout(
    showlegend=False,
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

# Section C.2: Ridgeline plot of top n artists' plays over all-time with month intervals

top_n = st.slider("Show top (Figure C.2)", min_value=5, max_value=50, value=10, step=5)

df_top_artists = df.copy()
top_artists = df_top_artists["artist_name"].value_counts().head(top_n).index
df_top = df_top_artists[df_top_artists["artist_name"].isin(top_artists)].copy()

# month encoding
df_top["month_num"] = df_top["time_stamp"].dt.year * 12 + (
    df_top["time_stamp"].dt.month - 1
)
# global month range
all_months = np.arange(df_top["month_num"].min(), df_top["month_num"].max() + 1)

# plot ridgeline
fig = go.Figure()

spacing = 1.25

for i, artist in enumerate(top_artists):
    artist_data = df_top[df_top["artist_name"] == artist]
    counts = artist_data["month_num"].value_counts().sort_index()
    counts = counts.reindex(all_months, fill_value=0)
    x = counts.index.values
    y = counts.values.astype(float)
    if y.max() > 0:
        y = y / y.max()
    y_plot = y + i * spacing
    month_labels = [
        pd.to_datetime(f"{m // 12}-{(m % 12) + 1:02d}-01").strftime("%B %Y") for m in x
    ]

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y_plot,
            mode="lines",
            line=dict(width=2),
            name=artist,
            customdata=np.stack((month_labels, counts.values), axis=-1),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Month: %{customdata[0]}<br>"
                "Plays: %{customdata[1]}<br>"
                "<extra></extra>"
            ),
        )
    )

# year ticks
start_year = df_top["time_stamp"].dt.year.min()
end_year = df_top["time_stamp"].dt.year.max()

tickvals = [year * 12 for year in range(start_year, end_year + 1)]
ticktext = [str(year) for year in range(start_year, end_year + 1)]

# plot layout
fig.update_layout(
    height=100 + top_n * 25,
    hovermode="closest",
    xaxis=dict(
        title="Year",
        tickvals=tickvals,
        ticktext=ticktext,
        showgrid=True,
    ),
    yaxis=dict(showticklabels=False),
    legend=dict(orientation="h", xanchor="center", x=0.5, y=-0.3),
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)

st.plotly_chart(fig, use_container_width=True)

# Section C.3: Line plot of top n artists ' plays over all-time with month intervals with a slider for months shown

df["month"] = df["time_stamp"].dt.to_period("M").astype(str)

col1, col2 = st.columns([2, 1])

with col1:
    top_n = st.slider(
        "Show top (Figure C.3)", min_value=5, max_value=50, value=10, step=5
    )

df_top_artists = df.copy()
top_artists = df_top_artists["artist_name"].value_counts().head(top_n).index

monthly = df.groupby(["month", "artist_name"]).size().reset_index(name="plays")
monthly = monthly[monthly["artist_name"].isin(top_artists)]
months = sorted(monthly["month"].unique())

with col2:
    window = st.slider("Months shown", min_value=6, max_value=len(months), value=24)


monthly_filtered = monthly[monthly["month"].isin(months[-window:])]
fig = px.line(
    monthly_filtered,
    x="month",
    y="plays",
    color="artist_name",
    markers=True,
)
# plot layout
fig.update_layout(
    legend=dict(orientation="h", xanchor="center", x=0.5, y=-0.3),
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)

st.plotly_chart(fig, use_container_width=True)


st.divider()


_ = """
Appendix D
Streaming Behavior 
- shuffle vs non-shuffle
- skipped vs non-skipped
- most songs played in a day
- fun facts
"""

st.markdown(
    """
    <div class="page-subtitle">Appendix D: Streaming Behavior </div>
    """,
    unsafe_allow_html=True,
)

period = st.radio(
    "Period", PERIOD_OPTIONS, horizontal=True, label_visibility="collapsed"
)
df_period = filter_period(df, period)

# Overview metrics
st.subheader("Overview")

total = len(df_period)
skipped = df_period["skipped"].sum()
shuffle = df_period["shuffle"].sum()

skip_rate = round(100 * skipped / total, 1) if total else 0
shuffle_rate = round(100 * shuffle / total, 1) if total else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total plays", f"{total:,}")
col2.metric("Skipped", f"{int(skipped):,}")
col3.metric("Skip rate", f"{skip_rate}%")
col4.metric("Shuffled", f"{int(shuffle):,}")
col5.metric("Shuffle rate", f"{shuffle_rate}%")

st.divider()

# Contingency table
df_period["skipped_cat"] = np.where(df_period["skipped"] == 1, "Skipped", "Not skipped")
df_period["shuffle_cat"] = np.where(
    df_period["shuffle"] == 1, "Shuffled", "Not shuffled"
)

rows = ["Skipped", "Not skipped"]
cols = ["Shuffled", "Not shuffled"]

# count table
ct = pd.crosstab(df_period["skipped_cat"], df_period["shuffle_cat"]).reindex(
    index=rows, columns=cols
)

# row % table
ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
ct_pct = ct_pct.round(1)

# total row counts
total_counts = ct.sum(axis=0)
grand_total = total_counts.sum()

# total row % of grand total
total_pct = (total_counts / grand_total * 100).round(1)

# combined table (counts and %)
combined = ct.astype(str) + " (" + ct_pct.astype(str) + "%)"

# add total column (row-wise totals)
combined["Total"] = ct.sum(axis=1).astype(str) + " (100%)"

# add total row
combined.loc["Total"] = (
    total_counts.astype(str) + " (" + total_pct.astype(str) + "%)"
).tolist() + [f"{grand_total} (100%)"]

# display: skip vs shuffle behavior matrix
st.dataframe(combined, use_container_width=True)


# reason_end breakdown
st.subheader("How plays end")

reason_end = (
    df_period.groupby("reason_end")
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)
fig = px.pie(reason_end, names="reason_end", values="count", hole=0.4)
fig.update_traces(
    texttemplate="%{label} • %{percent}",
    sort=False,
)
fig.update_layout(
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=150),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# reason_start breakdown
st.subheader("How plays start")

reason_start = (
    df_period.groupby("reason_start")
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)
fig = px.pie(reason_start, names="reason_start", values="count", hole=0.4)
fig.update_traces(
    texttemplate="%{label} • %{percent}",
    sort=False,
)
fig.update_layout(
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=150),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()


# skip + shuffle rate over time
st.subheader("Skip and shuffle rate over time")

skip_over_time = (
    df.set_index("time_stamp")
    .resample("ME")
    .agg(
        total=("play_id", "count"),
        skipped=("skipped", "sum"),
        shuffled=("shuffle", "sum"),
    )
    .reset_index()
)

# rates
skip_over_time["skip_rate"] = (
    100 * skip_over_time["skipped"] / skip_over_time["total"]
).round(1)

skip_over_time["shuffle_rate"] = (
    100 * skip_over_time["shuffled"] / skip_over_time["total"]
).round(1)

# reshape to long format
plot_df = skip_over_time.melt(
    id_vars="time_stamp",
    value_vars=["skip_rate", "shuffle_rate"],
    var_name="metric",
    value_name="rate",
)

# rename labels
plot_df["metric"] = plot_df["metric"].map(
    {"skip_rate": "Skip rate", "shuffle_rate": "Shuffle rate"}
)

fig = px.line(
    plot_df,
    x="time_stamp",
    y="rate",
    color="metric",
    labels={"time_stamp": "", "rate": "Rate (%)", "metric": ""},
)
fig.update_layout(
    legend=dict(orientation="h", xanchor="center", x=0.5),
    margin=dict(l=0, r=0, t=10, b=0),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

_ = """
Appendix E
Notes & Additional Figures
- most songs played in a day
- fun facts
"""

st.markdown(
    """
    <div class="page-subtitle">Appendix E: Notes & Additional Figures</div>
    """,
    unsafe_allow_html=True,
)
