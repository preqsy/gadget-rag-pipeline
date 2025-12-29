from __future__ import annotations
from typing import List

from llama_index.embeddings.huggingface import HuggingFaceEmbedding


class LlamaIndexHFEmbedder:
    def __init__(self, model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = model
        self.embed_model = HuggingFaceEmbedding(model_name=self.model)

    def embed(self, text: str) -> List[float]:
        return self.embed_model.get_text_embedding(text)


hug = LlamaIndexHFEmbedder()

# embedded = hug.embed("Hello")

# print(f"Embedded values: {embedded}")
