import os
from typing import Any

from django.conf import settings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from agents.llm import get_embeddings

class InsightStore:
    def __init__(self) -> None:
        self.embeddings = get_embeddings()
        self.store = None
        
    def add_insight(self, text: str, metadata: dict[str, Any] = None) -> None:
        doc = Document(page_content=text, metadata=metadata or {})
        if self.store is None:
            self.store = FAISS.from_documents([doc], self.embeddings)
        else:
            self.store.add_documents([doc])
            
    def search_similar(self, query: str, k: int = 5) -> list[Document]:
        if self.store is None:
            return []
        return self.store.similarity_search(query, k=k)
        
    def save(self) -> None:
        if self.store:
            os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)
            self.store.save_local(settings.FAISS_INDEX_DIR)
            
    def load(self) -> None:
        if os.path.exists(settings.FAISS_INDEX_DIR):
            self.store = FAISS.load_local(
                settings.FAISS_INDEX_DIR, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
