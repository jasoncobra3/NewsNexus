from sentence_transformers import SentenceTransformer
from news_scraper import fetch_rss_news
from sklearn.cluster import KMeans
from collections import defaultdict

model = SentenceTransformer('all-MiniLM-L6-v2')  

def cluster_articles(articles, num_clusters=10):
    texts = [article["title"] + " " + article["summary"] for article in articles]
    embeddings = model.encode(texts)

    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings)

    clustered = defaultdict(list)
    for idx, label in enumerate(labels):
        clustered[label].append(articles[idx])
    return clustered



if __name__ == "__main__":
    articles = fetch_rss_news()
    num_clusters = min(10, max(3, len(articles) // 5))  # Adaptive clustering
    clusters = cluster_articles(articles, num_clusters=num_clusters)


    for cluster_id, articles in clusters.items():
        print(f"\n🧠 Cluster {cluster_id} ({len(articles)} articles):")
        for a in articles[:2]:  # Print only first 2 articles per cluster
            print(f"• {a['title']}")
