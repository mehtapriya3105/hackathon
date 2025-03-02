import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import requests

def fetch_pubmed_articles(query, retmax=5):
    """Fetch top PubMed articles related to the query."""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": retmax}
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    ids = data.get("esearchresult", {}).get("idlist", [])
    abstracts = []
    
    for pub_id in ids:
        details_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        details_params = {"db": "pubmed", "id": pub_id, "retmode": "json"}
        details_response = requests.get(details_url, params=details_params).json()
        
        title = details_response["result"].get(pub_id, {}).get("title", "No Title")
        abstracts.append(f"{title} (PubMed ID: {pub_id})")
    
    return abstracts

model_name = "microsoft/biogpt"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def generate_medical_response(context, query):
    """Generate response using BioGPT given context from PubMed articles."""
    prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer:"
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        output = model.generate(**inputs, max_length=200)
    
    return tokenizer.decode(output[0], skip_special_tokens=True)


st.write("A chatbot that retrieves PubMed articles and generates responses using BioGPT.")

# User input for query
query = st.text_input("Enter a medical query (e.g., treatment for rare disease X):")

if query:
    with st.spinner("Fetching relevant PubMed articles..."):
        articles = fetch_pubmed_articles(query)
    
    if articles:
        st.subheader("Relevant Research Papers")
        for article in articles:
            st.write(f"- {article}")

        # Combine articles into context
        context = " ".join(articles)
        
        with st.spinner("Generating response..."):
            response = generate_medical_response(context, query)

        st.subheader("BioGPT Response")
        st.write(response)
    else:
        st.warning("No relevant articles found. Try a different query.")
