"""Simulation UI components and runner for Jenbina app"""
import streamlit as st
from contextlib import contextmanager
from datetime import datetime
import time
import json
import os
from types import SimpleNamespace

from core.needs.maslow_needs import create_basic_needs_chain
from core.needs.maslow_decision_chain import create_maslow_action_executor
from core.cognition.asimov_check_chain import create_asimov_check_system
from core.cognition.state_analysis_chain import create_state_analysis_system
from core.environment.world_state import create_world_description_system, create_comprehensive_world_state, get_world_state_summary
from core.environment.location_system import PaloAltoLocationSystem
from core.cognition.enhanced_action_decision_chain import create_meta_cognitive_action_chain
from core.emotions.emotion_analysis_chain import analyze_emotion_impact
from core.ui.chat import update_system_stage, send_proactive_message


def inject_tamagotchi_css():
    """Inject Tamagotchi-themed CSS. Call once at the start of each page render."""
    st.markdown("""
    <style>
    /* Tamagotchi Theme */
    .stApp {
        background-color: #FFF8F0;
    }

    /* Force readable text colors on cream background */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #3D2B1F !important;
    }
    .stApp p, .stApp span, .stApp label, .stApp div {
        color: #5C4033;
    }
    .stApp .stMarkdown, .stApp .stMarkdown p {
        color: #5C4033 !important;
    }

    /* Title styling */
    .stApp [data-testid="stTitle"],
    .stApp [data-testid="stHeading"] {
        color: #3D2B1F !important;
    }

    /* Page link / nav styling */
    .stApp a {
        color: #D4567A !important;
        font-weight: 500;
    }
    .stApp a:hover {
        color: #FF8FAB !important;
    }

    /* Number input styling */
    .stApp [data-testid="stNumberInput"] input {
        background-color: #FFF !important;
        color: #3D2B1F !important;
        border: 2px solid #FFD7BA !important;
        border-radius: 10px !important;
    }
    .stApp [data-testid="stNumberInput"] label {
        color: #5C4033 !important;
        font-weight: 500;
    }
    .stApp [data-testid="stNumberInput"] button {
        color: #5C4033 !important;
        background-color: #FFF3EC !important;
        border-color: #FFD7BA !important;
    }

    /* Button styling */
    .stApp button[kind="primary"],
    .stApp button[data-testid="stBaseButton-primary"] {
        background-color: #FF8FAB !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    .stApp button[kind="secondary"],
    .stApp button[data-testid="stBaseButton-secondary"] {
        background-color: #FFF3EC !important;
        color: #5C4033 !important;
        border: 2px solid #FFD7BA !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
    }

    /* Checkbox styling */
    .stApp [data-testid="stCheckbox"] label {
        color: #5C4033 !important;
    }

    /* Divider */
    .stApp hr {
        border-color: #F0E6D8 !important;
    }

    /* Page links in nav */
    .stApp [data-testid="stPageLink"] {
        background-color: #FFF3EC !important;
        border-radius: 10px !important;
        border: 1px solid #FFD7BA !important;
    }
    .stApp [data-testid="stPageLink"] a,
    .stApp [data-testid="stPageLink"] span {
        color: #5C4033 !important;
        font-weight: 500 !important;
    }

    /* Environment ribbon */
    .env-ribbon {
        background: linear-gradient(135deg, #FFE5D9, #FFD7BA);
        border-radius: 12px;
        padding: 8px 20px;
        text-align: center;
        font-size: 1.1em;
        color: #5C4033;
        margin-bottom: 16px;
        font-weight: 500;
    }

    /* Character frame */
    .character-frame {
        text-align: center;
        padding: 16px;
    }
    .character-frame img {
        border-radius: 20px;
        border: 4px solid #FFD7BA;
        box-shadow: 0 4px 16px rgba(255, 143, 171, 0.2);
    }

    /* Thought bubble */
    .thought-bubble {
        background: white;
        border-radius: 18px;
        padding: 12px 20px;
        margin: 8px auto;
        max-width: 500px;
        text-align: center;
        font-style: italic;
        color: #666;
        border: 2px solid #F0E6D8;
        position: relative;
    }
    .thought-bubble::before {
        content: '💭';
        position: absolute;
        top: -14px;
        left: 20px;
        font-size: 1.2em;
    }

    /* Needs bar */
    .need-row {
        display: flex;
        align-items: center;
        margin: 4px 0;
        gap: 8px;
    }
    .need-icon {
        font-size: 1.2em;
        width: 28px;
        text-align: center;
    }
    .need-label {
        width: 110px;
        font-size: 0.9em;
        color: #5C4033;
    }
    .need-bar-bg {
        flex: 1;
        height: 18px;
        background: #F0E6D8;
        border-radius: 9px;
        overflow: hidden;
    }
    .need-bar-fill {
        height: 100%;
        border-radius: 9px;
        transition: width 0.5s ease;
    }
    .need-pct {
        width: 45px;
        text-align: right;
        font-size: 0.85em;
        color: #888;
        font-weight: 600;
    }

    /* Pulse animation for critical needs */
    @keyframes pulse-critical {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    .need-critical .need-bar-fill {
        animation: pulse-critical 1.5s ease-in-out infinite;
    }

    /* Emotion chips */
    .emotion-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        margin: 8px 0;
    }
    .emotion-chip {
        background: white;
        border: 2px solid #FFD7BA;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.9em;
        color: #5C4033;
    }

    /* Action story card */
    .action-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
        border-left: 5px solid #FF8FAB;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .action-title {
        font-size: 1.15em;
        font-weight: 600;
        color: #333;
        margin-bottom: 6px;
    }
    .action-reasoning {
        font-size: 0.9em;
        color: #888;
        margin-bottom: 10px;
    }
    .satisfaction-delta {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 600;
    }
    .delta-positive {
        background: #E8F5E9;
        color: #2E7D32;
    }
    .delta-negative {
        background: #FFEBEE;
        color: #C62828;
    }
    .delta-neutral {
        background: #FFF8E1;
        color: #F57F17;
    }
    </style>
    """, unsafe_allow_html=True)


# Path to Jenbina images
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "images")


def _get_image_path(name):
    """Get absolute path to a Jenbina image."""
    return os.path.join(IMAGES_DIR, name)


def get_jenbina_image_for_action(chosen_action):
    """Determine which Jenbina image to show based on the chosen action."""
    action_lower = chosen_action.lower() if chosen_action else ""

    # Action-based mapping
    action_map = [
        (["eat", "food", "cook", "meal", "snack", "breakfast", "lunch", "dinner", "hungry"], "jenbina_eat.png"),
        (["drink", "water", "thirst", "hydrat", "beverage", "tea", "coffee"], "jenbina_drink.png"),
        (["walk", "move", "explor", "travel", "wander", "go to", "visit", "roam", "stroll"], "jenbina_walks.png"),
        (["sleep", "rest", "nap", "bed", "doze"], "jenbina_sleep.png"),
        (["talk", "chat", "convers", "speak", "social", "friend", "greet", "discuss"], "jenbina_talk.png"),
        (["read", "study", "learn", "book", "research", "reflect", "meditat", "think", "journal"], "jenbina_read.png"),
    ]

    for keywords, image_name in action_map:
        for kw in keywords:
            if kw in action_lower:
                return _get_image_path(image_name)

    return None  # No action-specific image matched


