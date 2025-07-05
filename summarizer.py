import os
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from collections import defaultdict
from langchain_groq import ChatGroq
from news_scraper import fetch_rss_news
from cluster import cluster_articles
from dotenv import load_dotenv



load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="mistral-saba-24b",
    temperature=0.2 , 
)

CATEGORIES = [
    "Politics", "Economy", "Business", "Climate", "Health", "Technology",
    "Science", "World", "Crime & Law", "Social Issues", "Sports", "Entertainment"
]
category_str = ", ".join(CATEGORIES)


# Prompt template
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a strict and concise news summarizer."),
    HumanMessage(content=f"""
Analyze the following grouped news headlines and summaries:

{{news_chunk}}

Pick the most appropriate topic **strictly** from the following list:
{category_str}

Output STRICTLY in this format, and NOTHING else:
Topic: <one-line topic name>
Summary: <2–3 sentence summary>

Rules:
- NO reasoning, thoughts, or steps.
- DO NOT mention instructions or the user.
- DO NOT say things like 'Alright' or 'Let me'.
- DO NOT repeat topic names from previous clusters.
- Pick the most *distinctive* topic that summarizes the group.
- DO NOT include 'Cluster', 'User', or 'Instructions' in your output.
- Just directly output the Topic and Summary only.
""")
])

chain = prompt | llm

# Main function to summarize clusters
def summarize_and_label(clustered_articles):
    results = {}

    for cluster_id, articles in clustered_articles.items():
        # Combine news titles + summaries
        news_chunk = "\n".join([f"- {a['title']}: {a['summary']}" for a in articles])

        try:
            output = chain.invoke({"news_chunk": news_chunk})
            response_text = output.content.strip()
            lines = response_text.strip().split("\n", 1)
            if len(lines) < 2 or not lines[0].startswith("Topic:") or not lines[1].startswith("Summary:"):
                    raise ValueError("Invalid model output format")

            topic_line, summary_line = lines

            topic = topic_line.replace("Topic:", "").strip()
            summary = summary_line.replace("Summary:", "").strip()
            
            #  ✅ Clean and validate topic
            valid_topics = set(CATEGORIES)
            if topic not in valid_topics:
                print(f"⚠️ Model returned unexpected topic: {topic}. Forcing fallback.")
                topic = "Uncategorized"

            results[cluster_id] = {
                "label": topic,
                "summary": summary,
                "articles": articles
            }

        except Exception as e:
            print(f"⚠️ Error in cluster {cluster_id}: {e}")
            results[cluster_id] = {
                "label": "Unknown",
                "summary": "Could not summarize.",
                "articles": articles
            }

    return results



def group_by_topic(results):
    grouped = defaultdict(list)

    for cluster_id, data in results.items():
        topic = data["label"]
        summary = data["summary"]
        grouped[topic].append({
            "cluster_id": int(cluster_id),
            "summary": summary,
            "articles": data["articles"]
        })

    return grouped


if __name__ == "__main__":
   

    articles = fetch_rss_news()
    clusters = cluster_articles(articles, num_clusters=5)
    results = summarize_and_label(clusters)

    # for cid, data in results.items():
    #     print(f"\n🧠 Cluster {cid} — {data['label']}")
    #     print(f"📌 Summary: {data['summary'][:200]}...")
    grouped_results = group_by_topic(results)

    for topic, clusters in grouped_results.items():
        print(f"\n🧠 Topic: {topic}")
        for idx, cluster in enumerate(clusters, 1):
            print(f"  🔹 Subtopic {idx}: {cluster['summary']}")
            
            
    import json

    with open("summary_output.json", "w", encoding="utf-8") as f:
        json.dump(grouped_results, f, indent=2, ensure_ascii=False)

    print("✅ Summary saved to summary_output.json")