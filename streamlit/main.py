_ = """
main.py

Run app and create navigation
"""

import streamlit as st

pg = st.navigation(
    [
        st.Page("0_cover.py", title="Cover"),
        st.Page("1_toc.py", title="Table of Contents"),
        st.Page("2_prologue.py", title="Prologue"),
        st.Page("3_top_artists.py", title="People I kept returning to"),
        st.Page("4_top_albums.py", title="Places I called home"),
        st.Page("5_top_tracks.py", title="Now that's what I call music"),
        st.Page("6_habits.py", title="Daily rituals"),
        st.Page("7_timeline.py", title="The years that changed me"),
        st.Page("8_epilogue.py", title="Epilogue"),
        st.Page("9_appendix.py", title="Appendix"),
    ]
)

pg.run()
