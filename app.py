import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="IntelSync Dashboard", layout="wide")
st.title("🧠 IntelSync Market Intelligence")

# --- Load and show articles ---
with open("data/sample_articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)
df = pd.DataFrame(articles)
df["fetched_at"] = pd.to_datetime(df["fetched_at"])

st.subheader("Scraped Articles")
st.dataframe(df[["title", "summary", "fetched_at"]], use_container_width=True)

# --- Sentiment bar chart + alert ---
if "sentiment" in df.columns:
    st.subheader("Sentiment Scores")
    st.bar_chart(df.set_index("title")["sentiment"])

    avg_sent = df["sentiment"].mean()
    if avg_sent < 0:
        st.error(f"⚠️ Overall market sentiment is negative! (avg: {avg_sent:.2f})")
    else:
        st.success(f"Overall market sentiment is positive (avg: {avg_sent:.2f})")

# --- Executive Insights text panel ---
st.subheader("Executive Insights")
with open("data/insights_summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()
st.text_area("", summary, height=300)

# --- Footer / Meta ---
st.markdown(
    """
    **Tech Stack:** Python • ADK • BigQuery • Cloud NL API • Streamlit  
    **Repo:** [GitHub](https://github.com/mneang/intelsync)  
    """
)