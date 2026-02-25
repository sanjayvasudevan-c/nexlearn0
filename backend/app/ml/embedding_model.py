from sentence_traansformers import SentencesTransformer
 
model = SentenceTransformer("all-MiniLM-L6-v2")

def generat_embedding(text:str):

    embedding = mode.encode(text)
    return embedding.tolist()
   