def get_jenbina_image_for_emotion(person):
    """Determine which Jenbina image to show based on dominant emotion."""
    dominant = person.emotion_system.get_dominant_emotions(1)
    if not dominant:
        return _get_image_path("jenbina_base.png")

    top_emotion = dominant[0]["name"].lower()
    intensity = dominant[0]["intensity"]

    if top_emotion == "joy" and intensity > 30:
        return _get_image_path("jenbina_smile.png")
    elif top_emotion == "sadness" and intensity > 30:
        return _get_image_path("jenbina_sad.png")
    elif top_emotion == "anger" and intensity > 30:
        return _get_image_path("jenbina_angry.png")
    elif top_emotion == "fear" and intensity > 30:
        return _get_image_path("jenbina_scary.png")
    elif top_emotion == "surprise" and intensity > 30:
        return _get_image_path("jenbina_surprised.png")

    return _get_image_path("jenbina_base.png")


def display_jenbina_image(image_path, caption=None):
    """Display a Jenbina image in the UI if the file exists."""
    if os.path.exists(image_path):
        st.image(image_path, caption=caption, width=175)
    else:
        # Fallback to base image if the specific one doesn't exist
        base = _get_image_path("jenbina_base.png")
        if os.path.exists(base):
            st.image(base, caption=caption or "Jenbina", width=125)


def render_environment_ribbon(world_summary):
    """Render a single-line environment ribbon at the top."""
    location = world_summary.get("location", {}).get("name", "Unknown")
    time_of_day = world_summary.get("time", {}).get("time_of_day", "unknown")
    weather = world_summary.get("weather", {}).get("description", "unknown")
    temp = world_summary.get("weather", {}).get("temperature", 0)

    weather_icons = {
        "sunny": "☀️", "clear": "☀️", "cloudy": "☁️", "overcast": "☁️",
        "rain": "🌧️", "storm": "⛈️", "snow": "❄️", "fog": "🌫️",
        "wind": "💨", "hot": "🔥", "cold": "🥶",
    }
    weather_icon = "🌤️"
    for keyword, icon in weather_icons.items():
        if keyword in weather.lower():
            weather_icon = icon
            break

    st.markdown(
        f'<div class="env-ribbon">{weather_icon} {location} · {time_of_day.capitalize()} · {weather} · {temp:.0f}°C</div>',
        unsafe_allow_html=True,
    )


def render_needs_bars(person):
    """Render Maslow needs as colored game-style progress bars."""
    needs_config = [
        ("hunger", "🍔", "Hunger"),
        ("sleep", "😴", "Sleep"),
        ("security", "🛡️", "Safety"),
        ("love", "💕", "Social"),
        ("esteem", "⭐", "Esteem"),
        ("self_actualization", "🌟", "Growth"),
    ]

    html_parts = []
    for need_name, icon, label in needs_config:
        satisfaction = person.maslow_needs.get_need_satisfaction(need_name)
        pct = max(0, min(100, satisfaction))

        if pct < 30:
            color = "#FF6B6B"
        elif pct < 60:
            color = "#FFD93D"
        else:
            color = "#6BCB77"

        critical_class = "need-critical" if pct < 30 else ""

        html_parts.append(f"""
        <div class="need-row {critical_class}">
            <span class="need-icon">{icon}</span>
            <span class="need-label">{label}</span>
            <div class="need-bar-bg">
                <div class="need-bar-fill" style="width: {pct}%; background: {color};"></div>
            </div>
            <span class="need-pct">{pct:.0f}%</span>
        </div>
        """)

    st.markdown("".join(html_parts), unsafe_allow_html=True)


def render_emotion_chips(person):
    """Render top emotions as colored pill chips."""
    emotion_icons = {
        "joy": "😊", "sadness": "😢", "anger": "😠", "fear": "😨",
        "surprise": "😮", "disgust": "🤢", "trust": "🤝", "anticipation": "🤩",
    }

    all_emotions = person.emotion_system.get_emotional_state_summary().get("emotions", {})
    visible = sorted(
        [(name, val) for name, val in all_emotions.items() if val > 15],
        key=lambda x: x[1],
        reverse=True,
    )[:4]

    if not visible:
        return

    chips_html = '<div class="emotion-chips">'
    for name, intensity in visible:
        icon = emotion_icons.get(name.lower(), "💭")
        chips_html += f'<span class="emotion-chip">{icon} {name.capitalize()} ({intensity:.0f})</span>'
    chips_html += "</div>"

    st.markdown(chips_html, unsafe_allow_html=True)


def render_mood_indicator(person):
    """Render a small colored pill badge showing Jenbina's dominant mood."""
    dominant = person.emotion_system.get_dominant_emotions(1)
    if not dominant:
        return

    emotion_name = dominant[0]["name"].lower()
    intensity = int(dominant[0]["intensity"])

    emoji_map = {
        "joy": "😊", "sadness": "😢", "anger": "😠", "fear": "😨",
        "surprise": "😲", "disgust": "🤢", "trust": "🤗", "anticipation": "✨",
    }
    positive_emotions = {"joy", "trust", "anticipation", "surprise"}
    emoji = emoji_map.get(emotion_name, "💭")
    color = "#4CAF50" if emotion_name in positive_emotions else "#E53935"

    st.markdown(
        f'<span style="background:{color};color:white;padding:4px 12px;border-radius:12px;'
        f'font-size:0.9em;font-weight:600;">{emoji} {emotion_name.capitalize()} ({intensity})</span>',
        unsafe_allow_html=True,
    )


def render_action_narrative(action_response, satisfaction_before, satisfaction_after):
    """Render the action decision as a narrative story card."""
    if not isinstance(action_response, dict):
        st.write(str(action_response))
        return

    chosen = action_response.get("chosen_action", "Unknown action")
    reasoning = action_response.get("reasoning", "")
    lessons = action_response.get("lessons_applied", "")

    delta = satisfaction_after - satisfaction_before
    if delta > 0:
        delta_class = "delta-positive"
        delta_icon = "📈"
    elif delta < 0:
        delta_class = "delta-negative"
        delta_icon = "📉"
    else:
        delta_class = "delta-neutral"
        delta_icon = "➡️"

    reasoning_html = f'<div class="action-reasoning">"{reasoning}"</div>' if reasoning else ""
    lessons_html = f'<div class="action-reasoning">Lessons applied: {lessons}</div>' if lessons else ""

    st.markdown(f"""
    <div class="action-card">
        <div class="action-title">▶ Jenbina decided to {chosen.lower()}</div>
        {reasoning_html}
        {lessons_html}
        <span class="satisfaction-delta {delta_class}">
            {delta_icon} Satisfaction: {satisfaction_before:.0f}% → {satisfaction_after:.0f}% ({delta:+.1f}%)
        </span>
    </div>
    """, unsafe_allow_html=True)


