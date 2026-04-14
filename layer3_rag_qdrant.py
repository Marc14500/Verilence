import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class RAGEngineQdrant:
    def __init__(self, collection_name="verilence_chunks", host="localhost", port=6333):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.vector_size = 3072  # Gemini embedding-2-preview size
    
    def create_collection(self, vector_size=3072):
        """Create Qdrant collection for storing chunk embeddings"""
        self.vector_size = vector_size
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print(f"[L3-RAG] ✓ Created Qdrant collection: {self.collection_name}")
    
    def index_chunks(self, embedded_chunks):
        """Index embedded chunks into Qdrant"""
        if not embedded_chunks:
            print("[L3-RAG] No chunks to index")
            return
        
        points = []
        for idx, chunk in enumerate(embedded_chunks):
            point_id = idx + 1
            points.append(
                PointStruct(
                    id=point_id,
                    vector=chunk['embedding'],
                    payload={
                        'chunk_id': chunk['id'],
                        'text': chunk['text'][:1000],
                        'source': chunk['source'],
                        'chunk_index': chunk['chunk_index'],
                        'metadata': chunk['metadata']
                    }
                )
            )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        print(f"[L3-RAG] ✓ Indexed {len(points)} chunks into Qdrant")
    
    def search(self, query_embedding, top_k=5):
        """Search for similar chunks"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
        )
        
        return [
            {
                'text': hit.payload['text'],
                'source': hit.payload['source'],
                'score': hit.score,
                'metadata': hit.payload['metadata']
            }
            for hit in results
        ]
    
    def search_chunks(self, query_text, query_embedding, top_k=5):
        """Search for chunks relevant to query"""
        results = self.search(query_embedding, top_k=top_k)
        print(f"[L3-RAG] ✓ Found {len(results)} relevant chunks for query")
        return results
