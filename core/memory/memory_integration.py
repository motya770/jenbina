"""
Memory Integration Module
Shows how to integrate the hybrid memory system with existing Jenbina components
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from .hybrid_memory_system import HybridMemorySystem, MemoryEvent
from ..person.person import Person

class MemoryIntegration:
    """
    Integrates the hybrid memory system with Jenbina's existing components
    """
    
    def __init__(self, memory_system: HybridMemorySystem):
        self.memory_system = memory_system
    
    def store_conversation_memory(self, 
                                 person_name: str, 
                                 message_content: str,
                                 message_type: str,
                                 sender_name: str = None,
                                 receiver_name: str = None,
                                 person_state: Person = None,
                                 metadata: Dict[str, Any] = None) -> str:
        """
        Store a conversation memory with full context
        
        Args:
            person_name: Name of the person being conversed with
            message_content: Content of the conversation
            message_type: Type of message (user_message, jenbina_response, etc.)
            sender_name: Name of the sender (defaults to person_name if None)
            receiver_name: Name of the receiver (defaults to "Jenbina" if None)
            person_state: Current state of Jenbina (Person object)
            metadata: Additional metadata
            
        Returns:
            event_id: Unique identifier for the stored memory
        """
        
        # Set default sender and receiver names
        if sender_name is None:
            sender_name = person_name
        if receiver_name is None:
            receiver_name = "Jenbina"
        
        # Extract current needs state
        needs_state = {}
        if person_state:
            for need_name, need_obj in person_state.maslow_needs.needs.items():
                needs_state[need_name] = need_obj.satisfaction
        
        # Create memory event
        event = MemoryEvent(
            event_id=None,  # Will be auto-generated
            timestamp=datetime.now(),
            event_type="conversation",
            content=message_content,
            people=[person_name] if person_name else [],
            locations=[],  # Could be extracted from context
            actions=["conversation"],
            emotions=[],  # Could be extracted from content analysis
            needs_state=needs_state,
            metadata={
                "message_type": message_type,
                "person_name": person_name,
                "sender_name": sender_name,
                "receiver_name": receiver_name,
                **(metadata or {})
            }
        )
        
        return self.memory_system.store_memory(event)
    
    def store_action_memory(self,
                           action_description: str,
                           action_type: str,
                           person_state: Person,
                           people_involved: List[str] = None,
                           location: str = None,
                           emotions: List[str] = None,
                           metadata: Dict[str, Any] = None) -> str:
        """
        Store an action memory with full context
        
        Args:
            action_description: Description of the action taken
            action_type: Type of action (walk, eat, sleep, etc.)
            person_state: Current state of Jenbina
            people_involved: List of people involved in the action
            location: Location where action occurred
            emotions: Emotions felt during the action
            metadata: Additional metadata
            
        Returns:
            event_id: Unique identifier for the stored memory
        """
        
        # Extract current needs state
        needs_state = {}
        for need_name, need_obj in person_state.maslow_needs.needs.items():
            needs_state[need_name] = need_obj.satisfaction
        
        # Create memory event
        event = MemoryEvent(
            event_id=None,
            timestamp=datetime.now(),
            event_type="action",
            content=action_description,
            people=people_involved or [],
            locations=[location] if location else [],
            actions=[action_type],
            emotions=emotions or [],
            needs_state=needs_state,
            metadata={
                "action_type": action_type,
                **(metadata or {})
            }
        )
        
        return self.memory_system.store_memory(event)
    
    def store_need_change_memory(self,
                                need_name: str,
                                old_value: float,
                                new_value: float,
                                reason: str,
                                person_state: Person,
                                metadata: Dict[str, Any] = None) -> str:
        """
        Store a memory of need state changes
        
        Args:
            need_name: Name of the need that changed
            old_value: Previous satisfaction level
            new_value: New satisfaction level
            reason: Reason for the change
            person_state: Current state of Jenbina
            metadata: Additional metadata
            
        Returns:
            event_id: Unique identifier for the stored memory
        """
        
        # Extract current needs state
        needs_state = {}
        for need_name, need_obj in person_state.maslow_needs.needs.items():
            needs_state[need_name] = need_obj.satisfaction
        
        # Create memory event
        event = MemoryEvent(
            event_id=None,
            timestamp=datetime.now(),
            event_type="need_change",
            content=f"Need '{need_name}' changed from {old_value:.1f}% to {new_value:.1f}%: {reason}",
            people=[],
            locations=[],
            actions=["need_change"],
            emotions=[],
            needs_state=needs_state,
            metadata={
                "need_name": need_name,
                "old_value": old_value,
                "new_value": new_value,
                "reason": reason,
                **(metadata or {})
            }
        )
        
        return self.memory_system.store_memory(event)
    
    def get_relevant_context(self, 
                           query: str, 
                           person_name: str = None,
                           top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Get relevant context for decision making
        
        Args:
            query: Query to search for relevant memories
            person_name: Optional person name to filter by
            top_k: Number of relevant memories to return
            
        Returns:
            List of relevant memory contexts
        """
        return self.memory_system.retrieve_semantic_memories(query, top_k)
    
    def get_person_context(self, person_name: str) -> Dict[str, Any]:
        """
        Get comprehensive context about a person
        
        Args:
            person_name: Name of the person
            
        Returns:
            Dictionary containing person's relationship data
        """
        return self.memory_system.get_person_relationships(person_name)
    
    def get_recent_memories(self, 
                           hours: int = 24,
                           event_type: str = None) -> List[Dict[str, Any]]:
        """
        Get recent memories within a time window
        
        Args:
            hours: Number of hours to look back
            event_type: Optional event type filter
            
        Returns:
            List of recent memories
        """
        from datetime import timedelta
        
        start_time = datetime.now() - timedelta(hours=hours)
        return self.memory_system.get_temporal_memories(
            start_time=start_time,
            end_time=datetime.now(),
            event_type=event_type
        )
    
    def get_needs_trends(self, 
                        need_name: str = None,
                        hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get trends in needs satisfaction over time
        
        Args:
            need_name: Optional specific need to track
            hours: Number of hours to look back
            
        Returns:
            List of needs history records
        """
        from datetime import timedelta
        
        start_time = datetime.now() - timedelta(hours=hours)
        return self.memory_system.get_needs_history(
            need_name=need_name,
            start_time=start_time,
            end_time=datetime.now()
        )
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all memory statistics
        
        Returns:
            Dictionary containing memory statistics
        """
        return self.memory_system.get_memory_stats()

# Example usage functions
def create_memory_integration() -> MemoryIntegration:
    """
    Create a memory integration instance with default settings
    
    Returns:
        MemoryIntegration instance
    """
    memory_system = HybridMemorySystem(
        embeddings_model="llama3.2:3b-instruct-fp16",
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password"
    )
    
    return MemoryIntegration(memory_system)

def example_usage():
    """
    Example of how to use the memory integration
    """
    print("🧠 Memory Integration Example")
    
    # Create memory integration
    memory_integration = create_memory_integration()
    
    # Create a sample person state
    person = Person()
    person.update_all_needs()
    
    # Store a conversation memory
    event_id = memory_integration.store_conversation_memory(
        person_name="Alice",
        message_content="Hello! How are you feeling today?",
        message_type="user_message",
        person_state=person,
        metadata={"topic": "greeting"}
    )
    print(f"✅ Stored conversation memory: {event_id}")
    
    # Store an action memory
    action_id = memory_integration.store_action_memory(
        action_description="Went for a walk in the park to clear my mind",
        action_type="walk",
        person_state=person,
        location="Central Park",
        emotions=["peaceful", "refreshed"],
        metadata={"duration_minutes": 30}
    )
    print(f"✅ Stored action memory: {action_id}")
    
    # Get relevant context
    context = memory_integration.get_relevant_context("walking and exercise", top_k=3)
    print(f"🔍 Found {len(context)} relevant memories")
    
    # Get person context
    alice_context = memory_integration.get_person_context("Alice")
    print(f"👥 Alice's context: {alice_context}")
    
    # Get memory summary
    summary = memory_integration.get_memory_summary()
    print(f"📊 Memory summary: {summary}")
    
    # Clean up
    memory_integration.memory_system.close()

if __name__ == "__main__":
    example_usage() 