def get_person_dict(person):
    """Get person state as dictionary for display"""
    return {
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
        },
        "emotions": person.emotion_system.get_emotional_state_summary()
    }


def display_person_state(person):
    """Display current person state"""
    st.write("### Current Jenbina State:")
    st.write(f"- Name: {person.name}")
    st.write(f"- Overall Satisfaction: {person.maslow_needs.get_overall_satisfaction():.1f}%")
    st.write(f"- Hunger: {person.maslow_needs.get_need_satisfaction('hunger'):.1f}%")
    st.write(f"- Sleep: {person.maslow_needs.get_need_satisfaction('sleep'):.1f}%")
    st.write(f"- Safety: {person.maslow_needs.get_need_satisfaction('security'):.1f}%")

    # Display emotional state
    dominant = person.emotion_system.get_dominant_emotions(3)
    st.write("**Emotional State:**")
    for emo in dominant:
        st.write(f"- {emo['name'].capitalize()}: {emo['intensity']}")
    all_emotions = person.emotion_system.get_emotional_state_summary()["emotions"]
    with st.container(border=True):
        st.caption("All Emotions")
        for name, val in all_emotions.items():
            st.write(f"- {name}: {val}")


def display_world_state(world_summary, world):
    """Display world state information"""
    st.write("**2. World State:**")
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
    
    st.write("**World State (JSON):**")
    st.json(world_summary)


def display_meta_cognitive_insights(meta_cognitive_system, iteration):
    """Display meta-cognitive insights with expander toggle"""
    with st.container(border=True):
        st.caption("🧠 Meta-Cognitive Insights")
        meta_stats = meta_cognitive_system.get_meta_cognitive_stats()
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


def display_learning_stats(person, iteration):
    """Display learning system stats"""
    if person.learning_system is None:
        return
    
    stats = person.learning_system.get_learning_stats()
    with st.container(border=True):
        st.caption("📚 Learning Stats")
        st.write(f"**Total Experiences:** {stats['total_experiences']}")
        st.write(f"**Active Lessons:** {stats['active_lessons']} / {stats['total_lessons']}")
        
        if stats['lessons']:
            st.write("**Learned Lessons:**")
            for lesson in stats['lessons']:
                confidence_bar = "█" * int(lesson['confidence'] * 10) + "░" * (10 - int(lesson['confidence'] * 10))
                st.write(
                    f"- [{lesson['category']}] {lesson['description']}\n"
                    f"  Confidence: {confidence_bar} {lesson['confidence']:.0%} | "
                    f"Confirmed: {lesson['times_confirmed']}x | "
                    f"Action: {lesson['recommended_action']}"
                )
        else:
            st.write("*No lessons learned yet. Jenbina needs more experiences.*")


def display_goal_stats(person, iteration):
    """Display goal system stats"""
    if person.goal_system is None:
        return

    stats = person.goal_system.get_goal_stats()
    with st.container(border=True):
        st.caption("🎯 Goal Stats")
        st.write(f"**Active Goals:** {stats['active_goals']} | **Completed:** {stats['completed_goals']} | **Abandoned:** {stats['abandoned_goals']}")

        if stats['goals']:
            st.write("**Active Goals:**")
            for goal in stats['goals']:
                progress_bar = "█" * int(goal['progress'] * 10) + "░" * (10 - int(goal['progress'] * 10))
                st.write(
                    f"- [{goal['horizon']}] {goal['description']}\n"
                    f"  Progress: {progress_bar} {goal['progress']:.0%} | "
                    f"Confidence: {goal['confidence']:.0%} | "
                    f"Advanced: {goal['times_advanced']}x"
                )
        else:
            st.write("*No active goals. Jenbina needs more experiences to form goals.*")

        if stats['completed']:
            st.write("**Recently Completed:**")
            for goal in stats['completed']:
                st.write(f"- ✅ {goal['description']}")


def display_working_memory_stats(person, iteration):
    """Display working memory stats"""
    stats = person.working_memory.get_stats()
    with st.container(border=True):
        st.caption("🧠 Working Memory")
        st.write(f"**Focus:** {stats['focus']:.0f}% | **Capacity:** {stats['buffer_size']}/{stats['capacity']} | **Context Switches:** {stats['context_switches']}")
        if stats['items']:
            for item in stats['items']:
                bar_len = int(item['salience'] * 10)
                bar = "█" * bar_len + "░" * (10 - bar_len)
                st.write(f"- [{item['source']}] {item['content']} | {bar} {item['salience']:.2f}")
        else:
            st.write("*Mind is clear.*")


def display_identity_stats(person, iteration):
    """Display self-narrative and identity stats."""
    if getattr(person, "self_narrative", None) is None:
        return

    stats = person.self_narrative.get_stats()
    with st.container(border=True):
        st.caption("🪞 Identity & Narrative")
        st.write(f"**Coherence:** {stats['identity_coherence']:.2f} | **Crisis:** {stats['identity_crisis_level']:.2f}")
        st.write("**Self Concept:**")
        for line in stats.get("self_concept", [])[:3]:
            st.write(f"- {line}")
        st.write("**Life Story:**")
        st.write(stats.get("life_story", ""))
        values = stats.get("values", {})
        if values:
            top = sorted(values.items(), key=lambda kv: kv[1], reverse=True)[:5]
            st.write("**Top Values:**")
            for name, score in top:
                st.write(f"- {name}: {score:.2f}")


def display_curiosity_stats(person, iteration):
    """Display curiosity and exploration stats."""
    if getattr(person, "curiosity_system", None) is None:
        return

    stats = person.curiosity_system.get_stats()
    with st.container(border=True):
        st.caption("🔎 Curiosity & Exploration")
        st.write(
            f"**Curiosity:** {stats['curiosity_level']:.2f} | "
            f"**Boredom:** {stats['boredom_level']:.2f} | "
            f"**Novelty:** {stats['last_novelty_score']:.2f} | "
            f"**Explore?:** {'yes' if stats['should_explore'] else 'no'}"
        )
        if stats.get("open_questions"):
            st.write("**Open Questions:**")
            for q in stats["open_questions"][:3]:
                st.write(f"- {q}")
        if stats.get("suggested_explorations"):
            st.write("**Exploration Candidates:**")
            for a in stats["suggested_explorations"][:5]:
                st.write(f"- {a}")


