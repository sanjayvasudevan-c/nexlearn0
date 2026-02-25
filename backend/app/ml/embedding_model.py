from sentence_transformers import SentenceTransformer

# Load model once when module loads
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text: str):
    embedding = model.encode(text)
    return embedding.tolist()