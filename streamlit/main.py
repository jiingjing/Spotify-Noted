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
        st.Page("3_top_artists.py", title="I. People I Kept Returning To"),
        st.Page("4_top_albums.py", title="II. Places I Called Home"),
        st.Page("5_top_tracks.py", title="III. Now That's What I Call Music!"),
        st.Page("6_habits.py", title="IV. Daily Rituals"),
        st.Page("7_timeline.py", title="V. The Years That Changed Me"),
        st.Page("8_epilogue.py", title="Epilogue"),
        st.Page("9_appendix.py", title="Appendix"),
    ]
)

pg.run()