def display_planning_stats(person, iteration):
    """Display planning system stats"""
    if person.planning_system is None:
        return

    stats = person.planning_system.get_planning_stats()
    with st.container(border=True):
        st.caption("📋 Planning Stats")
        st.write(f"**Active Plans:** {stats['active_plans']} | **Completed:** {stats['completed_plans']} | **Failed:** {stats['failed_plans']}")

        if stats['plans']:
            st.write("**Active Plans:**")
            for plan_data in stats['plans']:
                steps = plan_data.get('steps', [])
                current_idx = plan_data.get('current_step_index', 0)
                total = len(steps)
                completed_count = len([s for s in steps if s['status'] == 'completed'])
                st.write(
                    f"- **{plan_data['goal_description']}**\n"
                    f"  Step {current_idx + 1} of {total} | "
                    f"Completed: {completed_count}/{total} | "
                    f"Replanned: {plan_data.get('times_replanned', 0)}x"
                )
                for i, step in enumerate(steps):
                    icon = "✅" if step['status'] == 'completed' else "▶️" if step['status'] == 'active' else "⏳" if step['status'] == 'pending' else "❌"
                    st.write(f"  {icon} {step['description']} ({step['actual_cycles']}/{step['estimated_cycles']} cycles)")
        else:
            st.write("*No active plans.*")


def _print_json(label: str, data):
    """Pretty-print an LLM response to console."""
    try:
        if isinstance(data, dict):
            formatted = json.dumps(data, indent=2, default=str)
        elif isinstance(data, str):
            formatted = data
        else:
            formatted = json.dumps(str(data), indent=2)
        print(f"  {label}:")
        for line in formatted.splitlines():
            print(f"    {line}")
    except Exception:
        print(f"  {label}: {data}")


@contextmanager
def _card(title: str):
    """Render a bordered card with a bold title."""
    with st.container(border=True):
        st.markdown(f"**{title}**")
        yield


def _detect_location_from_action(chosen_action: str) -> str | None:
    """Detect if the chosen action moves Jenbina to a known location.

    Returns the location name if a match is found, otherwise None.
    """
    if not chosen_action:
        return None

    action_lower = chosen_action.lower()

    # All known locations — order matters: check longer/more specific names first
    location_system = PaloAltoLocationSystem()
    location_names = sorted(location_system.locations.keys(), key=len, reverse=True)

    for name in location_names:
        if name.lower() in action_lower:
            return name

    # Keyword aliases for common references
    _aliases = {
        "home": "Jenbina's House",
        "go back home": "Jenbina's House",
        "return home": "Jenbina's House",
        "head home": "Jenbina's House",
        "coupa": "Coupa Cafe",
        "baylands": "Baylands Nature Preserve",
        "stanford campus": "Stanford University",
        "shopping center": "Stanford Shopping Center",
        "shopping mall": "Stanford Shopping Center",
        "computer museum": "Computer History Museum",
        "history museum": "Computer History Museum",
        "filoli": "Filoli Gardens",
        "half moon": "Half Moon Bay",
        "santana": "Santana Row",
        "university ave": "University Avenue",
        "downtown": "University Avenue",
    }
    for alias, loc_name in _aliases.items():
        if alias in action_lower:
            return loc_name

    return None


