from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import hashlib
import os
import chromadb
from chromadb.config import Settings
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def parse_basic_needs_from_json(needs_json_str):
    """Parse BasicNeeds from JSON string stored in metadata"""
    if not needs_json_str:
        return None
    
    try:
        needs_data = json.loads(needs_json_str)
        return needs_data
    except (json.JSONDecodeError, TypeError):
        print(f"Error parsing BasicNeeds JSON: {needs_json_str}")
        return None

@dataclass
class ConversationMemory:
    """Represents a conversation memory entry"""
    person_name: str
    message_content: str
    message_type: str  # "user_message", "jenbina_response", "context"
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding_id: Optional[str] = None

class ChromaMemoryManager:
    def __init__(self, embeddings_model: str = "llama3.2:3b-instruct-fp16"):
        """
        Initialize Chroma-based memory manager
        
        Args:
            embeddings_model: Ollama model to use for embeddings
        """
        self.embeddings = OllamaEmbeddings(model=embeddings_model)
        self.vector_store_path = "./jenbina_memory"
        self.client = None
        self.collection = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize or load the Chroma vector store"""
        # Try persistent client first
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.vector_store_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection("jenbina_conversations")
                print(f"Loaded existing collection from {self.vector_store_path}")
                return  # Success, exit early
            except Exception as collection_error:
                error_msg = str(collection_error).lower()
                if "already exists" in error_msg:
                    # Collection exists but there was an issue getting it, try to get it again
                    try:
                        self.collection = self.client.get_collection("jenbina_conversations")
                        print(f"Retrieved existing collection from {self.vector_store_path}")
                        return  # Success, exit early
                    except Exception as retry_error:
                        print(f"Failed to retrieve existing collection: {retry_error}")
                        # If we still can't get it, try to delete and recreate
                        try:
                            self.client.delete_collection("jenbina_conversations")
                            self.collection = self.client.create_collection("jenbina_conversations")
                            print(f"Recreated collection at {self.vector_store_path}")
                            return  # Success, exit early
                        except Exception as recreate_error:
                            print(f"Failed to recreate collection: {recreate_error}")
                            # Continue to fallback
                elif "not found" in error_msg or "does not exist" in error_msg:
                    # Collection doesn't exist, create it
                    try:
                        self.collection = self.client.create_collection("jenbina_conversations")
                        print(f"Created new collection at {self.vector_store_path}")
                        return  # Success, exit early
                    except Exception as create_error:
                        print(f"Failed to create collection: {create_error}")
                        # Continue to fallback
                else:
                    print(f"Unknown collection error: {collection_error}")
                    # Continue to fallback
                
        except Exception as e:
            print(f"Error initializing persistent vector store: {e}")
            # Continue to fallback
        
        # Fallback to in-memory client
        print("Falling back to in-memory ChromaDB client...")
        try:
            self.client = chromadb.Client()
            # Try to get existing collection first
            try:
                self.collection = self.client.get_collection("jenbina_conversations")
                print("Using existing in-memory collection")
            except:
                self.collection = self.client.create_collection("jenbina_conversations")
                print("Created new in-memory collection")
        except Exception as fallback_error:
            print(f"In-memory fallback failed: {fallback_error}")
            # Last resort: create a new client and collection
            try:
                self.client = chromadb.Client()
                self.collection = self.client.create_collection("jenbina_conversations")
                print("Created new fallback collection")
            except Exception as final_error:
                print(f"Final fallback failed: {final_error}")
                raise final_error
    
    def _generate_embedding_id(self, person_name: str, content: str, timestamp: datetime) -> str:
        """Generate a unique ID for the embedding"""
        unique_string = f"{person_name}_{content}_{timestamp.isoformat()}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def store_conversation(self, person_name: str, message_content: str, 
                          message_type: str, sender_name: str = None, 
                          receiver_name: str = None, metadata: Dict[str, Any] = None) -> str:
        """
        Store a conversation message in Chroma
        
        Args:
            person_name: Name of the person
            message_content: Content of the message
            message_type: Type of message (user_message, jenbina_response, etc.)
            sender_name: Name of the sender (defaults to person_name if None)
            receiver_name: Name of the receiver (defaults to "Jenbina" if None)
            metadata: Additional metadata
            
        Returns:
            embedding_id: Unique ID of the stored embedding
        """
        try:
            timestamp = datetime.now()
            embedding_id = self._generate_embedding_id(person_name, message_content, timestamp)
            
            # Generate embedding
            embedding = self.embeddings.embed_query(message_content)
            
            # Set default sender and receiver names
            if sender_name is None:
                sender_name = person_name
            if receiver_name is None:
                receiver_name = "Jenbina"
            
            # Validate that sender_name is not None
            if not sender_name:
                raise ValueError("Sender name is required")
            
            # DEBUG: Print the exact parameters being used
            print(f"🔍 STORE DEBUG: person_name='{person_name}', sender='{sender_name}', receiver='{receiver_name}', message_type='{message_type}', content='{message_content[:30]}...'")
            
            # Prepare metadata - ensure all values are serializable
            doc_metadata = {
                "sender_name": sender_name,
                "receiver_name": receiver_name,
                "message_type": message_type,
                "timestamp": timestamp.isoformat(),
                "embedding_id": embedding_id,
            }
            
            # Add metadata with type checking
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        doc_metadata[key] = value
                    else:
                        # Convert complex objects to strings
                        doc_metadata[key] = str(value)[:500]  # Truncate if too long
            
            # DEBUG: Print the final metadata being stored
            print(f"🔍 STORE DEBUG: Final doc_metadata['sender_name']='{doc_metadata['sender_name']}'")
            
            # Add to Chroma collection
            self.collection.add(
                embeddings=[embedding],
                documents=[message_content],
                metadatas=[doc_metadata],
                ids=[embedding_id]
            )
            
            print(f"Stored conversation for {person_name}: {message_content[:50]}...")
            return embedding_id
            
        except Exception as e:
            print(f"Error storing conversation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def debug_collection_contents(self, person_name: str = None):
        """Debug method to inspect what's actually in the collection"""
        try:
            print(f"🔍 DEBUG: Inspecting collection contents...")
            
            # Get all documents without any filter first
            all_results = self.collection.get()
            print(f"🔍 DEBUG: Total documents in collection: {len(all_results['documents'])}")
            
            # Show all documents
            for i, (doc, metadata) in enumerate(zip(all_results['documents'], all_results['metadatas'])):
                sender = metadata.get('sender_name', 'Unknown') if metadata else 'Unknown'
                receiver = metadata.get('receiver_name', 'Unknown') if metadata else 'Unknown'
                msg_type = metadata.get('message_type', 'Unknown') if metadata else 'Unknown'
                timestamp = metadata.get('timestamp', 'Unknown') if metadata else 'Unknown'
                print(f"🔍 DEBUG: Doc {i}: Sender={sender}->Receiver={receiver}, Type={msg_type}, Time={timestamp}, Content={doc[:50]}...")
            
            # If person_name specified, show filtered results
            if person_name:
                # Filter by sender_name or receiver_name containing the person_name
                filtered_results = self.collection.get(
                    where={
                        "$or": [
                            {"sender_name": person_name},
                            {"receiver_name": person_name}
                        ]
                    }
                )
                print(f"🔍 DEBUG: Documents involving {person_name}: {len(filtered_results['documents'])}")
                for i, (doc, metadata) in enumerate(zip(filtered_results['documents'], filtered_results['metadatas'])):
                    sender = metadata.get('sender_name', 'Unknown') if metadata else 'Unknown'
                    receiver = metadata.get('receiver_name', 'Unknown') if metadata else 'Unknown'
                    msg_type = metadata.get('message_type', 'Unknown') if metadata else 'Unknown'
                    timestamp = metadata.get('timestamp', 'Unknown') if metadata else 'Unknown'
                    print(f"🔍 DEBUG: Filtered Doc {i}: Sender={sender}->Receiver={receiver}, Type={msg_type}, Time={timestamp}, Content={doc[:50]}...")
                    
        except Exception as e:
            print(f"Error debugging collection: {e}")
            import traceback
            traceback.print_exc()

    def retrieve_relevant_context(self, person_name: str, current_message: str, 
                                top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve recent conversation context for a person (all recent messages)
        
        Args:
            person_name: Name of the person
            current_message: Current message (not used for retrieval, just for compatibility)
            top_k: Number of recent documents to retrieve
            
        Returns:
            List of recent context documents with parsed BasicNeeds
        """
        try:
            # Debug: First let's see what's in the collection
            self.debug_collection_contents(person_name)
            
            # Get recent documents for this person (no semantic search, just chronological)
            # First, let's see how many documents exist for this person
            all_results = self.collection.get(
                where={
                    "$or": [
                        {"sender_name": person_name},
                        {"receiver_name": person_name}
                    ]
                }
            )
            print(f"🔍 Debug: Total documents involving {person_name}: {len(all_results['documents'])}")
            
            # Now get the recent ones with a higher limit
            results = self.collection.get(
                where={
                    "$or": [
                        {"sender_name": person_name},
                        {"receiver_name": person_name}
                    ]
                },
                limit=top_k * 5  # Increase limit to make sure we get enough
            )
            
            print(f"🔍 Debug: Found {len(results['documents'])} total documents for {person_name}")
            
            # Format and sort results by timestamp
            recent_context = []
            for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                if metadata:
                    print(f"🔍 Debug: Document {i}: {doc[:50]}... | Timestamp: {metadata.get('timestamp', 'N/A')}")
                    
                    # Parse BasicNeeds JSON if present
                    if "basic_needs_json" in metadata:
                        metadata["basic_needs"] = parse_basic_needs_from_json(metadata["basic_needs_json"])
                    
                    recent_context.append({
                        "content": doc,
                        "metadata": metadata,
                        "relevance_score": 1.0  # All recent messages are equally relevant
                    })
            
            print(f"🔍 Debug: Processed {len(recent_context)} documents")
            
            # Sort by timestamp (most recent first) and take top_k
            recent_context.sort(
                key=lambda x: x["metadata"]["timestamp"], 
                reverse=True
            )
            
            print(f"Retrieved {len(recent_context[:top_k])} recent contexts for {person_name}")
            return recent_context[:top_k]
            
        except Exception as e:
            print(f"Error retrieving context: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_person_conversation_history(self, person_name: str, 
                                      limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent conversation history for a specific person
        
        Args:
            person_name: Name of the person
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of conversation messages with parsed BasicNeeds
        """
        try:
            # Get all documents for this person (as sender or receiver)
            results = self.collection.get(
                where={
                    "$or": [
                        {"sender_name": person_name},
                        {"receiver_name": person_name}
                    ]
                },
                limit=limit
            )
            
            # Format and sort by timestamp
            person_history = []
            for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                # Parse BasicNeeds JSON if present
                if metadata and "basic_needs_json" in metadata:
                    metadata["basic_needs"] = parse_basic_needs_from_json(metadata["basic_needs_json"])
                
                person_history.append({
                    "content": doc,
                    "metadata": metadata
                })
            
            # Sort by timestamp (most recent first)
            person_history.sort(
                key=lambda x: x["metadata"]["timestamp"], 
                reverse=True
            )
            
            return person_history[:limit]
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    def get_conversation_between(self, sender_name: str, receiver_name: str, 
                               limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get conversation history between specific sender and receiver
        
        Args:
            sender_name: Name of the sender
            receiver_name: Name of the receiver
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of conversation messages between the specified parties
        """
        try:
            # Get documents where sender and receiver match
            # ChromaDB requires using $and operator for multiple conditions
            results = self.collection.get(
                where={
                    "$and": [
                        {"sender_name": sender_name},
                        {"receiver_name": receiver_name}
                    ]
                },
                limit=limit
            )
            
            # Also get reverse direction (receiver to sender)
            reverse_results = self.collection.get(
                where={
                    "$and": [
                        {"sender_name": receiver_name},
                        {"receiver_name": sender_name}
                    ]
                },
                limit=limit
            )
            
            # Combine and format results
            all_messages = []
            
            # Process forward direction
            for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                if metadata and "basic_needs_json" in metadata:
                    metadata["basic_needs"] = parse_basic_needs_from_json(metadata["basic_needs_json"])
                
                all_messages.append({
                    "content": doc,
                    "metadata": metadata,
                    "direction": "forward"
                })
            
            # Process reverse direction
            for i, (doc, metadata) in enumerate(zip(reverse_results['documents'], reverse_results['metadatas'])):
                if metadata and "basic_needs_json" in metadata:
                    metadata["basic_needs"] = parse_basic_needs_from_json(metadata["basic_needs_json"])
                
                all_messages.append({
                    "content": doc,
                    "metadata": metadata,
                    "direction": "reverse"
                })
            
            # Sort by timestamp (most recent first) and take limit
            all_messages.sort(
                key=lambda x: x["metadata"]["timestamp"], 
                reverse=True
            )
            
            return all_messages[:limit]
            
        except Exception as e:
            print(f"Error getting conversation between {sender_name} and {receiver_name}: {e}")
            return []
    
    def get_person_summary(self, person_name: str) -> Dict[str, Any]:
        """
        Get a summary of interactions with a specific person
        
        Args:
            person_name: Name of the person
            
        Returns:
            Summary dictionary
        """
        try:
            history = self.get_person_conversation_history(person_name, limit=50)
            
            if not history:
                return {
                    "person_name": person_name,
                    "total_interactions": 0,
                    "first_interaction": None,
                    "last_interaction": None,
                    "common_topics": [],
                    "interaction_patterns": {}
                }
            
            # Analyze interaction patterns
            message_types = [h["metadata"]["message_type"] for h in history]
            timestamps = [h["metadata"]["timestamp"] for h in history]
            
            # Extract common topics (simple keyword extraction)
            all_content = " ".join([h["content"] for h in history])
            common_words = self._extract_common_words(all_content)
            
            return {
                "person_name": person_name,
                "total_interactions": len(history),
                "first_interaction": min(timestamps) if timestamps else None,
                "last_interaction": max(timestamps) if timestamps else None,
                "common_topics": common_words[:10],
                "interaction_patterns": {
                    "user_messages": message_types.count("user_message"),
                    "jenbina_responses": message_types.count("jenbina_response"),
                    "context_entries": message_types.count("context")
                }
            }
            
        except Exception as e:
            print(f"Error getting person summary: {e}")
            return {"person_name": person_name, "error": str(e)}
    
    def _extract_common_words(self, text: str) -> List[str]:
        """Extract common words from text"""
        import re
        from collections import Counter
        
        # Remove punctuation and convert to lowercase
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 
            'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 
            'they', 'me', 'him', 'her', 'us', 'them', 'this', 'that', 'these', 
            'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count and return most common words
        word_counts = Counter(words)
        return [word for word, count in word_counts.most_common(20)]
    
    def search_similar_conversations(self, query: str, person_name: str = None, 
                                   top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar conversations
        
        Args:
            query: Search query
            person_name: Optional person name to filter by
            top_k: Number of results to return
            
        Returns:
            List of similar conversations
        """
        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)
            
            # Search
            if person_name:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where={"person_name": person_name}
                )
            else:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
            
            # Format results
            formatted_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            )):
                similarity_score = 1.0 / (1.0 + distance)
                formatted_results.append({
                    "content": doc,
                    "metadata": metadata,
                    "relevance_score": similarity_score
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching conversations: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory system
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            # Get collection count
            count = self.collection.count()
            
            if count == 0:
                return {
                    "total_conversations": 0,
                    "unique_people": 0,
                    "total_messages": 0,
                    "memory_size_mb": 0
                }
            
            # Get all documents to analyze
            all_results = self.collection.get(limit=count)
            
            # Count unique people (from both sender and receiver)
            unique_people = set()
            message_types = {}
            
            for metadata in all_results['metadatas']:
                if metadata:
                    sender_name = metadata.get("sender_name", "unknown")
                    receiver_name = metadata.get("receiver_name", "unknown")
                    unique_people.add(sender_name)
                    unique_people.add(receiver_name)
                    
                    message_type = metadata.get("message_type", "unknown")
                    message_types[message_type] = message_types.get(message_type, 0) + 1
            
            # Calculate memory size
            memory_size_mb = 0
            if os.path.exists(self.vector_store_path):
                for root, dirs, files in os.walk(self.vector_store_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        memory_size_mb += os.path.getsize(file_path) / (1024 * 1024)
            
            return {
                "total_conversations": count,
                "unique_people": len(unique_people),
                "total_messages": count,
                "message_types": message_types,
                "people": list(unique_people),
                "memory_size_mb": round(memory_size_mb, 2)
            }
            
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {"error": str(e)}
    
    def clear_memory(self, person_name: str = None):
        """
        Clear memory for a specific person or all memory
        
        Args:
            person_name: If provided, clear only this person's memory
        """
        try:
            if person_name:
                # Get all documents involving this person (as sender or receiver)
                results = self.collection.get(
                    where={
                        "$or": [
                            {"sender_name": person_name},
                            {"receiver_name": person_name}
                        ]
                    }
                )
                
                # Delete by IDs
                if results['ids']:
                    self.collection.delete(ids=results['ids'])
                    print(f"Cleared memory for {person_name}")
            else:
                # Clear all memory
                self.collection.delete(where={})
                print("Cleared all memory")
                
        except Exception as e:
            print(f"Error clearing memory: {e}") 