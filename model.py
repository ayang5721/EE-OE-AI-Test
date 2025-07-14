import openai
import os
import numpy as np
import faiss

# Using a placeholder API key for demonstration purposes only
openai.api_key = "sk-PLACEHOLDER1234567890abcdefg"

# Load and chunk long documents from the 'documents' folder
def load_and_chunk_documents(folder_path, max_words=300):
    all_chunks = []

    def chunk_text(text, max_words):
        words = text.split()
        return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as file:
                text = file.read()
                chunks = chunk_text(text, max_words)
                all_chunks.extend(chunks)

    return all_chunks

# Load and chunk documents
documents = load_and_chunk_documents("documents")

# Generate embeddings for the documents
def get_embedding(text):
    return openai.Embedding.create(input=[text], model="text-embedding-3-small")['data'][0]['embedding']

# Build FAISS index
embedding_dim = 1536  # dimension for text-embedding-3-small
index = faiss.IndexFlatL2(embedding_dim)
doc_embeddings = np.array([get_embedding(doc) for doc in documents]).astype('float32')
index.add(doc_embeddings)

user_input = input("Enter your question: ")

# Embed the user query
query_embedding = np.array(get_embedding(user_input)).astype('float32').reshape(1, -1)

# Retrieve all documents and their distances
distances, indices = index.search(query_embedding, len(documents))

# Weight and include all relevant documents
weighted_docs = [(documents[i], distances[0][j]) for j, i in enumerate(indices[0])]

# Sort by relevance (lowest distance means most relevant)
sorted_retrieved = sorted(weighted_docs, key=lambda x: x[1])

# Only include the best doc and others within 0.2 of its distance
context_chunks = []
if sorted_retrieved:
    best_distance = sorted_retrieved[0][1]
    threshold = best_distance + 0.2
    for doc, dist in sorted_retrieved:
        if dist <= threshold:
            context_chunks.append(f"[{round(dist, 2)}] {doc}")
        if len(context_chunks) >= 10 and dist > best_distance + 0.1:
            break

context = "\n".join(context_chunks) if context_chunks else "No relevant context found."

openai_request = {
  "model": "gpt-4.1",
  "messages": [
    {"role": "system", "content": f"You are a helpful assistant. Use the following weighted context to explain and apply concepts relevant to the user's question. Relevance scores are shown in brackets (lower is better):\n{context}"},
    {"role": "user", "content": user_input}
  ],
  "temperature": 0.7,
  "max_tokens": 4096
}

# Actual API call
response = openai.ChatCompletion.create(
  model='gpt-4.1',
  messages=openai_request["messages"],
  temperature=openai_request["temperature"],
  max_tokens=openai_request["max_tokens"]
)

print("\nContext Used:\n", context)
print("\nAssistant:\n", response["choices"][0]["message"]["content"])