def run_single_iteration(person, llm_json_mode, meta_cognitive_system, iteration):
    """Run a single simulation iteration with live-updating card grid.

    Each card computes its data then renders immediately so the UI
    updates progressively as each LLM call completes.
    """
    iteration_start_time = datetime.now()
    iter_num = iteration + 1
    print(f"{'='*60}")
    print(f"  🔄 ITERATION {iter_num}")
    print(f"{'='*60}")

    # ── SNAPSHOT BEFORE ─────────────────────────────────────────────────
    needs_before = person.get_needs_snapshot()
    emotions_before = person.get_emotions_snapshot()
    satisfaction_before = person.maslow_needs.get_overall_satisfaction()
    print(f"📸 Snapshot | Satisfaction: {satisfaction_before:.1f}%")

    # ==================================================================
    # Environment row — fast local data, render immediately
    # ==================================================================
    print(f"{'─'*40}")
    print(f"  🌍 Stage 1: Environment")
    print(f"{'─'*40}")
    update_system_stage("Building environment...")
    person_dict = get_person_dict(person)
    # Use tracked location (updated after each action) or default to home
    current_location = st.session_state.get("jenbina_location", "Jenbina's House")
    world = create_comprehensive_world_state(person_location=current_location)
    world_summary = get_world_state_summary(world)
    print(f"  👤 Person: {person.name} | Satisfaction: {satisfaction_before:.1f}%")
    print(f"  📍 Location: {world_summary['location']['name']}")
    print(f"  🕐 Time: {world_summary['time']['time_of_day']}")
    print(f"  🌤️  Weather: {world_summary['weather']['description']} ({world_summary['weather']['temperature']:.0f}°C)")

    # ── Tamagotchi Screen ─────────────────────────────────────────────
    inject_tamagotchi_css()
    render_environment_ribbon(world_summary)

    # Centered Jenbina avatar
    _, avatar_center, _ = st.columns([1, 2, 1])
    with avatar_center:
        avatar_placeholder = st.empty()
        initial_image = get_jenbina_image_for_emotion(person)
        with avatar_placeholder.container():
            display_jenbina_image(initial_image, caption=f"{person.name}")

    # ==================================================================
    # Stage 2 — Perception & Context  (compute, render later)
    # ==================================================================

    # Needs Analysis (LLM call)
    print(f"{'─'*40}")
    print(f"  🧠 Stage 2: Perception & Context")
    print(f"{'─'*40}")
    update_system_stage("Analyzing needs...")
    print(f"  📊 [2a] Analyzing basic needs...")
    needs_response = create_basic_needs_chain(llm_json_mode, person.maslow_needs)
    print(f"  ✅ Needs analysis complete")
    _print_json("📊 Needs Response", needs_response)

    # Card 2: Context — world description LLM + working memory update → display
    update_system_stage("Generating world description...")
    print(f"  🌐 [2b] Generating world description...")
    prev_actions_list = []
    for record in st.session_state.get("simulation_history", [])[-6:]:
        action = (record.get("action_decision", {}) or {}).get("chosen_action")
        if action:
            prev_actions_list.append(action)
    recent_actions_str = "\n".join(f"- {a}" for a in prev_actions_list) or "None yet."
    world_chain = create_world_description_system(llm_json_mode)
    world_response = world_chain(person, world, recent_actions=recent_actions_str)
    print(f"  ✅ World description complete")
    _print_json("🌐 World Description", world_response)

    active_plan_step = None
    if person.planning_system is not None:
        result = person.planning_system.get_current_step()
        if result:
            _, step = result
            active_plan_step = {"description": step.description, "action_hint": step.action_hint}

    active_goals_data = []
    if person.goal_system is not None:
        goal_stats = person.goal_system.get_goal_stats()
        active_goals_data = goal_stats.get("goals", [])

    world_ctx_wm = {
        "location": world_summary.get("location", {}).get("name", ""),
        "time_of_day": world_summary.get("time", {}).get("time_of_day", ""),
        "weather": world_summary.get("weather", {}).get("description", ""),
    }

    needs_with_levels = {}
    for name, need in person.maslow_needs.needs.items():
        needs_with_levels[name] = {"satisfaction": need.satisfaction, "level": need.level.value}

    person.working_memory.update(
        needs=needs_with_levels,
        emotions=emotions_before,
        active_plan_step=active_plan_step,
        active_goals=active_goals_data,
        recent_experience=None,
        world_context=world_ctx_wm,
        sleep_satisfaction=person.maslow_needs.get_need_satisfaction("sleep"),
    )

    update_system_stage("Updating working memory...")
    print(f"  🧩 [2c] Updating working memory...")
    wm_text = person.working_memory.format_for_prompt()
    print(f"  ✅ Working memory updated")
    plan_text = person.planning_system.format_plan_for_prompt() if person.planning_system is not None else "No active plan."
    goals_text = person.goal_system.format_goals_for_prompt() if person.goal_system is not None else "No goals set yet."
    lessons_text = "No lessons learned yet."
    if person.learning_system is not None:
        lessons_text = person.learning_system.format_lessons_for_prompt(
            needs=needs_before, emotions=emotions_before
        )

    recent_actions = []
    for record in st.session_state.get("simulation_history", [])[-6:]:
        action = (record.get("action_decision", {}) or {}).get("chosen_action")
        if action:
            recent_actions.append(action)
    print(f"  📋 Recent actions for context ({len(recent_actions)}): {recent_actions}")

    curiosity_text = "Curiosity is low; prioritize practical actions."
    if getattr(person, "curiosity_system", None) is not None:
        available_actions = []
        try:
            world_data = json.loads(world_response) if isinstance(world_response, str) else {}
            available_actions = world_data.get("list_of_actions", []) if isinstance(world_data, dict) else []
        except Exception:
            available_actions = []

        person.curiosity_system.observe_cycle(
            needs=needs_before,
            world_context=world_ctx_wm,
            available_actions=available_actions,
            recent_actions=recent_actions,
        )
        curiosity_text = person.curiosity_system.format_for_prompt()

    inner_voice_text = "No inner thoughts at the moment."
    if person.inner_monologue is not None:
        update_system_stage("Generating inner monologue...")
        print(f"  🧠 [2d] Generating inner monologue...")
        recent_exp_list = None
        recent_exp_str = "No notable recent experiences."
        if person.learning_system is not None:
            stats = person.learning_system.get_learning_stats()
            recent_exp_list = stats.get("recent_experiences", [])
            if recent_exp_list:
                recent_exp_str = "\n".join(
                    f"- {e.get('action_taken', 'unknown')}: satisfaction "
                    f"{e.get('overall_satisfaction_before', 0):.0f}→{e.get('overall_satisfaction_after', 0):.0f}"
                    for e in recent_exp_list[-3:]
                )

        emotional_state_str = ", ".join(
            f"{name}: {val}" for name, val in emotions_before.items()
        )
        needs_summary_str = ", ".join(
            f"{name}: {sat:.0f}%" for name, sat in needs_before.items()
        )
        world_context_str = (
            f"Location: {world_summary.get('location', {}).get('name', 'Unknown')}, "
            f"Time: {world_summary.get('time', {}).get('time_of_day', 'unknown')}, "
            f"Weather: {world_summary.get('weather', {}).get('description', 'unknown')}"
        )

        last_action = "Nothing in particular."
        if st.session_state.get("simulation_history"):
            prev = st.session_state["simulation_history"][-1].get("action_decision", {})
            if isinstance(prev, dict):
                last_action = prev.get("chosen_action", last_action)

        person.inner_monologue.think(
            needs=needs_before,
            emotions=emotions_before,
            working_memory_str=wm_text,
            needs_summary_str=needs_summary_str,
            emotional_state_str=emotional_state_str,
            world_context_str=world_context_str,
            recent_action_str=last_action,
            recent_experiences_list=recent_exp_list,
            recent_experiences_str=recent_exp_str,
            lessons_learned_str=lessons_text,
            goals_str=goals_text,
        )
        inner_voice_text = person.inner_monologue.format_for_prompt()
        print(f"  ✅ Inner monologue generated")

    # Render Tamagotchi center panel: thought bubble, needs, emotions
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        if inner_voice_text != "No inner thoughts at the moment.":
            thought_display = inner_voice_text.split(".")[0] + "..." if "." in inner_voice_text else inner_voice_text
            st.markdown(f'<div class="thought-bubble">{thought_display}</div>', unsafe_allow_html=True)

        render_needs_bars(person)
        render_emotion_chips(person)

    # Card 3: Action Decision (LLM call → display)
    print(f"{'─'*40}")
    print(f"  ⚡ Stage 3: Action Decision")
    print(f"{'─'*40}")
    update_system_stage("Deciding next action...")
    print(f"  🤔 Running meta-cognitive action chain...")

    # Show thinking image while deciding
    with avatar_placeholder.container():
        display_jenbina_image(_get_image_path("jenbina_thinking.png"), caption=f"{person.name} is thinking...")

    action_response = create_meta_cognitive_action_chain(
        llm=llm_json_mode,
        person=person,
        world_description=world_response,
        meta_cognitive_system=meta_cognitive_system,
        world_state=world,
        recent_actions=recent_actions,
    )
    chosen = action_response.get('chosen_action', '?') if isinstance(action_response, dict) else str(action_response)[:50]
    print(f"  ✅ Action chosen: {chosen}")

    # Update avatar to reflect the chosen action (or fall back to emotion)
    action_image = get_jenbina_image_for_action(chosen)
    if action_image is None:
        action_image = get_jenbina_image_for_emotion(person)
    with avatar_placeholder.container():
        display_jenbina_image(action_image, caption=f"{person.name}: {chosen}")

    if getattr(person, "curiosity_system", None) is not None and isinstance(action_response, dict):
        person.curiosity_system.update_after_action(action_response.get("chosen_action", ""))
    _print_json("⚡ Action Response", action_response)

    # Apply action effects to needs via fuzzy matching
    action_executor = create_maslow_action_executor(person.maslow_needs)
    _action_key_map = {
        # Physiological
        "eat": "eat", "food": "eat", "cook": "eat", "meal": "eat",
        "breakfast": "eat", "lunch": "eat", "dinner": "eat", "kitchen": "eat", "snack": "eat",
        "drink": "drink", "water": "drink", "coffee": "drink", "tea": "drink",
        "sleep": "sleep", "nap": "sleep", "bed": "sleep",
        "rest": "rest", "relax": "rest", "sit": "rest", "lounge": "rest",
        "shelter": "find_shelter", "home": "find_shelter", "house": "find_shelter", "inside": "find_shelter",
        "health": "maintain_health", "exercise": "maintain_health", "walk": "maintain_health",
        "outside": "maintain_health", "courtyard": "maintain_health", "stroll": "maintain_health",
        "fresh air": "maintain_health", "stretch": "maintain_health", "garden": "maintain_health",
        "step out": "maintain_health",
        # Safety
        "safe": "find_safety", "security": "find_safety", "lock": "find_safety",
        "routine": "establish_routine", "plan": "establish_routine", "schedule": "establish_routine",
        "order": "create_order", "clean": "create_order", "organize": "create_order", "tidy": "create_order",
        "protect": "seek_protection", "check": "seek_protection",
        # Social
        "socialize": "socialize", "talk": "socialize", "chat": "socialize",
        "conversation": "socialize", "greet": "socialize", "visit": "socialize",
        "neighbor": "socialize", "call": "socialize",
        "friend": "make_friends",
        "love": "seek_love",
        "community": "join_community", "gather": "join_community", "market": "join_community",
        "relationship": "build_relationships",
        # Esteem
        "goal": "work_on_goals", "work": "work_on_goals", "task": "work_on_goals", "chore": "work_on_goals",
        "confidence": "build_confidence",
        "recognition": "seek_recognition",
        "skill": "develop_skills", "practice": "develop_skills", "study": "develop_skills", "train": "develop_skills",
        # Self-actualization
        "learn": "learn_new_things", "read": "learn_new_things", "book": "learn_new_things",
        "explor": "learn_new_things", "observ": "learn_new_things", "discover": "learn_new_things",
        "investigat": "learn_new_things", "inspect": "learn_new_things", "surround": "learn_new_things",
        "creative": "be_creative", "paint": "be_creative", "write": "be_creative", "art": "be_creative",
        "sing": "be_creative", "music": "be_creative", "draw": "be_creative",
        "purpose": "find_purpose", "pray": "find_purpose",
        "meaning": "explore_meaning", "reflect": "explore_meaning", "meditat": "explore_meaning",
        "think": "explore_meaning", "contemplate": "explore_meaning",
        "philosoph": "philosophical_exploration",
    }
    import re
    chosen_lower = chosen.lower()
    matched_action = None
    # Try word-boundary match first to avoid false positives (e.g. "rest" in "restaurant")
    for keyword, action_key in _action_key_map.items():
        if re.search(r'\b' + re.escape(keyword), chosen_lower):
            matched_action = action_key
            break
    if matched_action is None:
        # Fall back to substring match
        for keyword, action_key in _action_key_map.items():
            if keyword in chosen_lower:
                matched_action = action_key
                break
    if matched_action:
        effect_result = action_executor(matched_action)
        print(f"  🎯 Action effect applied: {matched_action} → satisfied {effect_result.get('satisfied_needs', {})}")
    else:
        print(f"  ⚠️  No need-satisfaction mapping for action: {chosen}")

    # Detect if the action moves Jenbina to a new location
    new_location = _detect_location_from_action(chosen)
    if new_location:
        old_location = st.session_state.get("jenbina_location", "Jenbina's House")
        if new_location != old_location:
            st.session_state["jenbina_location"] = new_location
            print(f"  📍 Location changed: {old_location} → {new_location}")

    # Action narrative placeholder — updated after post-processing with satisfaction delta
    _, action_center, _ = st.columns([1, 2, 1])
    with action_center:
        action_placeholder = st.empty()
        with action_placeholder.container():
            st.markdown(f"""
            <div class="action-card">
                <div class="action-title">▶ Jenbina decided to {chosen.lower()}</div>
            </div>
            """, unsafe_allow_html=True)

    # ==================================================================
    # Stage 4 — Checks & Analysis  (compute only, render in debug)
    # ==================================================================
    print(f"{'─'*40}")
    print(f"  🛡️  Stage 4: Checks & Analysis")
    print(f"{'─'*40}")
    update_system_stage("Running safety check...")
    print(f"  ⚖️  [4a] Running Asimov safety check...")
    asimov_chain = create_asimov_check_system(llm_json_mode)
    asimov_response = asimov_chain(action_response)
    print(f"  ✅ Safety check complete")
    _print_json("⚖️  Asimov Response", asimov_response)

    print(f"  🔍 [4b] Analyzing state changes...")
    state_response = create_state_analysis_system(
        llm_json_mode,
        action_decision=action_response,
        compliance_check=asimov_response
    )
    print(f"  ✅ State analysis complete")
    _print_json("🔍 State Analysis", state_response)

    update_system_stage("Analyzing emotional impact...")
    print(f"  💭 [4c] Analyzing emotional impact...")
    action_situation = f"Action taken: {action_response.get('chosen_action', 'unknown')}. Reasoning: {action_response.get('reasoning', '')}"
    emotion_adjustments = analyze_emotion_impact(
        llm=llm_json_mode,
        situation=action_situation,
        emotion_system=person.emotion_system,
        maslow_needs=person.maslow_needs,
    )
    if emotion_adjustments:
        person.emotion_system.apply_adjustments(emotion_adjustments)
        print(f"  ✅ Emotions: " + ", ".join(f"{k}: {v:+.0f}" for k, v in emotion_adjustments.items()))
        _print_json("💭 Emotion Adjustments", emotion_adjustments)
    else:
        print(f"  ✅ No significant emotional changes")

    # ==================================================================
    # Post-processing: needs update, experience recording, goals, plans
    # ==================================================================
    print(f"{'─'*40}")
    print(f"  📝 Stage 5: Learning & Updates")
    print(f"{'─'*40}")
    update_system_stage("Learning & updating...")
    print(f"  🔄 Updating needs & decaying emotions...")
    person.update_all_needs()

    needs_after = person.get_needs_snapshot()
    emotions_after = person.get_emotions_snapshot()
    satisfaction_after = person.maslow_needs.get_overall_satisfaction()
    sat_delta = satisfaction_after - satisfaction_before
    chosen_action = action_response.get("chosen_action", "unknown") if isinstance(action_response, dict) else str(action_response)
    reasoning = action_response.get("reasoning", "") if isinstance(action_response, dict) else ""
    world_ctx = {
        "location": world_summary.get("location", {}).get("name", "unknown"),
        "time_of_day": world_summary.get("time", {}).get("time_of_day", "unknown"),
        "weather": world_summary.get("weather", {}).get("description", "unknown"),
    }

    learning_messages = []
    goal_messages = []
    plan_messages = []
    lesson_stats = {}
    experience = None

    if person.learning_system is not None:
        print(f"  📓 Recording experience...")
        experience = person.learning_system.record_experience(
            action_taken=chosen_action,
            action_reasoning=reasoning,
            needs_before=needs_before,
            needs_after=needs_after,
            emotions_before=emotions_before,
            emotions_after=emotions_after,
            world_context=world_ctx,
            overall_satisfaction_before=satisfaction_before,
            overall_satisfaction_after=satisfaction_after,
        )

        delta_icon = "📈" if sat_delta >= 0 else "📉"
        learning_messages.append(f"{delta_icon} Satisfaction: {satisfaction_before:.1f}% → {satisfaction_after:.1f}% ({sat_delta:+.1f}%)")
        stats = person.learning_system.get_learning_stats()
        learning_messages.append(f"📚 Active lessons: {stats['active_lessons']} | Total experiences: {stats['total_experiences']}")
        print(f"  {delta_icon} Satisfaction: {satisfaction_before:.1f}% → {satisfaction_after:.1f}% ({sat_delta:+.1f}%)")
        print(f"  📚 Lessons: {stats['active_lessons']} active | {stats['total_experiences']} total experiences")

        if person.goal_system is not None:
            print(f"  🎯 Updating goal progress...")
            person.goal_system.set_experiences(person.learning_system.experiences)
            advanced_goals = person.goal_system.update_progress(experience)
            if advanced_goals:
                for g in advanced_goals:
                    goal_messages.append(f"🎯 {g.description} → {g.progress:.0%}")
                    print(f"  🎯 Goal advanced: {g.description} → {g.progress:.0%}")

            if person.goal_system.should_generate():
                person.goal_system.reset_generation_counter()
                needs_dict = {name: need.satisfaction for name, need in person.maslow_needs.needs.items()}
                emotions_dict = person.get_emotions_snapshot()
                personality = person.maslow_needs.personality_traits
                lesson_stats = person.learning_system.get_learning_stats()
                person.goal_system.generate_goals(
                    needs=needs_dict,
                    emotions=emotions_dict,
                    personality_traits=personality,
                    lessons=lesson_stats.get("lessons", []),
                )

        if person.planning_system is not None:
            print(f"  📋 Evaluating plan progress...")
            step_result = person.planning_system.evaluate_step(experience)
            if step_result == "step_completed":
                plan_messages.append("📋 Plan step completed!")
                current = person.planning_system.get_current_step()
                if current:
                    _, next_step = current
                    plan_messages.append(f"Next step: {next_step.description}")
                else:
                    for p in person.planning_system.plans:
                        if p.status == "completed" and p.goal_id is not None:
                            plan_messages.append(f"📋 Plan completed: {p.goal_description}")
                            if person.goal_system is not None:
                                for g in person.goal_system.goals:
                                    if g.description == p.goal_description and g.is_active():
                                        g.advance(0.3)
                                        break
            elif step_result == "step_overridden":
                plan_messages.append("📋 Plan step overridden by urgent needs.")

            replan_result = person.planning_system.check_for_replan(
                needs=needs_after, world_context=world_ctx,
            )
            if replan_result is not None:
                plan_messages.append(f"📋 Replanned: {replan_result.goal_description}")
                plan_messages.append(f"New first step: {replan_result.steps[0].description}")

            if person.goal_system is not None:
                for idx, goal in enumerate(person.goal_system.goals):
                    if not goal.is_active():
                        continue
                    if person.planning_system.get_plan_for_goal(idx) is not None:
                        continue
                    should_plan = goal.horizon == "short_term"
                    if not should_plan:
                        low_source = any(
                            needs_after.get(n, 100) < 50
                            for n in goal.source_needs
                        )
                        should_plan = low_source
                    if should_plan:
                        person.planning_system.create_plan(
                            goal_description=goal.description,
                            goal_id=idx,
                            needs=needs_after,
                            emotions=emotions_after,
                            world_context=world_ctx,
                            lessons=lesson_stats.get("lessons", []),
                        )

    # Keep identity updates independent of learning-system availability
    if getattr(person, "self_narrative", None) is not None:
        if experience is None:
            experience = SimpleNamespace(
                action_taken=chosen_action,
                action_reasoning=reasoning,
                overall_satisfaction_before=satisfaction_before,
                overall_satisfaction_after=satisfaction_after,
                timestamp=time.time(),
            )
            lessons_for_identity = []
        else:
            lessons_for_identity = person.learning_system.lessons if person.learning_system is not None else []
        person.self_narrative.integrate_experience(experience, lessons_for_identity)

    # ==================================================================
    # Update action narrative with final satisfaction delta
    # ==================================================================
    with action_placeholder.container():
        render_action_narrative(action_response, satisfaction_before, satisfaction_after)

    # Final avatar update — reflect post-action emotional state
    final_image = get_jenbina_image_for_emotion(person)
    with avatar_placeholder.container():
        display_jenbina_image(final_image, caption=f"{person.name}")

    # ==================================================================
    # Tier 2 — Auto-expanding sections (interesting content only)
    # ==================================================================
    _, tier2_center, _ = st.columns([1, 2, 1])
    with tier2_center:
        # Learning
        with st.container(border=True):
            st.caption("📚 Learning")
            for msg in learning_messages:
                st.write(msg)
            if not learning_messages:
                st.write("*No learning updates.*")
            if goal_messages:
                st.caption("Goals Advanced")
                for msg in goal_messages:
                    st.write(msg)
            if plan_messages:
                st.caption("Plan Updates")
                for msg in plan_messages:
                    st.write(msg)

        # Goals
        if person.goal_system is not None:
            with st.container(border=True):
                st.caption("🎯 Goals")
                display_goal_stats(person, iteration)

        # Plans
        if person.planning_system is not None:
            with st.container(border=True):
                st.caption("📋 Plans")
                display_planning_stats(person, iteration)

        # Curiosity
        if getattr(person, "curiosity_system", None) is not None:
            with st.container(border=True):
                st.caption("🔎 Curiosity")
                display_curiosity_stats(person, iteration)

    # ==================================================================
    # Tier 3 — Debug details (always collapsed)
    # ==================================================================
    with st.container(border=True):
        st.caption("🔧 Debug Details")
        st.caption("Needs Analysis")
        st.json(needs_response if isinstance(needs_response, dict) else {"raw": str(needs_response)})
        st.caption("World Description")
        st.json({"raw": str(world_response)[:2000]} if not isinstance(world_response, dict) else world_response)
        st.caption("Action Decision")
        st.json(action_response if isinstance(action_response, dict) else {"raw": str(action_response)})
        # Chain of thought
        trace = action_response.get("reasoning_trace", []) if isinstance(action_response, dict) else []
        if trace:
            st.caption("Chain of Thought")
            step_labels = {"assess": "Assess", "deliberate": "Deliberate", "decide": "Decide"}
            for entry in trace:
                if isinstance(entry, dict):
                    label = step_labels.get(entry.get("step", ""), entry.get("step", ""))
                    st.write(f"**{label}:**")
                    output = entry.get("output", entry)
                    st.json(output)
                else:
                    st.write(str(entry))
        st.caption("Safety Check")
        st.json(asimov_response if isinstance(asimov_response, dict) else {"raw": str(asimov_response)})
        st.caption("State Analysis")
        st.json(state_response if isinstance(state_response, dict) else {"raw": str(state_response)})
        if emotion_adjustments:
            st.caption("Emotion Adjustments")
            st.json(emotion_adjustments)
        display_meta_cognitive_insights(meta_cognitive_system, iteration)
        display_working_memory_stats(person, iteration)
        display_identity_stats(person, iteration)
        display_learning_stats(person, iteration)
        st.caption("Person State")
        st.json(person_dict)
        st.caption("World State")
        st.json(world_summary)

    # Check if Jenbina wants to say something proactively
    try:
        llm = st.session_state.get("_proactive_llm")
        if llm is None:
            from core.connect import get_llm
            llm = get_llm(provider="openai", temperature=1)
            st.session_state._proactive_llm = llm
        send_proactive_message(person, llm)
    except Exception as e:
        print(f"  Proactive message check failed: {e}")

    iteration_duration = (datetime.now() - iteration_start_time).total_seconds()
    print(f"{'='*60}")
    print(f"  ✅ ITERATION {iter_num} COMPLETE — {iteration_duration:.2f}s")
    print(f"{'='*60}")
    update_system_stage(f"Iteration {iter_num} complete ({iteration_duration:.1f}s)")
    st.success(f"Iteration {iter_num} completed in {iteration_duration:.2f}s")

    return {
        "needs_response": needs_response,
        "world_description": world_response,
        "action_decision": action_response,
        "state_response": state_response,
        "person_dict": person_dict,
        "world_summary": world_summary,
        "iteration_duration": iteration_duration,
        "satisfaction_delta": sat_delta,
    }


