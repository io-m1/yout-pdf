# algodev.py - Military-grade AlgoDev simulation engine
import networkx as nx
from collections import Counter
import re
from spacy import load as spacy_load
from sentence_transformers import SentenceTransformer, util
from io import StringIO
import pandas as pd

nlp = spacy_load("en_core_web_sm")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def chunk_text(text, max_chars=8000):
    """Split large text into chunks to avoid token limits"""
    chunks = []
    current = ""
    for line in text.split('\n'):
        if len(current) + len(line) > max_chars:
            chunks.append(current.strip())
            current = line
        else:
            current += "\n" + line
    if current:
        chunks.append(current.strip())
    return chunks

def simulate_dfil(full_text):
    """Enhanced DFIL: NER + semantic co-occurrence graph with centrality"""
    chunks = chunk_text(full_text)
    all_entities = []
    all_topics = []

    for chunk in chunks:
        doc = nlp(chunk)
        entities = [ent.text for ent in doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE', 'EVENT', 'WORK_OF_ART']]
        topics = [token.lemma_ for token in doc if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop and len(token.text) > 3]
        all_entities.extend(entities)
        all_topics.extend(topics)

    entity_counter = Counter(all_entities)
    topic_counter = Counter(all_topics)
    top_entities = [e for e, c in entity_counter.most_common(15)]
    top_topics = [t for t, c in topic_counter.most_common(30)]

    all_terms = list(set(top_entities + top_topics))
    if not all_terms:
        return [], nx.Graph(), []

    embeddings = embedder.encode(all_terms)
    G = nx.Graph()

    for i in range(len(all_terms)):
        for j in range(i+1, len(all_terms)):
            sim = util.cos_sim(embeddings[i], embeddings[j]).item()
            if sim > 0.45:  # Tuned threshold
                G.add_edge(all_terms[i], all_terms[j], weight=sim)

    # Compute centrality for smarter ranking
    centrality = nx.eigenvector_centrality(G, max_iter=500, weight='weight')
    ranked_terms = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

    return ranked_terms, G, all_terms

def simulate_gating(ranked_terms, G, context_mode='Evergreen', serper_key=None, query=""):
    """Context-aware gating with velocity boost in QDF"""
    weights = {term: centrality for term, centrality in ranked_terms}

    if context_mode == 'QDF' and serper_key and query:
        try:
            payload = {"q": f"{query} site:youtube.com"}
            headers = {"X-API-KEY": serper_key, "Content-Type": "application/json"}
            resp = requests.post("https://google.serper.dev/search", json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                results = resp.json().get('organic', [])[:10]
                trending_text = " ".join([r['title'] + " " + r['snippet'] for r in results]).lower()
                trending_terms = re.findall(r'\w+', trending_text)
                trending_counter = Counter(trending_terms)
                for term in weights:
                    lower_term = term.lower()
                    if lower_term in trending_counter:
                        boost = 1 + (trending_counter[lower_term] / 5) * 2  # Velocity scaling
                        weights[term] *= boost
        except:
            pass  # Silent fallback

    # Normalize weights
    max_w = max(weights.values()) if weights else 1
    for term in weights:
        weights[term] /= max_w

    return weights

def generate_seo_report(ranked_terms, G, gated_weights):
    """Generate full SEO Beast dashboard report + CSV-ready data"""
    report = "=== SEO Beast Dashboard (AlgoDev Military-Grade) ===\n\n"

    report += "**Top Ranked Terms (Centrality + Gating):**\n"
    sorted_gated = sorted(gated_weights.items(), key=lambda x: x[1], reverse=True)[:15]
    for term, weight in sorted_gated:
        report += f"- {term}: {weight:.3f}\n"

    report += "\n**Key DFIL Interactions (Top 10):**\n"
    edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)[:10]
    for a, b, data in edges:
        report += f"{a} ↔ {b} (strength: {data['weight']:.3f})\n"

    # CSV-ready data
    csv_data = pd.DataFrame({
        'Keyword': [t for t, w in sorted_gated],
        'Gated_Weight': [w for t, w in sorted_gated],
        'Centrality': [next((c for term, c in ranked_terms if term == t), 0) for t, w in sorted_gated]
    })

    return report, csv_data
