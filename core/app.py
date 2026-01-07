import streamlit as st
from datetime import datetime
import sys
import os

# Add the parent directory to the Python path so we can import core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your other components with absolute imports
from core.cognition.action_decision_chain import create_action_decision_chain
from core.needs.maslow_needs import BasicNeeds, create_basic_needs_chain
from core.cognition.asimov_check_chain import create_asimov_check_system
from core.cognition.state_analysis_chain import create_state_analysis_system
from core.environment.world_state import WorldState, create_world_description_system, create_comprehensive_world_state, get_world_state_summary
from core.interaction.chat_handler import handle_chat_interaction
from core.person.person import Person
from core.cognition.meta_cognition import MetaCognitiveSystem
from core.cognition.enhanced_action_decision_chain import create_meta_cognitive_action_chain
from core.memory.conversation_memory import ChromaMemoryManager
from core.environment.environment_simulator import EnvironmentSimulator

# Initialize LLM
# os.environ['OLLAMA_HOST'] = 'http://129.153.140.217:11434'
os.environ['OLLAMA_HOST'] = 'http://localhost:11434'

os.environ['LANGSMITH_TRACING'] = 'true'
os.environ['LANGSMITH_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGSMITH_API_KEY'] = "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"
os.environ['LANGSMITH_PROJECT'] = "jenbina"


### LLM - Using ChatGPT as default
from langchain.schema import HumanMessage
from core.connect import get_llm, get_json_llm

# Use ChatGPT by default (change provider to "ollama" for local)
# Options: "openai" (GPT-5-nano), "openai-advanced" (GPT-5.2), "ollama" (local)
llm = get_llm(provider="openai", temperature=1)
llm_json_mode = get_json_llm(provider="openai", temperature=1)

# Example usage
person = Person()
person.update_all_needs()
print(person)

# Initialize meta-cognitive system
meta_cognitive_system = MetaCognitiveSystem(llm_json_mode)

# Initialize memory manager
memory_manager = ChromaMemoryManager()

# Initialize environment simulator
environment_simulator = EnvironmentSimulator("Palo Alto, CA")

# Initialize session state for meta-cognition
if 'meta_cognitive_system' not in st.session_state:
    st.session_state.meta_cognitive_system = meta_cognitive_system

# Initialize session state for memory manager
if 'memory_manager' not in st.session_state:
    st.session_state.memory_manager = memory_manager

# Initialize session state for environment simulator
if 'environment_simulator' not in st.session_state:
    st.session_state.environment_simulator = environment_simulator

# Initialize session state for person's state if not already done
if 'person' not in st.session_state:
    st.session_state.person = person
    st.session_state.action_history = []

st.title("Jenbina:")

# Get current environment state
current_environment = st.session_state.environment_simulator.get_environment_state()

# Display current environment
with st.sidebar:
    st.subheader("🌍 Current Environment")
    st.write(f"**Location:** {current_environment.location}")
    st.write(f"**Time:** {current_environment.time.current_time.strftime('%H:%M')}")
    st.write(f"**Day:** {current_environment.time.day_of_week}")
    st.write(f"**Weather:** {current_environment.weather.description}")
    st.write(f"**Temperature:** {current_environment.weather.temperature}°C")
    st.write(f"**Season:** {current_environment.time.season}")
    
    if current_environment.events:
        st.write("**Events:**")
        for event in current_environment.events:
            st.write(f"• {event}")
    
    # Location exploration
    st.subheader("🗺️ Explore Locations")
    
    # Get activity suggestion
    activity_suggestion = st.session_state.environment_simulator.location_system.get_daily_activity_suggestion()
    st.write(f"**Suggested Activity:** {activity_suggestion['activity']}")
    st.write(f"*{activity_suggestion['reason']}*")
    
    # Dynamic events and venues
    st.subheader("🎉 Dynamic Events & Venues")
    
    # Get today's highlights
    highlights = st.session_state.environment_simulator.get_today_highlights()
    for highlight in highlights:
        st.write(f"• {highlight}")
    
    # Get dynamic recommendations
    recommendations = st.session_state.environment_simulator.get_dynamic_recommendations()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🎵 Events This Week:**")
        if recommendations.get('events'):
            for event in recommendations['events'][:3]:
                st.write(f"• {event.name}")
                st.write(f"  {event.start_time.strftime('%m/%d %H:%M')} - {event.price}")
        else:
            st.write("• No events found")
    
    with col2:
        st.write("**🍺 Popular Venues:**")
        if recommendations.get('venues'):
            for venue in recommendations['venues'][:3]:
                st.write(f"• {venue.name}")
                st.write(f"  {venue.rating}⭐ ({venue.price_level})")
        else:
            st.write("• No venues found")
    
    # Location recommendations
    st.subheader("📍 Location Recommendations")
    col3, col4 = st.columns(2)
    
    with col3:
        st.write("**Popular Places:**")
        popular_locations = st.session_state.environment_simulator.location_system.get_popular_locations(0.7)
        for location in popular_locations[:3]:
            st.write(f"• {location.name} ({location.type})")
    
    with col4:
        st.write("**Currently Open:**")
        open_locations = st.session_state.environment_simulator.location_system.get_open_locations()
        for location in open_locations[:3]:
            st.write(f"• {location.name} ({location.type})")

