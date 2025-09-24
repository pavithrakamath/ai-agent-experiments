import os
import pickle
from typing import List, Any

import faiss
import numpy as np

from ai_agent_experiments.config import Configuration


class PersistentFaissStore:
    def __init__(self, config: Configuration):
        self.save_path = config.faiss_server_config["path"]
        self.embedding_dim = config.faiss_server_config["dimension"]  # OpenAI ada-002
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.chunks = []
        self.metadata = []
        os.makedirs(self.save_path, exist_ok=True)
        self.load(config)

    def load(self, config: Configuration):
        index_path = os.path.join(self.save_path, "embeddings.index")
        data_path = os.path.join(self.save_path, "data.pkl")
        if os.path.exists(index_path) and os.path.exists(data_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(data_path, "rb") as f:
                    self.chunks, self.metadata, self.embedding_dim = pickle.load(f)
                    print("Loaded embeddings from disk.")
            except Exception as e:
                print(f"Error loading embeddings from disk: {e}")
                self.__init__(config)

    def save(self):
        index_path = os.path.join(self.save_path, "embeddings.index")
        data_path = os.path.join(self.save_path, "data.pkl")
        faiss.write_index(self.index, index_path)
        with open(data_path, "wb") as f:
            pickle.dump((self.chunks, self.metadata, self.embedding_dim), f)
            print("Saved embeddings to disk.")

    def add_embeddings(self, embeddings, chunks, metadata=None):
        embedding_vector = np.array([item.embedding for item in embeddings.data]).astype("float32")
        faiss.normalize_L2(embedding_vector)
        self.index.add(embedding_vector)
        self.chunks.extend(chunks)
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{"index": i} for i in range(len(chunks))])

        self.save()
        print(f"Added embeddings to index. Total embeddings: {len(self.chunks)}")

    def search(self, query_embeddings, top_k=3) -> List[Any]:
        if len(self.chunks) == 0:
            return []

        query_embedding_vector = np.array([query_embeddings.embedding]).astype("float32")
        faiss.normalize_L2(query_embedding_vector)
        similarities, indices = self.index.search(query_embedding_vector, top_k)
        results = []
        for i in range(top_k):
            results.append(
                {
                    "index": indices[0][i],
                    "score": similarities[0][i],
                    "chunk": self.chunks[indices[0][i]],
                    "metadata": self.metadata[indices[0][i]],
                }
            )
        return results
