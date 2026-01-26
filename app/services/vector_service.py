import faiss
import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer

class VectorService:
    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []
        self.load_index()

    def ingest_text(self, full_text):
        """
        Splits text into larger chunks to ensure context is preserved.
        """
        print(f"🧠 Vectorizing {len(full_text)} characters...")
        
        # --- CRITICAL UPGRADE FOR QWEN 2.5 ---
        # 1. Chunk Size 1000: Ensures we capture full degree requirements in one block.
        # 2. Overlap 500: Ensures the "Header" and "List" appear together.
        chunk_size = 1000   
        overlap = 500       
        
        self.chunks = []
        for i in range(0, len(full_text), chunk_size - overlap):
            chunk = full_text[i:i + chunk_size]
            # Only keep chunks that have meaningful content (>50 chars)
            if len(chunk) > 50: 
                self.chunks.append(chunk)
        
        print(f"🧩 Created {len(self.chunks)} chunks.")

        if self.chunks:
            embeddings = self.embedder.encode(self.chunks)
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(np.array(embeddings).astype('float32'))
            self.save_index()
            return f"Success: Indexed {len(self.chunks)} chunks."
        return "Warning: No text found to chunk."

    def search(self, query, top_k=5):
        """
        Searches the Vector DB.
        """
        if self.index.ntotal == 0: return ""
        
        query_vector = self.embedder.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), top_k)
        
        results = []
        for i in indices[0]:
            if i < len(self.chunks):
                results.append(self.chunks[i])
        
        return "\n\n".join(results)

    def save_index(self):
        faiss.write_index(self.index, "vector_store.index")
        with open("chunks.pkl", "wb") as f:
            pickle.dump(self.chunks, f)

    def load_index(self):
        if os.path.exists("vector_store.index") and os.path.exists("chunks.pkl"):
            self.index = faiss.read_index("vector_store.index")
            with open("chunks.pkl", "rb") as f:
                self.chunks = pickle.load(f)