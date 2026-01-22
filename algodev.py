# algodev.py - Military-grade AlgoDev + Interactive Graph (Null-Safe)
import networkx as nx
from collections import Counter
import re
from spacy import load as spacy_load
from sentence_transformers import SentenceTransformer, util
from io import StringIO
import pandas as pd
from pyvis.network import Network

nlp = spacy_load("en_core_web_sm")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def chunk_text(text, max_chars=8000):
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
    return chunks if chunks else [""]  # at least one empty chunk

def simulate_dfil(full_text):
    if not full_text.strip():
        return [], nx.Graph(), [], None, "No content provided for analysis."

    chunks = chunk_text(full_text)
    all_entities, all_topics = [], []

    for chunk in chunks:
        if not chunk.strip():
            continue
        doc = nlp(chunk)
        entities = [ent.text for ent in doc.ents if ent.label_ in ['PERSON','ORG','GPE','EVENT','WORK_OF_ART']]
        topics = [token.lemma_ for token in doc if token.pos_ in ['NOUN','PROPN'] and not token.is_stop and len(token.text) > 3]
        all_entities.extend(entities)
        all_topics.extend(topics)

    entity_counter = Counter(all_entities)
    topic_counter = Counter(all_topics)
    top_entities = [e for e,c in entity_counter.most_common(15)]
    top_topics = [t for t,c in topic_counter.most_common(30)]
    all_terms = list(set(top_entities + top_topics))

    if not all_terms:
        return [], nx.Graph(), [], None, "No meaningful entities or topics could be extracted."

    embeddings = embedder.encode(all_terms)
    G = nx.Graph()

    for i in range(len(all_terms)):
        for j in range(i+1, len(all_terms)):
            sim = util.cos_sim(embeddings[i], embeddings[j]).item()
            if sim > 0.45:
                G.add_edge(all_terms[i], all_terms[j], weight=sim)

    # Safe centrality only if graph has nodes
    centrality = {}
    if len(G.nodes) > 0:
        try:
            centrality = nx.eigenvector_centrality(G, max_iter=500, weight='weight')
        except nx.NetworkXPointlessConcept:
            centrality = {node: 0.0 for node in G.nodes}
    else:
        centrality = {}

    ranked_terms = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

    # Interactive graph only if nodes exist
    net = None
    if len(G.nodes) > 0:
        net = Network(height="600px", width="100%", notebook=False, bgcolor="#0d1117", font_color="#c9d1d9")
        for node, cent in ranked_terms:
            net.add_node(node, label=node, size=max(cent*80, 10), title=f"Centrality: {cent:.3f}")
        for a,b,data in G.edges(data=True):
            net.add_edge(a, b, value=data['weight']*5, title=f"Similarity: {data['weight']:.3f}")
        net.repulsion(node_distance=150, central_gravity=0.1)

    msg = "" if ranked_terms else "Limited content — no strong interactions detected."
    return ranked_terms, G, all_terms, net, msg

def simulate_gating(ranked_terms, G, context_mode='Evergreen', serper_key=None, query=""):
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
                        boost = 1 + (trending_counter[lower_term]/5)*2
                        weights[term] *= boost
        except:
            pass
    max_w = max(weights.values()) if weights else 1
    for term in weights: weights[term] /= max_w
    return weights

def generate_seo_report(ranked_terms, G, gated_weights, extra_msg=""):
    report = "=== SEO Beast Dashboard (AlgoDev Military-Grade) ===\n\n"
    if extra_msg:
        report += f"Note: {extra_msg}\n\n"
    sorted_gated = sorted(gated_weights.items(), key=lambda x: x[1], reverse=True)[:15]
    if sorted_gated:
        report += "**Top Ranked Terms (Centrality + Gating):**\n"
        for term, weight in sorted_gated:
            report += f"- {term}: {weight:.3f}\n"
    else:
        report += "**No ranked terms detected.**\n"
    report += "\n**Key DFIL Interactions (Top 10):**\n"
    edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)[:10]
    if edges:
        for a,b,data in edges:
            report += f"{a} ↔ {b} (strength: {data['weight']:.3f})\n"
    else:
        report += "No interactions detected.\n"
    csv_data = pd.DataFrame({
        'Keyword':[t for t,_ in sorted_gated],
        'Gated_Weight':[w for _,w in sorted_gated],
        'Centrality':[next((c for term,c in ranked_terms if term==t),0) for t,_ in sorted_gated]
    })
    return report, csv_data
