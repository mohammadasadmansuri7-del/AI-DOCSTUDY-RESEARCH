import os
import uuid
import re
import math
import hashlib
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.config import settings

class VectorStoreManager:
    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION
        self.dim = 384  # Dimension for all-MiniLM-L6-v2 / hashed TF-IDF
        
        # Initialize Qdrant Client
        if settings.QDRANT_URL and settings.QDRANT_URL.strip():
            self.client = QdrantClient(
                url=settings.QDRANT_URL.strip(),
                api_key=settings.QDRANT_API_KEY.strip() if settings.QDRANT_API_KEY else None
            )
        else:
            local_qdrant_path = os.path.join(os.getcwd(), "qdrant_db")
            os.makedirs(local_qdrant_path, exist_ok=True)
            try:
                self.client = QdrantClient(path=local_qdrant_path)
            except Exception as e:
                print(f"[VectorStore] Local path lock fallback to memory: {e}")
                self.client = QdrantClient(":memory:")

        self.encoder = None
        self._init_encoder()
        self._ensure_collection()

    def _init_encoder(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
            print("[VectorStore] SentenceTransformer 'all-MiniLM-L6-v2' successfully loaded.")
        except Exception as e:
            print(f"[VectorStore] SentenceTransformer init fallback: {e}")
            self.encoder = None

    def embed_text(self, text: str) -> List[float]:
        if self.encoder is not None:
            try:
                vector = self.encoder.encode(text).tolist()
                return vector
            except Exception as e:
                print(f"[VectorStore] Encoder exception fallback: {e}")

        # High-precision Term Hashing Vectorizer (384 dimensions)
        vec = [0.0] * self.dim
        tokens = re.findall(r'\w+', text.lower())
        if not tokens:
            return vec

        ngrams = tokens + [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens)-1)]
        
        for token in ngrams:
            idx = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % self.dim
            vec[idx] += 1.0

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]

        return vec

    def _ensure_collection(self):
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=self.dim,
                        distance=qmodels.Distance.COSINE
                    )
                )
            # Ensure keyword index on document_id for filtering
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="document_id",
                    field_schema=qmodels.PayloadSchemaType.KEYWORD
                )
            except Exception as pe:
                pass
        except Exception as e:
            print(f"[VectorStore] Collection check error: {e}")

    def upsert_chunks(self, document_id: str, filename: str, chunks_data: List[Dict[str, Any]]):
        points = []
        for item in chunks_data:
            chunk_id = item["chunk_id"]
            page_number = item["page_number"]
            content = item["content"]
            
            vector = self.embed_text(content)
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{document_id}_{chunk_id}"))
            
            payload = {
                "document_id": document_id,
                "filename": filename,
                "page_number": page_number,
                "chunk_id": chunk_id,
                "content": content
            }
            
            points.append(
                qmodels.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )
            
        if points:
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )

    def search_relevant_chunks(
        self,
        query: str,
        document_ids: List[str],
        top_k: int = 6,
        score_threshold: float = 0.05
    ) -> List[Dict[str, Any]]:
        query_vector = self.embed_text(query)
        
        query_filter = None
        if document_ids:
            query_filter = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="document_id",
                        match=qmodels.MatchAny(any=document_ids)
                    )
                ]
            )
            
        try:
            hits = []
            if hasattr(self.client, "query_points"):
                res = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    query_filter=query_filter,
                    limit=top_k,
                    score_threshold=score_threshold
                )
                hits = res.points
            elif hasattr(self.client, "search"):
                hits = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    query_filter=query_filter,
                    limit=top_k,
                    score_threshold=score_threshold
                )
            
            results = []
            for hit in hits:
                results.append({
                    "score": hit.score,
                    "document_id": hit.payload.get("document_id"),
                    "filename": hit.payload.get("filename"),
                    "page_number": hit.payload.get("page_number"),
                    "chunk_id": hit.payload.get("chunk_id"),
                    "content": hit.payload.get("content")
                })
            return results
        except Exception as e:
            print(f"[VectorStore] Search error: {e}")
            return []

    def delete_document_chunks(self, document_id: str):
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=qmodels.FilterSelector(
                    filter=qmodels.Filter(
                        must=[
                            qmodels.FieldCondition(
                                key="document_id",
                                match=qmodels.MatchValue(value=document_id)
                            )
                        ]
                    )
                )
            )
        except Exception as e:
            print(f"[VectorStore] Delete error for doc {document_id}: {e}")

# Global vector store instance
vector_store = VectorStoreManager()
