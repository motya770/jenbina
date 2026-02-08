from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..needs.maslow_needs import MaslowNeedsSystem
from ..emotions.emotion_system import EmotionSystem
from datetime import datetime


@dataclass
class Message:
    """Represents a single message in a conversation"""
    timestamp: datetime
    sender: str  # "person" or "outsider"
    content: str
    message_type: str = "text"  # text, action, system, etc.


@dataclass
class Conversation:
    """Represents a conversation with a specific outsider"""
    outsider_name: str
    messages: List[Message] = field(default_factory=list)
    last_interaction: datetime = field(default_factory=datetime.now)
    
    def add_message(self, sender: str, content: str, message_type: str = "text"):
        """Add a new message to the conversation"""
        message = Message(
            timestamp=datetime.now(),
            sender=sender,
            content=content,
            message_type=message_type
        )
        self.messages.append(message)
        self.last_interaction = datetime.now()
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get the most recent messages from the conversation"""
        return self.messages[-count:] if self.messages else []
    
    def get_messages_by_type(self, message_type: str) -> List[Message]:
        """Get all messages of a specific type"""
        return [msg for msg in self.messages if msg.message_type == message_type]
    
    def __str__(self):
        return f"Conversation with {self.outsider_name} ({len(self.messages)} messages, last: {self.last_interaction.strftime('%Y-%m-%d %H:%M')})"


@dataclass
class Person:
    name: str = "Jenbina"
    maslow_needs: MaslowNeedsSystem = None
    emotion_system: EmotionSystem = None
    learning_system: Any = None  # Initialized separately (needs LLM)
    goal_system: Any = None  # Initialized separately (needs LLM)
    planning_system: Any = None  # Initialized separately (needs LLM)
    conversations: Dict[str, Conversation] = field(default_factory=dict)

    def __post_init__(self):
        if self.maslow_needs is None:
            self.maslow_needs = MaslowNeedsSystem()
        if self.emotion_system is None:
            self.emotion_system = EmotionSystem()
    
    def init_learning_system(self, llm):
        """Initialize the learning system with an LLM instance.
        Called separately because LLM isn't available at Person creation time."""
        from ..learning.learning_system import LearningSystem
        self.learning_system = LearningSystem(llm)

    def init_goal_system(self, llm):
        """Initialize the goal system with an LLM instance.
        Called separately because LLM isn't available at Person creation time."""
        from ..goals.goal_system import GoalSystem
        self.goal_system = GoalSystem(llm)

    def init_planning_system(self, llm):
        """Initialize the planning system with an LLM instance.
        Called separately because LLM isn't available at Person creation time."""
        from ..planning.planning_system import PlanningSystem
        self.planning_system = PlanningSystem(llm)
    
    def update_all_needs(self):
        """Update all needs, decay emotions, and decay lessons"""
        self.maslow_needs.update_all_needs()
        self.emotion_system.update_all()
        # Decay learned lessons over time (small amount per update cycle)
        if self.learning_system is not None:
            self.learning_system.decay_all_lessons(hours=0.5)
        # Decay goal confidence over time
        if self.goal_system is not None:
            self.goal_system.decay_all_goals(hours=0.5)
    
    def get_needs_snapshot(self) -> Dict[str, float]:
        """Get current needs as a flat dict (for learning system)"""
        return {
            name: need.satisfaction 
            for name, need in self.maslow_needs.needs.items()
        }
    
    def get_emotions_snapshot(self) -> Dict[str, float]:
        """Get current emotions as a flat dict (for learning system)"""
        summary = self.emotion_system.get_emotional_state_summary()
        return summary.get("emotions", {})
    
    def add_conversation(self, outsider_name: str) -> Conversation:
        """Start a new conversation with an outsider"""
        if outsider_name not in self.conversations:
            self.conversations[outsider_name] = Conversation(outsider_name)
        return self.conversations[outsider_name]
    
    def receive_message(self, outsider_name: str, content: str, message_type: str = "text"):
        """Receive a message from an outsider"""
        conversation = self.add_conversation(outsider_name)
        conversation.add_message("outsider", content, message_type)
    
    def send_message(self, outsider_name: str, content: str, message_type: str = "text"):
        """Send a message to an outsider"""
        conversation = self.add_conversation(outsider_name)
        conversation.add_message("person", content, message_type)
    
    def get_conversation_history(self, outsider_name: str, count: int = None) -> List[Message]:
        """Get conversation history with a specific outsider"""
        if outsider_name not in self.conversations:
            return []
        
        conversation = self.conversations[outsider_name]
        if count is None:
            return conversation.messages
        return conversation.get_recent_messages(count)
    
    def get_all_conversations(self) -> Dict[str, Conversation]:
        """Get all conversations"""
        return self.conversations
    
    def get_conversation_summary(self, outsider_name: str) -> Dict[str, Any]:
        """Get a summary of conversation with a specific outsider"""
        if outsider_name not in self.conversations:
            return {"outsider_name": outsider_name, "message_count": 0, "last_interaction": None}
        
        conversation = self.conversations[outsider_name]
        return {
            "outsider_name": outsider_name,
            "message_count": len(conversation.messages),
            "last_interaction": conversation.last_interaction,
            "recent_messages": [{"sender": msg.sender, "content": msg.content, "timestamp": msg.timestamp} 
                               for msg in conversation.get_recent_messages(5)]
        }
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get overall communication statistics"""
        total_conversations = len(self.conversations)
        total_messages = sum(len(conv.messages) for conv in self.conversations.values())
        
        # Get most active conversations
        active_conversations = sorted(
            self.conversations.items(),
            key=lambda x: len(x[1].messages),
            reverse=True
        )[:5]
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "most_active_conversations": [
                {"outsider": name, "message_count": len(conv.messages)} 
                for name, conv in active_conversations
            ]
        }
    
    def get_current_state(self):
        """Get a summary of the person's current state"""
        state = {"name": self.name}

        # Add Maslow needs state
        state["maslow_needs"] = self.maslow_needs.get_needs_summary()

        # Add emotional state
        state["emotions"] = self.emotion_system.get_emotional_state_summary()

        # Add communication state
        comm_stats = self.get_communication_stats()
        state["communication"] = comm_stats

        # Add learning state
        if self.learning_system is not None:
            state["learning"] = self.learning_system.get_learning_stats()

        # Add goal state
        if self.goal_system is not None:
            state["goals"] = self.goal_system.get_goal_stats()

        # Add planning state
        if self.planning_system is not None:
            state["planning"] = self.planning_system.get_planning_stats()

        return state
    
    def __str__(self):
        comm_stats = self.get_communication_stats()
        maslow_summary = self.maslow_needs.get_needs_summary()
        dominant = self.emotion_system.get_dominant_emotions(2)
        emotions_str = ", ".join(f"{d['name']}:{d['intensity']}" for d in dominant)
        return f"Person(name={self.name}, maslow_stage={maslow_summary['stage_name']}, emotions=[{emotions_str}], conversations={comm_stats['total_conversations']}, messages={comm_stats['total_messages']})"
