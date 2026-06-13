"""
streamlit_app.py
--------------
Uses streamlit to display Spotify data
"""

import streamlit as st

st.title("Spotify Noted")

# Initialise connection
conn = st.connection("mysql", type="sql")

# Perform query
df = conn.query("SELECT * from tracks_metadata;", ttl=600)

# Print results
for row in df.itertuples():
    st.write(f"{row.track_name} - {row.artist_name}:")
