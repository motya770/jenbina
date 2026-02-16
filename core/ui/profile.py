"""Profile UI component — Jenbina's profile page with embedded chat."""
import streamlit as st
from core.ui.simulation import (
    get_jenbina_image_for_emotion,
    display_jenbina_image,
    render_needs_bars,
    render_emotion_chips,
    inject_tamagotchi_css,
)
from core.ui.chat import (
    handle_user_input,
    display_communication_stats,
    display_conversation_history,
    display_social_model,
    display_memory_stats,
    display_memory_debug,
)


def _render_inner_monologue(person):
    """Show Jenbina's current inner thought."""
    monologue = getattr(person, "inner_monologue", None)
    if monologue is None:
        return

    thought = monologue.get_current_thought()
    if thought is None:
        st.caption("*Mind is quiet...*")
        return

    mode_icons = {
        "deliberation": "🤔",
        "rumination": "🔄",
        "worry": "😟",
        "daydreaming": "💭",
    }
    icon = mode_icons.get(thought.mode, "💭")

    st.markdown(
        f'<div style="background:#FFF3EC;border-radius:12px;padding:12px 16px;'
        f'border-left:4px solid #FFD7BA;margin-bottom:8px;">'
        f'<span style="font-size:0.85em;color:#B08968;font-weight:600;">'
        f'{icon} {thought.mode.capitalize()} · {thought.emotional_tone}</span><br>'
        f'<span style="color:#5C4033;font-style:italic;">"{thought.content}"</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_learning_summary(person):
    """Show active lessons from the learning system."""
    learning = getattr(person, "learning_system", None)
    if learning is None:
        return

    stats = learning.get_learning_stats()
    active = stats.get("lessons", [])
    total_exp = stats.get("total_experiences", 0)

    st.markdown(f"**Experiences:** {total_exp} | **Active lessons:** {len(active)}")

    if active:
        for lesson in active[:5]:
            confidence = lesson.get("confidence", 0)
            bar_pct = max(0, min(100, confidence * 100))
            st.markdown(
                f'<div style="background:#F0FFF0;border-radius:8px;padding:8px 12px;'
                f'margin-bottom:4px;border-left:3px solid #6BCB77;">'
                f'<span style="font-size:0.8em;color:#888;">[{lesson.get("category", "?")}]</span> '
                f'{lesson.get("description", "")}'
                f'<div style="background:#E0E0E0;border-radius:4px;height:4px;margin-top:4px;">'
                f'<div style="background:#6BCB77;width:{bar_pct}%;height:100%;border-radius:4px;"></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("No lessons learned yet.")


def _render_working_memory(person):
    """Show current working memory buffer."""
    wm = getattr(person, "working_memory", None)
    if wm is None:
        return

    stats = wm.get_stats()
    items = stats.get("items", [])
    focus = stats.get("focus", 0)
    capacity = stats.get("capacity", 0)
    buf_size = stats.get("buffer_size", 0)

    st.markdown(f"**Focus:** {focus:.0f}% | **Slots:** {buf_size}/{capacity}")

    if items:
        for item in items[:5]:
            salience = item.get("salience", 0)
            source = item.get("source", "")
            content = item.get("content", "")
            st.markdown(
                f'<div style="background:#F0F0FF;border-radius:8px;padding:6px 10px;'
                f'margin-bottom:3px;font-size:0.9em;">'
                f'<span style="color:#888;">[{source}]</span> {content} '
                f'<span style="color:#aaa;font-size:0.8em;">(salience: {salience:.2f})</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("Mind is clear.")


def _render_identity_summary(person):
    """Show self-narrative / identity summary."""
    narrative = getattr(person, "self_narrative", None)
    if narrative is None:
        return

    coherence = getattr(narrative, "identity_coherence", 0)
    values = getattr(narrative, "values", {})
    self_concept = getattr(narrative, "self_concept", [])

    st.markdown(f"**Identity coherence:** {coherence:.0%}")

    if values:
        top_values = sorted(values.items(), key=lambda kv: kv[1], reverse=True)[:5]
        vals_str = " | ".join(f"{name}: {score:.1f}" for name, score in top_values)
        st.markdown(f"**Values:** {vals_str}")

    if self_concept:
        for concept in self_concept[-3:]:
            st.caption(f'"{concept}"')


def render_profile_page(person, llm, memory_manager, debug_mode):
    """Render the full Jenbina profile page with embedded chat."""

    # ── Profile header: avatar + state ──────────────────────────────
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        image_path = get_jenbina_image_for_emotion(person)
        display_jenbina_image(image_path, caption=person.name)

    # Needs & emotions under the avatar
    render_needs_bars(person)
    render_emotion_chips(person)

    st.markdown("---")

    # ── Inner monologue ─────────────────────────────────────────────
    st.subheader("Inner Thoughts")
    _render_inner_monologue(person)

    st.markdown("---")

    # ── Chat ────────────────────────────────────────────────────────
    st.subheader("Chat")
    handle_user_input(person, llm, memory_manager, debug_mode)

    # ── Collapsible detail sections ─────────────────────────────────
    with st.expander("Learning", expanded=False):
        _render_learning_summary(person)

    with st.expander("Working Memory", expanded=False):
        _render_working_memory(person)

    with st.expander("Identity", expanded=False):
        _render_identity_summary(person)

    display_social_model(person)
    display_communication_stats(person)
    display_conversation_history(person)
    display_memory_stats(memory_manager)

    if debug_mode:
        display_memory_debug(memory_manager)
