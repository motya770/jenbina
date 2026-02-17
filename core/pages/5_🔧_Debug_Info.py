"""Jenbina — Debug Info page."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from core.ui.shared_init import require_auth

st.set_page_config(page_title="Jenbina — Debug Info", page_icon="🔧", layout="wide")

if not require_auth():
    st.stop()

nav1, nav2, nav3, nav4, nav5 = st.columns(5)
with nav1:
    st.page_link("app.py", label="👧 Simulation", icon="👧")
with nav2:
    st.page_link("pages/2_💬_Chat.py", label="💬 Chat", icon="💬")
with nav3:
    st.page_link("pages/3_🌍_Environment.py", label="🌍 Environment", icon="🌍")
with nav4:
    st.page_link("pages/4_📋_Console.py", label="📋 Console", icon="📋")
with nav5:
    st.page_link("pages/5_🔧_Debug_Info.py", label="🔧 Debug Info", icon="🔧")

st.title("🔧 Debug Info")

iterations = st.session_state.get("debug_iterations", [])

if not iterations:
    st.info("No debug data yet. Run a simulation to see debug info here.")
    st.stop()

# Iteration selector
iteration_labels = [f"Iteration {d['iteration']} — {d['timestamp']}" for d in iterations]
selected_idx = st.selectbox(
    "Select iteration",
    range(len(iterations)),
    index=len(iterations) - 1,
    format_func=lambda i: iteration_labels[i],
)

data = iterations[selected_idx]

st.caption("Needs Analysis")
needs = data["needs_response"]
st.json(needs if isinstance(needs, dict) else {"raw": str(needs)})

st.caption("World Description")
world_resp = data["world_response"]
st.json(world_resp if isinstance(world_resp, dict) else {"raw": str(world_resp)[:2000]})

st.caption("Action Decision")
action = data["action_response"]
st.json(action if isinstance(action, dict) else {"raw": str(action)})

# Chain of thought
trace = action.get("reasoning_trace", []) if isinstance(action, dict) else []
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
asimov = data["asimov_response"]
st.json(asimov if isinstance(asimov, dict) else {"raw": str(asimov)})

st.caption("State Analysis")
state = data["state_response"]
st.json(state if isinstance(state, dict) else {"raw": str(state)})

if data.get("emotion_adjustments"):
    st.caption("Emotion Adjustments")
    st.json(data["emotion_adjustments"])

# Meta-cognitive insights
meta = data.get("meta_cognitive_stats")
if meta:
    with st.container(border=True):
        st.caption("🧠 Meta-Cognitive Insights")
        st.write(f"**Total Cognitive Processes:** {meta['total_processes']}")
        st.write(f"**Total Insights:** {meta['total_insights']}")
        st.write("**Cognitive Biases Detected:**")
        for bias, level in meta['cognitive_biases'].items():
            if level > 0:
                st.write(f"- {bias}: {level:.2f}")
        if meta.get('recent_insights'):
            st.write("**Recent Insights:**")
            for insight in meta['recent_insights']:
                st.write(f"- **{insight['type']}**: {insight['description']}")

# Working memory
wm = data.get("working_memory_stats")
if wm:
    with st.container(border=True):
        st.caption("🧠 Working Memory")
        st.write(f"**Focus:** {wm['focus']:.0f}% | **Capacity:** {wm['buffer_size']}/{wm['capacity']} | **Context Switches:** {wm['context_switches']}")
        if wm.get('items'):
            for item in wm['items']:
                bar_len = int(item['salience'] * 10)
                bar = "█" * bar_len + "░" * (10 - bar_len)
                st.write(f"- [{item['source']}] {item['content']} | {bar} {item['salience']:.2f}")
        else:
            st.write("*Mind is clear.*")

# Identity
identity = data.get("identity_stats")
if identity:
    with st.container(border=True):
        st.caption("🪞 Identity & Narrative")
        st.write(f"**Coherence:** {identity['identity_coherence']:.2f} | **Crisis:** {identity['identity_crisis_level']:.2f}")
        st.write("**Self Concept:**")
        for line in identity.get("self_concept", [])[:3]:
            st.write(f"- {line}")
        st.write("**Life Story:**")
        st.write(identity.get("life_story", ""))
        values = identity.get("values", {})
        if values:
            top = sorted(values.items(), key=lambda kv: kv[1], reverse=True)[:5]
            st.write("**Top Values:**")
            for name, score in top:
                st.write(f"- {name}: {score:.2f}")

# Learning stats
learning = data.get("learning_stats")
if learning:
    with st.container(border=True):
        st.caption("📚 Learning Stats")
        st.write(f"**Total Experiences:** {learning['total_experiences']}")
        st.write(f"**Active Lessons:** {learning['active_lessons']} / {learning['total_lessons']}")
        if learning.get('lessons'):
            st.write("**Learned Lessons:**")
            for lesson in learning['lessons']:
                confidence_bar = "█" * int(lesson['confidence'] * 10) + "░" * (10 - int(lesson['confidence'] * 10))
                st.write(
                    f"- [{lesson['category']}] {lesson['description']}\n"
                    f"  Confidence: {confidence_bar} {lesson['confidence']:.0%} | "
                    f"Confirmed: {lesson['times_confirmed']}x | "
                    f"Action: {lesson['recommended_action']}"
                )
        else:
            st.write("*No lessons learned yet.*")

st.caption("Person State")
st.json(data["person_dict"])

st.caption("World State")
st.json(data["world_summary"])
