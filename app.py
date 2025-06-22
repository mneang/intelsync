import os
import streamlit as st
import pandas as pd
import json
import altair as alt
from google.cloud import bigquery

# ─── YOUR ADK COLOR PALETTE ───────────────────────────────────────────────────
BACKGROUND_HEX = "#202125"  # dark background
TEXT_HEX       = "#000000"  # light text
ACCENT_BLUE    = "#2b6b34"  # primary accent
ACCENT_NAVY    = "#bbe8d8"  # panel background
ACCENT_GREEN   = "#33ac5f"  # positive sentiment / chart bars
# ─────────────────────────────────────────────────────────────────────────────

# Page config
st.set_page_config(page_title="IntelSync Dashboard", page_icon="🧠", layout="wide")

# Inject CSS
st.markdown(f"""
<style>
  .reportview-container .main, .sidebar .sidebar-content {{
    background-color: {BACKGROUND_HEX};
  }}
  h1, h2, h3 {{ color: {ACCENT_BLUE} !important; }}
  .stText, .stMarkdown, .stDataFrame td, .stDataFrame th {{ color: {TEXT_HEX} !important; }}
  .stDataFrame thead th {{ background-color: {ACCENT_NAVY} !important; color: {TEXT_HEX} !important; }}
  .stMultiSelect > div div div span {{
    background-color: {ACCENT_BLUE} !important; color: white !important;
  }}
  .stDownloadButton>button {{ background-color: {ACCENT_GREEN} !important; color: white; }}
  .insights-card {{
    background-color: {ACCENT_NAVY};
    padding: 1rem;
    border-radius: 0.5rem;
    color: {TEXT_HEX};
  }}
</style>
""", unsafe_allow_html=True)

# ─── Load scraped articles ────────────────────────────────────────────────────
with open("data/sample_articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)
df = pd.DataFrame(articles)
df["fetched_at"] = pd.to_datetime(df["fetched_at"])

# ─── HEADER & RUN TIMESTAMP ───────────────────────────────────────────────────
st.markdown("<h1>🧠 IntelSync Market Intelligence</h1>", unsafe_allow_html=True)
last_run = df["fetched_at"].max()
st.markdown(f"**Last run:** {last_run:%Y-%m-%d %H:%M:%S UTC}", unsafe_allow_html=True)

# ─── FILTER by title ─────────────────────────────────────────────────────────
titles = df["title"].tolist()
selected = st.multiselect("Filter by Article Title", options=titles, default=titles)
filtered_df = df[df["title"].isin(selected)]

# ─── SCRAPED ARTICLES ─────────────────────────────────────────────────────────
st.markdown("## Scraped Articles", unsafe_allow_html=True)
st.dataframe(filtered_df[["title","summary","fetched_at"]], use_container_width=True)
csv_articles = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Articles CSV", csv_articles, "articles.csv", "text/csv")

# ─── SENTIMENT SCORES ─────────────────────────────────────────────────────────
if "sentiment" in filtered_df.columns:
    st.markdown("## Sentiment Scores", unsafe_allow_html=True)
    chart = (
        alt.Chart(filtered_df)
           .mark_bar(color=ACCENT_GREEN)
           .encode(
               x=alt.X("title:N", sort=None, title="Article"),
               y=alt.Y("sentiment:Q", title="Sentiment Score"),
               tooltip=["title","sentiment"]
           )
           .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)

    avg = filtered_df["sentiment"].mean()
    if avg < 0:
        st.error(f"⚠️ Overall market sentiment is negative! (avg: {avg:.2f})")
    else:
        st.success(f"✅ Overall market sentiment is positive (avg: {avg:.2f})")

# ─── KEY ENTITIES ──────────────────────────────────────────────────────────────
try:
    with open("data/entities.json", "r", encoding="utf-8") as f:
        entities = json.load(f)
    ent_df = pd.DataFrame(entities)
    st.markdown("## Key Entities", unsafe_allow_html=True)
    st.table(ent_df)
    csv_ent = ent_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Entities CSV", csv_ent, "entities.csv", "text/csv")
except FileNotFoundError:
    pass

# ─── EXECUTIVE INSIGHTS ───────────────────────────────────────────────────────
st.markdown("## Executive Insights", unsafe_allow_html=True)
with open("data/insights_summary.txt", "r", encoding="utf-8") as f:
    md = f.read()
st.markdown(f'<div class="insights-card">\n{md}\n</div>', unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown(
    """
    **Tech Stack:** Python • ADK • BigQuery • Cloud NL API • Streamlit • Altair  
    **Repo:** [GitHub](https://github.com/mneang/intelsync)  
    **Connect:** [LinkedIn](https://linkedin.com/in/mneang) • [Portfolio](https://mneang.github.io)  
    **#adkhackathon**
    """,
    unsafe_allow_html=True
)