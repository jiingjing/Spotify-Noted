import streamlit as st


def apply_styles(bg_uri: str):
    st.markdown(
        f"""
<link href="https://fonts.googleapis.com/css2?family=Baskervville:ital,wght@0,400..700;1,400..700&display=swap" rel="stylesheet">

<style>
#MainMenu, header, footer {{
    visibility: hidden;
}}

[data-testid="stAppViewContainer"] {{
    background: url("{bg_uri}") repeat;
    background-size: 600px 600px;
}}

.block-container {{
    max-width: 750px;
    padding-top: 8rem;
}}

.cover-title {{
    font-family: "Baskervville", serif;
    font-size: 5.5rem;
    font-weight: 400;
    font-variant: small-caps;
    letter-spacing: 0.08em;
    text-align: center;
    color: #222;
    line-height: 0.95;
    margin-bottom: 2rem;
}}

.cover-byline {{
    font-family: "Baskervville", serif;
    font-style: italic;
    font-size: 1.4rem;
    text-align: center;
    color: #555;
    margin-bottom: 4rem;
}}

.cover-dates {{
    font-family: "Baskervville", serif;
    font-size: 1rem;
    text-align: center;
    color: #444;
    letter-spacing: 0.04em;
}}


.page-title {{
    font-family: "Baskervville", serif;
    font-size: 3.5rem;
    font-weight: 400;
    font-variant: small-caps;
    letter-spacing: 0.08em;
    text-align: center;
    color: #222;
    line-height: 0.95;
    margin-bottom: 2rem;
}}

.page-subtitle {{
    font-family: "Baskervville", serif;
    font-size: 2.5rem;
    letter-spacing: 0.08em;
    text-align: center;
    color: #222;
    line-height: 0.95;
    margin-bottom: 2rem;
}}

.page-text {{
    font-family: "Baskervville", serif;
    font-size: 1.5rem;
    text-align: left;
    color: #222;
    line-height: 1.6; 
}}

.page-text ul {{
    list-style: none;
    padding-left: 0;
}}

.page-text ul ul {{
    margin-left: 20px;
}}

.page-caption {{
    font-family: "Baskervville", serif;
    font-style: italic;
    font-size: 1.0rem;
    text-align: left;
    color: #222;
    line-height: 1.6; 
}}

.metric-label {{
    font-family: "Baskervville", serif;
    font-size: 1rem;
    text-align: center;
    color: #222;
    letter-spacing: 0.08em;
}}

.metric-value {{
    font-family: "Baskervville", serif;
    font-size: 1rem;
    text-align: center;
    color: #222;
    line-height: 1.6; 
}}

.plot-label {{
    font-family: "Baskervville", serif;
    font-size: 1rem;
    text-align: center;
    color: #666;
    line-height: 1.6; 
}}

</style>
""",
        unsafe_allow_html=True,
    )
