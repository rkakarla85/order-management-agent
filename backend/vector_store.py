import chromadb
import uuid
import json

class VectorStoreManager:
    def __init__(self, persistence_path="./chroma_db"):
        self.client = chromadb.PersistentClient(path=persistence_path)
        # Get or create collection
        self.collection = self.client.get_or_create_collection(name="inventory")

    def index_inventory(self, business_id, items):
        """
        Re-indexes the inventory for a specific business.
        1. Deletes existing items for this business_id.
        2. Adds new items with metadata.
        """
        print(f"Indexing {len(items)} items for business: {business_id}")
        
        # 1. Delete existing
        try:
            self.collection.delete(where={"business_id": business_id})
        except Exception:
            pass # Collection might be empty or business not found, which is fine

        if not items:
            return

        documents = []
        metadatas = []
        ids = []

        for item in items:
            # Create a rich text representation for embedding dynamically
            # This handles different schemas (e.g. 'Item Name' vs 'Dish Name')
            doc_parts = []
            
            # Priority fields to ensure they appear first (optional, but good for some models)
            priority_keys = ['Item Name', 'Dish Name', 'item', 'name', 'Category', 'category']
            
            for key in priority_keys:
                if key in item and item[key]:
                    doc_parts.append(f"{key}: {item[key]}")
            
            # Add remaining fields
            for k, v in item.items():
                if k not in priority_keys and v:
                     doc_parts.append(f"{k}: {v}")
            
            doc_text = ". ".join(doc_parts)
            
            # Metadata for filtering and retrieval
            meta = {
                "business_id": business_id,
                "json_data": json.dumps(item) # Store full item data to return on search
            }
            
            documents.append(doc_text)
            metadatas.append(meta)
            ids.append(f"{business_id}_{uuid.uuid4()}")

        # 2. Add new items
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Index complete. Added {len(ids)} vectors.")

    def search(self, query, business_id, limit=5):
        """
        Semantic search for items belonging to business_id.
        """
        print(f"DEBUG: Doing vector search for '{query}' in business '{business_id}'")
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where={"business_id": business_id}
        )
        print(f"DEBUG: Raw Vector Results: {len(results['ids'][0])} matches.")
        
        # Parse results back to list of item dicts
        items = []
        if results['metadatas']:
            for meta in results['metadatas'][0]:
                if meta and 'json_data' in meta:
                    items.append(json.loads(meta['json_data']))
        
        return items
