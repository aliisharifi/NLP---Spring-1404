import gradio as gr
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel, AutoConfig
from datasets import load_dataset
import faiss
import numpy as np
from huggingface_hub import hf_hub_download
from tqdm import tqdm
import re

model_name = "alisharifi/glot500-fa-dapt-contrastive" # This should be the name you pushed the model to
tokenizer = AutoTokenizer.from_pretrained(model_name)
base_encoder = AutoModel.from_pretrained(model_name)

class ProjectionHead(nn.Module):
    def __init__(self, hidden_size, proj_size=256):
        super().__init__()
        self.proj = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, proj_size),
        )
    def forward(self, x):
        return self.proj(x)

proj_head_path = hf_hub_download(repo_id="alisharifi/glot500-fa-dapt-contrastive-proj", filename="proj_head.pt")

config = AutoConfig.from_pretrained(model_name)
proj_head = ProjectionHead(config.hidden_size, proj_size=256)
proj_head.load_state_dict(torch.load(proj_head_path, map_location=torch.device('cpu'))) # Load on CPU first

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
base_encoder.to(device)
proj_head.to(device)

dataset = load_dataset("alisharifi/aggregate-fa-qa")
corpus = dataset['train']['context']

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text


def create_embeddings(texts, model, proj_head, tokenizer, device, batch_size=64, max_len=128):
    model.eval()
    proj_head.eval()
    all_embeddings = []
    with torch.no_grad():
        for i in tqdm(range(0, len(texts), batch_size), desc="Creating Embeddings"):
            batch_texts = texts[i:i + batch_size]
            encoded_input = tokenizer(batch_texts, padding='max_length', truncation=True, max_length=max_len, return_tensors='pt').to(device)
            with torch.no_grad():
                model_output = model(**encoded_input)
            sentence_embeddings = model_output.last_hidden_state.mean(dim=1)
            projected_embeddings = proj_head(sentence_embeddings)
            all_embeddings.append(F.normalize(projected_embeddings, dim=1).cpu())
    return torch.cat(all_embeddings, dim=0).numpy()

unique_corpus_texts = list(dict.fromkeys(normalize_text(text) for text in corpus))
corpus_embeddings = create_embeddings(unique_corpus_texts, base_encoder, proj_head, tokenizer, device)

index = faiss.IndexFlatL2(corpus_embeddings.shape[1])
index.add(corpus_embeddings)

def search_documents(query, k=10):
    base_encoder.eval()
    proj_head.eval()
    with torch.no_grad():
        encoded_input = tokenizer(query, padding='max_length', truncation=True, max_length=128, return_tensors='pt').to(device)
        model_output = base_encoder(**encoded_input)
        sentence_embedding = model_output.last_hidden_state.mean(dim=1)
        projected_embedding = proj_head(sentence_embedding)
        query_embedding = F.normalize(projected_embedding, dim=1).cpu().numpy()

    D, I = index.search(query_embedding, k)

    results = []
    for i in range(k):
        unique_doc_index = int(I[0][i])
        results.append(f"Document {unique_doc_index}: {unique_corpus_texts[unique_doc_index]}")

    return "\n\n".join(results)

iface = gr.Interface(
    fn=search_documents,
    inputs=gr.Textbox(label="Enter your query"),
    outputs=gr.Textbox(label="Most relevant documents"),
    title="Document Search with Trained Model",
    description="Enter a query to find the most relevant documents from the uploaded dataset."
)

iface.launch(debug=True)