def run_simulation_loop(person, llm_json_mode, meta_cognitive_system, iterations, delay_seconds):
    """Run the simulation loop for specified iterations"""
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Container for all iterations
    iterations_container = st.container()
    
    results = []
    
    for iteration in range(iterations):
        # Update progress
        progress = (iteration + 1) / iterations
        progress_bar.progress(progress)
        status_text.text(f"🔄 Running iteration {iteration + 1} of {iterations}...")
        
        with iterations_container:
            # Create expander for each iteration
            with st.expander(f"📍 Iteration {iteration + 1} of {iterations}", expanded=(iteration == iterations - 1)):
                result = run_single_iteration(person, llm_json_mode, meta_cognitive_system, iteration)

                # Store iteration record and immediately update session
                # history so the NEXT iteration sees this action in
                # recent_actions / last_action prompts.
                iteration_record = {
                    "iteration": iteration + 1,
                    "timestamp": datetime.now().isoformat(),
                    "duration_seconds": result["iteration_duration"],
                    "action_decision": result["action_decision"],
                    "needs_state": result["person_dict"]["maslow_needs"],
                    "emotions_state": result["person_dict"].get("emotions", {}),
                    "world_summary": result["world_summary"]
                }
                results.append(iteration_record)
                # Push to session history immediately so next iteration
                # can read recent actions from it.
                if "simulation_history" not in st.session_state:
                    st.session_state.simulation_history = []
                st.session_state.simulation_history.append(iteration_record)

        # Wait before next iteration (except for the last one)
        if iteration < iterations - 1:
            status_text.text(f"⏳ Waiting {delay_seconds} seconds before next iteration...")
            time.sleep(delay_seconds)
    
    # Simulation completed
    progress_bar.progress(1.0)
    status_text.text(f"✅ Simulation completed! Ran {iterations} iteration(s).")
    
    return results


