"""Sidebar UI components for Jenbina app"""
import streamlit as st


def render_environment_sidebar(environment_simulator):
    """Render the environment information in the sidebar"""
    current_environment = environment_simulator.get_environment_state()
    
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


def render_location_exploration(environment_simulator):
    """Render location exploration section in sidebar"""
    st.subheader("🗺️ Explore Locations")
    
    # Get activity suggestion
    activity_suggestion = environment_simulator.location_system.get_daily_activity_suggestion()
    st.write(f"**Suggested Activity:** {activity_suggestion['activity']}")
    st.write(f"*{activity_suggestion['reason']}*")


def render_dynamic_events(environment_simulator):
    """Render dynamic events and venues section"""
    st.subheader("🎉 Dynamic Events & Venues")
    
    # Get today's highlights
    highlights = environment_simulator.get_today_highlights()
    for highlight in highlights:
        st.write(f"• {highlight}")
    
    # Get dynamic recommendations
    recommendations = environment_simulator.get_dynamic_recommendations()
    
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


def render_location_recommendations(environment_simulator):
    """Render location recommendations section"""
    st.subheader("📍 Location Recommendations")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Popular Places:**")
        popular_locations = environment_simulator.location_system.get_popular_locations(0.7)
        for location in popular_locations[:3]:
            st.write(f"• {location.name} ({location.type})")
    
    with col2:
        st.write("**Currently Open:**")
        open_locations = environment_simulator.location_system.get_open_locations()
        for location in open_locations[:3]:
            st.write(f"• {location.name} ({location.type})")


def render_debug_controls(memory_manager):
    """Render debug controls in sidebar"""
    st.subheader("🔧 Debug Controls")
    
    # Memory operations
    if st.button("🗑️ Clear All Memory"):
        memory_manager.clear_memory()
        st.success("Memory cleared!")
    
    if st.button("📊 Refresh Memory Stats"):
        st.rerun()
    
    if st.button("🔄 Refresh Environment"):
        st.rerun()
    
    # Show current memory path
    st.write(f"**Memory Path:** `{memory_manager.vector_store_path}`")
    
    # Show embedding model
    st.write(f"**Embedding Model:** `{memory_manager.embeddings.model}`")


def render_full_sidebar(environment_simulator, memory_manager, debug_mode):
    """Render the complete sidebar"""
    with st.sidebar:
        render_environment_sidebar(environment_simulator)
        render_location_exploration(environment_simulator)
        render_dynamic_events(environment_simulator)
        render_location_recommendations(environment_simulator)
        
        if debug_mode:
            render_debug_controls(memory_manager)
    
    return st.sidebar.checkbox("🔧 Debug Mode", value=True, help="Show detailed debugging information")
