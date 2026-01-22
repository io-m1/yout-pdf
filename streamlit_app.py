# streamlit_app.py - SEO Beast w/ Interactive DFIL Graph
import streamlit as st
import io
import pandas as pd
from algodev import simulate_dfil, simulate_gating, generate_seo_report
from pyvis.network import Network

st.set_page_config(page_title="SEO Beast + DFIL Graph", layout="wide")
st.title("🚀 Military-Grade SEO Beast + Interactive Graph")

uploaded_file = st.file_uploader("Upload PDF/DOC for analysis", type=["pdf","docx"])
text_input = st.text_area("Or paste text content here", height=200)
context_mode = st.selectbox("Gating Context", ["Evergreen","QDF/Trending","Mobile/Short-Form"])

if st.button("Run SEO Beast"):
    full_text = ""
    if uploaded_file:
        import pypdf2
        from docx import Document
        if uploaded_file.type=="application/pdf":
            reader = pypdf2.PdfReader(uploaded_file)
            full_text = "".join([p.extract_text() or "" for p in reader.pages])
        elif uploaded_file.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(uploaded_file)
            full_text = "\n".join([p.text for p in doc.paragraphs])
    full_text += "\n"+text_input

    ranked_terms, G, all_terms, net = simulate_dfil(full_text)
    gated_weights = simulate_gating(ranked_terms, G, context_mode)

    report, csv_data = generate_seo_report(ranked_terms, G, gated_weights)
    st.text_area("SEO Beast Report", report, height=400)

    csv_buffer = io.StringIO()
    csv_data.to_csv(csv_buffer, index=False)
    st.download_button("📥 Download Keywords CSV", csv_buffer.getvalue(), "seo_keywords.csv", "text/csv")

    # Render interactive graph
    st.markdown("### DFIL Semantic Co-occurrence Graph")
    net.save_graph("dfil_graph.html")
    with open("dfil_graph.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=650, scrolling=True)
