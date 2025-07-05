import streamlit as st
import json
from summarizer import summarize_and_label
from news_scraper import fetch_rss_news
from cluster import cluster_articles
import os


summary_path = "summary_output.json"

# Load only if file exists and is not empty
if os.path.exists(summary_path) and os.path.getsize(summary_path) > 0:
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_data = json.load(f)
else:
    summary_data = {}
    st.warning("⚠️ Summary file not found or empty. Please run summarization first.")


st.set_page_config(page_title="NewsNexus", layout="wide")
st.title("🗞️ NewsNexus: Real-Time AI News Summarizer")

st.sidebar.header("📂 Filter Options")


if st.button("🧠 Summarize Today's News"):
    with st.spinner("Summarizing..."):
        from summarizer import summarize_and_label, group_by_topic
        from news_scraper import fetch_rss_news
        from cluster import cluster_articles

        articles = fetch_rss_news()
        clusters = cluster_articles(articles, num_clusters=min(len(articles) // 4, 15))
        results = summarize_and_label(clusters)
        summary_data = group_by_topic(results)

        with open("summary_output.json", "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        st.success("✅ Summary generated and saved.")

else:
    # Load from existing file if button not clicked
    try:
        with open("summary_output.json", "r", encoding="utf-8") as f:
            summary_data = json.load(f)
    except FileNotFoundError:
        st.warning("📁 No summary file found. Click 'Summarize Today's News' first.")

# Sidebar topic filter
if summary_data and isinstance(summary_data, dict):
    all_topics = sorted(summary_data.keys())
    selected_topic = st.sidebar.selectbox("🧠 Filter by Topic", ["All Topics"] + all_topics)

    # Display all topics or filtered one
    topics_to_display = all_topics if selected_topic == "All Topics" else [selected_topic]

    for topic in topics_to_display:
        st.subheader(f"🧠 Topic: {topic}")
        for idx, cluster in enumerate(summary_data[topic], 1):
            with st.expander(f"🔹 Subtopic {idx}: {cluster['summary'][:80]}..."):
                st.markdown(f"**Summary:** {cluster['summary']}")
                st.markdown("---")
                for article in cluster["articles"]:
                    source = article.get("source", "Unknown")
                    title = article.get("title", "No Title")
                    st.markdown(f"• `{source}` — **{title}**")

    # Download option
    st.download_button("📥 Download Summary JSON", json.dumps(summary_data, indent=2), "news_summary.json")
    
else:
    st.sidebar.warning("⚠️ No topics found in summary data.")
    selected_topic = "All Topics"
