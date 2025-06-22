import streamlit as st
import pandas as pd
import json
import altair as alt

# ─── COLOR PALETTE ────────────────────────────────────────────────────────────
BACKGROUND_HEX = "#F9FAFB"  # very light gray
TEXT_HEX       = "#111827"  # dark charcoal
ACCENT_BLUE    = "#4285F4"  # Google blue
ACCENT_GREEN   = "#34A853"  # Google green
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="IntelSync Dashboard", page_icon="🧠", layout="wide")

# Custom CSS
st.markdown(f"""
<style>
  .reportview-container .main {{ background-color: {BACKGROUND_HEX}; }}
  .sidebar .sidebar-content {{ background-color: {BACKGROUND_HEX}; }}
  h1, h2, h3 {{ color: {ACCENT_BLUE} !important; }}
  .stText, .stMarkdown {{ color: {TEXT_HEX} !important; }}
</style>
""", unsafe_allow_html=True)

# Load articles
with open("data/sample_articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)
df = pd.DataFrame(articles)
df["fetched_at"] = pd.to_datetime(df["fetched_at"])

# Header & timestamp
st.markdown("<h1>🧠 IntelSync Market Intelligence</h1>", unsafe_allow_html=True)
st.markdown(f"**Last run:** {df['fetched_at'].max():%Y-%m-%d %H:%M:%S UTC}", unsafe_allow_html=True)

# Scraped Articles
st.markdown("## Scraped Articles", unsafe_allow_html=True)
st.dataframe(df[["title","summary","fetched_at"]], use_container_width=True)

# Sentiment Chart & Alert
if "sentiment" in df.columns:
    st.markdown("## Sentiment Scores", unsafe_allow_html=True)
    chart = (
        alt.Chart(df)
           .mark_bar(color=ACCENT_GREEN)
           .encode(
               x=alt.X("title:N", sort=None, title="Article"),
               y=alt.Y("sentiment:Q", title="Sentiment Score"),
               tooltip=["title","sentiment"]
           )
           .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)

    avg = df["sentiment"].mean()
    if avg < 0:
        st.error(f"⚠️ Overall market sentiment is negative! (avg: {avg:.2f})")
    else:
        st.success(f"✅ Overall market sentiment is positive (avg: {avg:.2f})")

# Entity Table
try:
    with open("data/entities.json", "r", encoding="utf-8") as f:
        entities = json.load(f)
    ent_df = pd.DataFrame(entities)
    st.markdown("## Key Entities", unsafe_allow_html=True)
    st.table(ent_df)
except FileNotFoundError:
    pass  # no entities yet

# Executive Insights
st.markdown("## Executive Insights", unsafe_allow_html=True)
with open("data/insights_summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()
st.text_area("", summary, height=300)

# Footer
st.markdown(
    "**Tech Stack:** Python • ADK • BigQuery • Cloud NL API • Streamlit • Altair  \n"
    "**Repo:** [GitHub](https://github.com/mneang/intelsync)",
    unsafe_allow_html=True
)