def display_simulation_summary(simulation_history, iterations, person=None):
    """Display summary of simulation history"""
    st.success(f"🎉 Completed {iterations} simulation cycles!")
    
    if len(simulation_history) > 0:
        with st.expander("📊 Simulation History Summary", expanded=True):
            st.write(f"**Total Iterations:** {len(simulation_history)}")
            
            # Show action decisions across iterations
            st.write("**Action Decisions:**")
            for record in simulation_history[-iterations:]:
                action = record.get("action_decision", {})
                if isinstance(action, dict):
                    chosen = action.get("chosen_action", "Unknown")
                    lessons_applied = action.get("lessons_applied", "")
                else:
                    chosen = str(action)[:100]
                    lessons_applied = ""
                
                delta = record.get("satisfaction_delta", 0)
                delta_icon = "📈" if delta >= 0 else "📉"
                st.write(f"- Iteration {record['iteration']}: {chosen} {delta_icon} ({delta:+.1f}%)")
                if lessons_applied:
                    st.write(f"  *Lessons applied: {lessons_applied}*")
            
            # Show needs evolution
            st.write("**Needs Evolution:**")
            for record in simulation_history[-iterations:]:
                needs = record.get("needs_state", {})
                overall = needs.get("overall_satisfaction", 0)
                st.write(f"- Iteration {record['iteration']}: Overall Satisfaction {overall:.1f}%")
            
            # Show learning summary
            if person is not None and person.learning_system is not None:
                stats = person.learning_system.get_learning_stats()
                st.write("---")
                st.write(f"**📚 Learning Summary:**")
                st.write(f"- Total experiences recorded: {stats['total_experiences']}")
                st.write(f"- Active lessons: {stats['active_lessons']}")
                
                if stats['lessons']:
                    st.write("**Learned Lessons:**")
                    for lesson in stats['lessons']:
                        st.write(f"- **{lesson['description']}** (confidence: {lesson['confidence']:.0%}, confirmed {lesson['times_confirmed']}x)")

            if person is not None and person.goal_system is not None:
                goal_stats = person.goal_system.get_goal_stats()
                st.write(f"**🎯 Goal Summary:**")
                st.write(f"- Active goals: {goal_stats['active_goals']}")
                st.write(f"- Completed goals: {goal_stats['completed_goals']}")
                st.write(f"- Abandoned goals: {goal_stats['abandoned_goals']}")
                if goal_stats['goals']:
                    st.write("**Active Goals:**")
                    for goal in goal_stats['goals']:
                        st.write(f"- [{goal['horizon']}] **{goal['description']}** (progress: {goal['progress']:.0%}, confidence: {goal['confidence']:.0%})")

            if person is not None and person.planning_system is not None:
                plan_stats = person.planning_system.get_planning_stats()
                st.write(f"**📋 Planning Summary:**")
                st.write(f"- Active plans: {plan_stats['active_plans']}")
                st.write(f"- Completed plans: {plan_stats['completed_plans']}")
                st.write(f"- Failed plans: {plan_stats['failed_plans']}")
                if plan_stats['plans']:
                    st.write("**Active Plans:**")
                    for p in plan_stats['plans']:
                        steps = p.get('steps', [])
                        done = len([s for s in steps if s['status'] == 'completed'])
                        st.write(f"- **{p['goal_description']}** ({done}/{len(steps)} steps done, replanned {p.get('times_replanned', 0)}x)")


def render_simulation_controls():
    """Render simulation control UI and return settings (designed for sidebar)"""
    st.markdown("### Simulation Controls")
    num_iterations = st.number_input("Iterations", min_value=1, max_value=20, value=5, step=1)
    delay_seconds = st.number_input("Delay (seconds)", min_value=1, max_value=60, value=3, step=1)
    run_loop = st.button("🔄 Run Simulation Loop", type="primary", use_container_width=True)
    single_run = st.button("▶️ Run Single Iteration", use_container_width=True)

    return {
        "num_iterations": num_iterations,
        "delay_seconds": delay_seconds,
        "run_loop": run_loop,
        "single_run": single_run
    }