# Debug mode toggle
debug_mode = st.sidebar.checkbox("🔧 Debug Mode", value=True, help="Show detailed debugging information")

# Debug controls
if debug_mode:
    st.sidebar.subheader("🔧 Debug Controls")
    
    # Memory operations
    if st.sidebar.button("🗑️ Clear All Memory"):
        st.session_state.memory_manager.clear_memory()
        st.sidebar.success("Memory cleared!")
    
    if st.sidebar.button("📊 Refresh Memory Stats"):
        st.sidebar.rerun()
    
    if st.sidebar.button("🔄 Refresh Environment"):
        st.sidebar.rerun()
    
    # Show current memory path
    st.sidebar.write(f"**Memory Path:** `{st.session_state.memory_manager.vector_store_path}`")
    
    # Show embedding model
    st.sidebar.write(f"**Embedding Model:** `{st.session_state.memory_manager.embeddings.model}`")

# Create columns for the interface layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("System Stages and Responses")
    
    # Initialize states if not already done
    if 'simulation_completed' not in st.session_state:
        st.session_state.simulation_completed = False
        st.session_state.needs_response = None
        st.session_state.world_description = None
        st.session_state.action_decision = None
        st.session_state.state_response = None

    if st.button("Start simulation"):
        # Display all stages
        st.write("### Processing Stages:")
        st.write("### Current Jenbina State:")
        st.write(f"- Name: {person.name}")
        st.write(f"- Overall Satisfaction: {person.maslow_needs.get_overall_satisfaction():.1f}%")
        st.write(f"- Hunger: {person.maslow_needs.get_need_satisfaction('hunger'):.1f}%")
        st.write(f"- Sleep: {person.maslow_needs.get_need_satisfaction('sleep'):.1f}%")
        st.write(f"- Safety: {person.maslow_needs.get_need_satisfaction('security'):.1f}%")
        
        # JSON representation of person object
        st.write("**Person Object (JSON):**")
        person_dict = {
            "name": person.name,
            "maslow_needs": {
                "overall_satisfaction": person.maslow_needs.get_overall_satisfaction(),
                "individual_needs": {
                    need_name: person.maslow_needs.get_need_satisfaction(need_name)
                    for need_name in ["hunger", "sleep", "security", "love", "esteem", "self_actualization"]
                    if person.maslow_needs.get_need_satisfaction(need_name) > 0
                },
                "critical_needs": person.maslow_needs.get_critical_needs(),
                "low_needs": person.maslow_needs.get_low_needs()
            }
        }
        st.json(person_dict)
        
        # Basic needs analysis
        st.write("**1. Basic Needs Analysis:**")
        needs_response = create_basic_needs_chain(llm_json_mode, person.maslow_needs)
        st.session_state.needs_response = needs_response
        st.write(st.session_state.needs_response)

        # World state and description
        st.write("**2. World State:**")
        world = create_comprehensive_world_state(person_location="Jenbina's House")
        world_summary = get_world_state_summary(world)
        
        st.write(f"Location: {world_summary['location']['name']}")
        st.write(f"Time of Day: {world_summary['time']['time_of_day']}")
        st.write(f"Weather: {world_summary['weather']['description']}")
        st.write(f"Temperature: {world_summary['weather']['temperature']:.1f}°C")
        st.write(f"Humidity: {world_summary['weather']['humidity']:.1f}%")
        st.write(f"Nearby Locations: {world_summary['environment']['nearby_locations_count']}")
        st.write(f"Open Locations: {world_summary['environment']['open_locations_count']}")
        st.write(f"Current Events: {world_summary['environment']['current_events_count']}")
        
        if world.last_descriptions:
            st.write(f"Previous Descriptions: {len(world.last_descriptions)} items")

        # Display world state as JSON
        st.write("**World State (JSON):**")
        st.json(world_summary)

        st.write("**2.1 World Description:**")
        world_chain = create_world_description_system(llm_json_mode)
        world_response = world_chain(person, world)
        st.session_state.world_description = world_response
        st.write(st.session_state.world_description)

        # Enhanced action decision with meta-cognition
        st.write("**3. Action Decision (with Meta-Cognition):**")
        action_response = create_meta_cognitive_action_chain(
            llm=llm_json_mode, 
            person=person, 
            world_description=st.session_state.world_description,
            meta_cognitive_system=st.session_state.meta_cognitive_system,
            world_state=world
        )
        st.session_state.action_decision = action_response
        st.write(st.session_state.action_decision)
        
        # Display meta-cognitive insights
        with st.expander("Meta-Cognitive Insights", expanded=False):
            meta_stats = st.session_state.meta_cognitive_system.get_meta_cognitive_stats()
            st.write(f"**Total Cognitive Processes:** {meta_stats['total_processes']}")
            st.write(f"**Total Insights:** {meta_stats['total_insights']}")
            
            st.write("**Cognitive Biases Detected:**")
            for bias, level in meta_stats['cognitive_biases'].items():
                if level > 0:
                    st.write(f"- {bias}: {level:.2f}")
            
            if meta_stats['recent_insights']:
                st.write("**Recent Insights:**")
                for insight in meta_stats['recent_insights']:
                    st.write(f"- **{insight['type']}**: {insight['description']}")

        # Asimov compliance check
        st.write("**5. Asimov Compliance Check:**")
        asimov_chain = create_asimov_check_system(llm_json_mode)
        asimov_response = asimov_chain(st.session_state.action_decision)
        st.write(asimov_response)

        # State analysis
        st.write("**4. State Analysis:**") 
        state_response = create_state_analysis_system(llm_json_mode, action_decision=st.session_state.action_decision, compliance_check=asimov_response)
        st.session_state.state_response = state_response
        st.write(st.session_state.state_response)

        # Mark simulation as completed
        st.session_state.simulation_completed = True

    # Chat interface - always available (simulation is optional)
    st.write("**6. Interaction with User:**")
    st.write("### Chat with Jenbina")
    
    # Display current person state
    st.write("**Current State:**")
    st.write(f"- Name: {person.name}")
    st.write(f"- Overall Satisfaction: {person.maslow_needs.get_overall_satisfaction():.1f}%")
    st.write(f"- Hunger: {person.maslow_needs.get_need_satisfaction('hunger'):.1f}%")
    st.write(f"- Sleep: {person.maslow_needs.get_need_satisfaction('sleep'):.1f}%")
    st.write(f"- Safety: {person.maslow_needs.get_need_satisfaction('security'):.1f}%")
    
    user_input = st.chat_input("Talk to Jenbina...")
    
    if user_input:
        print("User input:", user_input)
        
        # Store the user message in person's communication history
        person.receive_message("User", user_input, "text")
        
        # Get conversation history for context
        conversation_history = person.get_conversation_history("User", count=1000)
        recent_context = "\n".join([
            f"{msg.sender}: {msg.content}" 
            for msg in conversation_history  # All messages for context
        ])
        
        # Handle chat interaction using stored session state values and person's state
        chat_result = handle_chat_interaction(
            st=st,
            llm=llm,
            needs_response=st.session_state.needs_response,
            world_description=st.session_state.world_description,
            action_decision=st.session_state.action_decision,
            state_response=st.session_state.state_response,
            user_input=user_input,
            person_state=person.get_current_state(),
            conversation_context=recent_context,
            memory_manager=st.session_state.memory_manager,
            debug_mode=debug_mode
        )
        
        print(chat_result)

        # Store the person's response in communication history
        if "assistant_response" in chat_result:
            person.send_message("User", chat_result["assistant_response"], "text")

        # Add interactions to history
        if "user_message" in chat_result:
            st.session_state.action_history.append({
                "role": "user",
                "content": chat_result["user_message"]
            })
        st.session_state.action_history.append({
            "role": "assistant",
            "content": chat_result["assistant_response"]
        })
    
    # Display communication statistics
    with st.expander("Communication Statistics", expanded=False):
        comm_stats = person.get_communication_stats()
        st.write(f"**Total Conversations:** {comm_stats['total_conversations']}")
        st.write(f"**Total Messages:** {comm_stats['total_messages']}")
        
        if comm_stats['most_active_conversations']:
            st.write("**Most Active Conversations:**")
            for conv in comm_stats['most_active_conversations']:
                st.write(f"- {conv['outsider']}: {conv['message_count']} messages")
    
    # Display recent conversation history
    with st.expander("Recent Conversation History", expanded=False):
        user_summary = person.get_conversation_summary("User")
        if user_summary['message_count'] > 0:
            st.write(f"**Messages with User:** {user_summary['message_count']}")
            st.write(f"**Last Interaction:** {user_summary['last_interaction'].strftime('%Y-%m-%d %H:%M')}")
            
            st.write("**Recent Messages:**")
            for msg in user_summary['recent_messages']:
                sender_icon = "👤" if msg['sender'] == "User" else "🤖"
                st.write(f"{sender_icon} **{msg['sender']}** ({msg['timestamp'].strftime('%H:%M')}): {msg['content']}")
        else:
            st.write("No conversation history yet.")
    
    # Display memory system statistics
    with st.expander("Memory System Statistics", expanded=False):
        memory_stats = st.session_state.memory_manager.get_memory_stats()
        st.write(f"**Total Conversations in Memory:** {memory_stats.get('total_conversations', 0)}")
        st.write(f"**Unique People:** {memory_stats.get('unique_people', 0)}")
        st.write(f"**Memory Size:** {memory_stats.get('memory_size_mb', 0)} MB")
        
        if memory_stats.get('people'):
            st.write("**People in Memory:**")
            for person_name in memory_stats['people']:
                st.write(f"- {person_name}")
        
        if memory_stats.get('message_types'):
            st.write("**Message Types:**")
            for msg_type, count in memory_stats['message_types'].items():
                st.write(f"- {msg_type}: {count}")
    
    # Debug section for memory system
    if debug_mode:
        with st.expander("🐛 Memory Debug Info", expanded=False):
            st.write("**Memory Manager Status:**")
            st.write(f"- Memory Manager Initialized: {st.session_state.memory_manager is not None}")
            st.write(f"- Chroma Client: {st.session_state.memory_manager.client is not None if st.session_state.memory_manager else False}")
            st.write(f"- Collection: {st.session_state.memory_manager.collection is not None if st.session_state.memory_manager else False}")
            
            # Test memory operations
            if st.button("🧪 Test Memory Operations"):
                try:
                    # Test storing
                    test_id = st.session_state.memory_manager.store_conversation(
                        "TestUser", "This is a test message", "test_message"
                    )
                    st.success(f"✅ Test message stored with ID: {test_id}")
                    
                    # Test retrieval
                    test_context = st.session_state.memory_manager.retrieve_relevant_context(
                        "TestUser", "test message", top_k=1
                    )
                    st.success(f"✅ Test retrieval found {len(test_context)} documents")
                    
                    # Clean up test
                    st.session_state.memory_manager.clear_memory("TestUser")
                    st.success("✅ Test data cleaned up")
                    
                except Exception as e:
                    st.error(f"❌ Memory test failed: {str(e)}")

# with col2:
#     # Internal state visualization
#     st.subheader("Jenbina's Internal State")
#     st.write("Current Emotional State:", st.session_state.person.emotional_state)
#     st.write("Decision Making Process:")
    
#     # Display the reasoning chain
#     if st.session_state.action_history:
#         with st.expander("Latest Decision Chain", expanded=True):
#             chain = state_analysis_chain(st.session_state.person)
#             st.write(chain)
            
#     # Display Asimov compliance status
#     compliance_status = check_asimov_compliance(st.session_state.person)
#     st.metric("Asimov Compliance", value=f"{compliance_status}%") 