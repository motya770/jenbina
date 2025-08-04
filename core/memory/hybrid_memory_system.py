from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import hashlib
import os
import chromadb
from chromadb.config import Settings
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

# ChromaDB availability check
try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("Warning: ChromaDB not installed. Install with: pip install chromadb")

# Neo4j imports
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("Warning: Neo4j driver not installed. Install with: pip install neo4j")

# Time-series imports
try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

@dataclass
class MemoryEvent:
    """Represents a memory event with all its components"""
    event_id: str
    timestamp: datetime
    event_type: str  # "conversation", "action", "need_change", "location_change"
    content: str
    people: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    emotions: List[str] = field(default_factory=list)
    needs_state: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PersonNode:
    """Represents a person in the graph database"""
    name: str
    first_met: datetime
    relationship_strength: float = 0.0  # 0-1 scale
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None
    personality_traits: Dict[str, float] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)

@dataclass
class LocationNode:
    """Represents a location in the graph database"""
    name: str
    location_type: str  # "home", "work", "restaurant", "park", etc.
    first_visited: datetime
    visit_count: int = 0
    last_visit: Optional[datetime] = None
    associated_emotions: List[str] = field(default_factory=list)

class HybridMemorySystem:
    """
    Hybrid memory system combining:
    - ChromaDB for semantic/contextual memory
    - Neo4j for relationship tracking
    - SQLite for chronological/time-series data
    """
    
    def __init__(self, 
                 embeddings_model: str = "llama3.2:3b-instruct-fp16",
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j",
                 neo4j_password: str = "password",
                 vector_store_path: str = "./jenbina_memory",
                 time_series_path: str = "./jenbina_memory/timeseries.db"):
        
        # Initialize logging first
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.embeddings = OllamaEmbeddings(model=embeddings_model)
        self.vector_store_path = vector_store_path
        self.time_series_path = time_series_path
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # Initialize vector store (ChromaDB)
        self._initialize_vector_store()
        
        # Initialize graph database (Neo4j)
        self._initialize_graph_database(neo4j_uri, neo4j_user, neo4j_password)
        
        # Initialize time-series database (SQLite)
        self._initialize_time_series_db()
    
    def _initialize_vector_store(self):
        """Initialize ChromaDB for semantic memory storage"""
        if not CHROMA_AVAILABLE:
            self.logger.warning("ChromaDB not available. Vector storage features will be disabled.")
            self.chroma_client = None
            self.chroma_collection = None
            return
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.vector_store_path, exist_ok=True)
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.vector_store_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            try:
                self.chroma_collection = self.chroma_client.get_collection("jenbina_memories")
                self.logger.info(f"Loaded existing ChromaDB collection from {self.vector_store_path}")
            except Exception as e:
                # If there's a schema mismatch or other error, try to reset and recreate
                if "no such column" in str(e) or "schema" in str(e).lower():
                    self.logger.warning(f"ChromaDB schema mismatch detected: {e}")
                    self.logger.info("Resetting ChromaDB database due to schema mismatch...")
                    try:
                        # Try to delete the collection if it exists
                        self.chroma_client.delete_collection("jenbina_memories")
                    except:
                        pass  # Collection might not exist
                    
                    # Try to reset the entire database
                    try:
                        import shutil
                        # Remove the entire ChromaDB directory and recreate
                        if os.path.exists(self.vector_store_path):
                            shutil.rmtree(self.vector_store_path)
                        os.makedirs(self.vector_store_path, exist_ok=True)
                        
                        # Recreate the client
                        self.chroma_client = chromadb.PersistentClient(
                            path=self.vector_store_path,
                            settings=Settings(
                                anonymized_telemetry=False,
                                allow_reset=True
                            )
                        )
                    except Exception as reset_error:
                        self.logger.error(f"Failed to reset ChromaDB: {reset_error}")
                        # Fallback to in-memory client
                        self.chroma_client = chromadb.Client()
                    
                    # Create fresh collection
                    self.chroma_collection = self.chroma_client.create_collection("jenbina_memories")
                    self.logger.info(f"Created new ChromaDB collection after schema reset at {self.vector_store_path}")
                else:
                    # For other errors, just create a new collection
                    self.chroma_collection = self.chroma_client.create_collection("jenbina_memories")
                    self.logger.info(f"Created new ChromaDB collection at {self.vector_store_path}")
                
        except Exception as e:
            self.logger.error(f"Error initializing ChromaDB: {e}")
            # Fallback to in-memory client
            self.chroma_client = chromadb.Client()
            self.chroma_collection = self.chroma_client.create_collection("jenbina_memories")
    
    def _initialize_graph_database(self, uri: str, user: str, password: str):
        """Initialize Neo4j for relationship tracking"""
        if not NEO4J_AVAILABLE:
            self.logger.warning("Neo4j driver not available. Graph features will be disabled.")
            self.graph_driver = None
            return
        
        try:
            self.graph_driver = GraphDatabase.driver(uri, auth=(user, password))
            
            # Test connection and create constraints
            with self.graph_driver.session() as session:
                # Create constraints for unique nodes
                session.run("CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE")
                session.run("CREATE CONSTRAINT location_name IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE")
                session.run("CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:Event) REQUIRE e.event_id IS UNIQUE")
                
            self.logger.info("Neo4j graph database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing Neo4j: {e}")
            self.graph_driver = None
    
    def _initialize_time_series_db(self):
        """Initialize SQLite for chronological/time-series data"""
        if not SQLITE_AVAILABLE:
            self.logger.warning("SQLite not available. Time-series features will be disabled.")
            self.time_series_conn = None
            return
        
        try:
            os.makedirs(os.path.dirname(self.time_series_path), exist_ok=True)
            self.time_series_conn = sqlite3.connect(self.time_series_path)
            
            # Create tables for time-series data
            cursor = self.time_series_conn.cursor()
            
            # Events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    content TEXT,
                    people TEXT,
                    locations TEXT,
                    actions TEXT,
                    emotions TEXT,
                    needs_state TEXT,
                    metadata TEXT
                )
            """)
            
            # Needs tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS needs_history (
                    timestamp TEXT NOT NULL,
                    need_name TEXT NOT NULL,
                    satisfaction_level REAL NOT NULL,
                    PRIMARY KEY (timestamp, need_name)
                )
            """)
            
            # Person interaction history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS person_interactions (
                    timestamp TEXT NOT NULL,
                    person_name TEXT NOT NULL,
                    interaction_type TEXT NOT NULL,
                    content TEXT,
                    emotion TEXT,
                    PRIMARY KEY (timestamp, person_name, interaction_type)
                )
            """)
            
            self.time_series_conn.commit()
            self.logger.info("Time-series database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing time-series database: {e}")
            self.time_series_conn = None
    
    def store_memory(self, event: MemoryEvent) -> str:
        """
        Store a memory event across all three databases
        
        Args:
            event: MemoryEvent object containing all event data
            
        Returns:
            event_id: Unique identifier for the stored event
        """
        event_id = event.event_id if event.event_id else self._generate_event_id(event)
        
        # 1. Store in ChromaDB (semantic memory)
        self._store_in_vector_db(event_id, event)
        
        # 2. Store in Neo4j (relationships)
        if self.graph_driver:
            self._store_in_graph_db(event_id, event)
        
        # 3. Store in SQLite (time-series)
        if self.time_series_conn:
            self._store_in_time_series_db(event_id, event)
        
        return event_id
    
    def _generate_event_id(self, event: MemoryEvent) -> str:
        """Generate a unique event ID"""
        unique_string = f"{event.timestamp.isoformat()}_{event.event_type}_{event.content[:50]}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _store_in_vector_db(self, event_id: str, event: MemoryEvent):
        """Store event in ChromaDB for semantic search"""
        try:
            # Create document for vector storage
            document = Document(
                page_content=event.content,
                metadata={
                    "event_id": event_id,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp.isoformat(),
                    "people": json.dumps(event.people),
                    "locations": json.dumps(event.locations),
                    "actions": json.dumps(event.actions),
                    "emotions": json.dumps(event.emotions),
                    "needs_state": json.dumps(event.needs_state)
                }
            )
            
            # Split document if needed
            documents = self.text_splitter.split_documents([document])
            
            # Store in ChromaDB
            for i, doc in enumerate(documents):
                chunk_id = f"{event_id}_chunk_{i}"
                self.chroma_collection.add(
                    documents=[doc.page_content],
                    metadatas=[doc.metadata],
                    ids=[chunk_id]
                )
                
        except Exception as e:
            self.logger.error(f"Error storing in vector database: {e}")
    
    def _store_in_graph_db(self, event_id: str, event: MemoryEvent):
        """Store event relationships in Neo4j"""
        if not self.graph_driver:
            return
        
        try:
            with self.graph_driver.session() as session:
                # Create event node
                session.run("""
                    CREATE (e:Event {
                        event_id: $event_id,
                        timestamp: $timestamp,
                        event_type: $event_type,
                        content: $content
                    })
                """, event_id=event_id, 
                    timestamp=event.timestamp.isoformat(),
                    event_type=event.event_type,
                    content=event.content)
                
                # Create person nodes and relationships
                for person in event.people:
                    session.run("""
                        MERGE (p:Person {name: $name})
                        ON CREATE SET p.first_met = $timestamp, p.interaction_count = 1
                        ON MATCH SET p.interaction_count = p.interaction_count + 1, p.last_interaction = $timestamp
                        WITH p
                        MATCH (e:Event {event_id: $event_id})
                        CREATE (p)-[:PARTICIPATED_IN]->(e)
                    """, name=person, timestamp=event.timestamp.isoformat(), event_id=event_id)
                
                # Create location nodes and relationships
                for location in event.locations:
                    session.run("""
                        MERGE (l:Location {name: $name})
                        ON CREATE SET l.first_visited = $timestamp, l.visit_count = 1
                        ON MATCH SET l.visit_count = l.visit_count + 1, l.last_visit = $timestamp
                        WITH l
                        MATCH (e:Event {event_id: $event_id})
                        CREATE (e)-[:OCCURRED_AT]->(l)
                    """, name=location, timestamp=event.timestamp.isoformat(), event_id=event_id)
                
                # Create action relationships
                for action in event.actions:
                    session.run("""
                        MATCH (e:Event {event_id: $event_id})
                        CREATE (e)-[:INVOLVED_ACTION]->(:Action {name: $action})
                    """, event_id=event_id, action=action)
                
        except Exception as e:
            self.logger.error(f"Error storing in graph database: {e}")
    
    def _store_in_time_series_db(self, event_id: str, event: MemoryEvent):
        """Store event in SQLite for chronological tracking"""
        if not self.time_series_conn:
            return
        
        try:
            cursor = self.time_series_conn.cursor()
            
            # Store main event
            cursor.execute("""
                INSERT OR REPLACE INTO events 
                (event_id, timestamp, event_type, content, people, locations, actions, emotions, needs_state, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                event.timestamp.isoformat(),
                event.event_type,
                event.content,
                json.dumps(event.people),
                json.dumps(event.locations),
                json.dumps(event.actions),
                json.dumps(event.emotions),
                json.dumps(event.needs_state),
                json.dumps(event.metadata)
            ))
            
            # Store needs state if present
            for need_name, satisfaction in event.needs_state.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO needs_history 
                    (timestamp, need_name, satisfaction_level)
                    VALUES (?, ?, ?)
                """, (event.timestamp.isoformat(), need_name, satisfaction))
            
            # Store person interactions
            for person in event.people:
                cursor.execute("""
                    INSERT OR REPLACE INTO person_interactions 
                    (timestamp, person_name, interaction_type, content, emotion)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    event.timestamp.isoformat(),
                    person,
                    event.event_type,
                    event.content,
                    json.dumps(event.emotions)
                ))
            
            self.time_series_conn.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing in time-series database: {e}")
    
    def retrieve_semantic_memories(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories based on semantic similarity"""
        try:
            results = self.chroma_collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            memories = []
            for i in range(len(results['ids'][0])):
                memory = {
                    'event_id': results['metadatas'][0][i].get('event_id'),
                    'content': results['documents'][0][i],
                    'event_type': results['metadatas'][0][i].get('event_type'),
                    'timestamp': results['metadatas'][0][i].get('timestamp'),
                    'people': json.loads(results['metadatas'][0][i].get('people', '[]')),
                    'locations': json.loads(results['metadatas'][0][i].get('locations', '[]')),
                    'actions': json.loads(results['metadatas'][0][i].get('actions', '[]')),
                    'emotions': json.loads(results['metadatas'][0][i].get('emotions', '[]')),
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            self.logger.error(f"Error retrieving semantic memories: {e}")
            return []
    
    def get_person_relationships(self, person_name: str) -> Dict[str, Any]:
        """Get all relationships and interactions for a person"""
        if not self.graph_driver:
            return {}
        
        try:
            with self.graph_driver.session() as session:
                # Get person node and basic info
                result = session.run("""
                    MATCH (p:Person {name: $name})
                    RETURN p
                """, name=person_name)
                
                person_data = result.single()
                if not person_data:
                    return {"person_name": person_name, "exists": False}
                
                person = person_data['p']
                
                # Get recent interactions
                interactions = session.run("""
                    MATCH (p:Person {name: $name})-[:PARTICIPATED_IN]->(e:Event)
                    RETURN e ORDER BY e.timestamp DESC LIMIT 10
                """, name=person_name)
                
                # Get shared locations
                locations = session.run("""
                    MATCH (p:Person {name: $name})-[:PARTICIPATED_IN]->(e:Event)-[:OCCURRED_AT]->(l:Location)
                    RETURN l.name, count(e) as visit_count
                    ORDER BY visit_count DESC
                """, name=person_name)
                
                return {
                    "person_name": person_name,
                    "exists": True,
                    "first_met": person.get('first_met'),
                    "interaction_count": person.get('interaction_count', 0),
                    "last_interaction": person.get('last_interaction'),
                    "recent_interactions": [dict(e) for e in interactions],
                    "shared_locations": [{"location": r['l.name'], "visits": r['visit_count']} for r in locations]
                }
                
        except Exception as e:
            self.logger.error(f"Error getting person relationships: {e}")
            return {"person_name": person_name, "error": str(e)}
    
    def get_temporal_memories(self, 
                            start_time: datetime = None, 
                            end_time: datetime = None,
                            event_type: str = None) -> List[Dict[str, Any]]:
        """Get memories within a time range"""
        if not self.time_series_conn:
            return []
        
        try:
            cursor = self.time_series_conn.cursor()
            
            query = "SELECT * FROM events WHERE 1=1"
            params = []
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            memories = []
            for row in rows:
                memory = {
                    'event_id': row[0],
                    'timestamp': row[1],
                    'event_type': row[2],
                    'content': row[3],
                    'people': json.loads(row[4] or '[]'),
                    'locations': json.loads(row[5] or '[]'),
                    'actions': json.loads(row[6] or '[]'),
                    'emotions': json.loads(row[7] or '[]'),
                    'needs_state': json.loads(row[8] or '{}'),
                    'metadata': json.loads(row[9] or '{}')
                }
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            self.logger.error(f"Error retrieving temporal memories: {e}")
            return []
    
    def get_needs_history(self, 
                         need_name: str = None,
                         start_time: datetime = None,
                         end_time: datetime = None) -> List[Dict[str, Any]]:
        """Get needs satisfaction history over time"""
        if not self.time_series_conn:
            return []
        
        try:
            cursor = self.time_series_conn.cursor()
            
            query = "SELECT * FROM needs_history WHERE 1=1"
            params = []
            
            if need_name:
                query += " AND need_name = ?"
                params.append(need_name)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    'timestamp': row[0],
                    'need_name': row[1],
                    'satisfaction_level': row[2]
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error retrieving needs history: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory system"""
        stats = {
            "vector_db": {},
            "graph_db": {},
            "time_series_db": {}
        }
        
        # ChromaDB stats
        try:
            stats["vector_db"]["collection_count"] = self.chroma_collection.count()
        except:
            stats["vector_db"]["collection_count"] = 0
        
        # Neo4j stats
        if self.graph_driver:
            try:
                with self.graph_driver.session() as session:
                    person_count = session.run("MATCH (p:Person) RETURN count(p) as count").single()['count']
                    location_count = session.run("MATCH (l:Location) RETURN count(l) as count").single()['count']
                    event_count = session.run("MATCH (e:Event) RETURN count(e) as count").single()['count']
                    
                    stats["graph_db"] = {
                        "person_count": person_count,
                        "location_count": location_count,
                        "event_count": event_count
                    }
            except Exception as e:
                stats["graph_db"]["error"] = str(e)
        
        # SQLite stats
        if self.time_series_conn:
            try:
                cursor = self.time_series_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM events")
                event_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM needs_history")
                needs_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM person_interactions")
                interaction_count = cursor.fetchone()[0]
                
                stats["time_series_db"] = {
                    "event_count": event_count,
                    "needs_records": needs_count,
                    "interaction_records": interaction_count
                }
            except Exception as e:
                stats["time_series_db"]["error"] = str(e)
        
        return stats
    
    def close(self):
        """Close all database connections"""
        if self.graph_driver:
            self.graph_driver.close()
        
        if self.time_series_conn:
            self.time_series_conn.close() 