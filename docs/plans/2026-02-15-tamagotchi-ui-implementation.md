# Tamagotchi UI Redesign — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the Jenbina simulation UI from a data-dump grid into a focused, playful Tamagotchi-style screen.

**Architecture:** Pure CSS/HTML injection via `st.markdown(unsafe_allow_html=True)` layered on top of Streamlit. All rendering helpers live in `core/ui/simulation.py`. The computation flow in `run_single_iteration()` stays identical — only the rendering sections change.

**Tech Stack:** Streamlit 1.38, custom CSS, HTML via `st.markdown()`

**Design doc:** `docs/plans/2026-02-15-tamagotchi-ui-redesign.md`

---

### Task 1: Add CSS injection function

**Files:**
- Modify: `core/ui/simulation.py:1-18` (add import, new function at top)

**Step 1: Add `inject_tamagotchi_css()` function**

Add this function after the imports (before `IMAGES_DIR`). It injects all custom styles once per page load via `st.markdown`.

```python
def inject_tamagotchi_css():
    """Inject Tamagotchi-themed CSS. Call once at the start of each page render."""
    st.markdown("""
    <style>
    /* Tamagotchi Theme */
    .stApp {
        background-color: #FFF8F0;
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
```

**Step 2: Verify CSS renders**

Temporarily add `inject_tamagotchi_css()` at the top of `run_single_iteration()` (first line after the docstring), then run the app and confirm the background changes to cream `#FFF8F0`.

Run: `cd /Users/wizard/Desktop/programming/projects/jenbina && python -c "import streamlit; print('Streamlit', streamlit.__version__)"`
Expected: Streamlit 1.38.0 (confirms version supports unsafe_allow_html)

**Step 3: Commit**

```bash
git add core/ui/simulation.py
git commit -m "feat(ui): add Tamagotchi CSS injection function"
```

---

### Task 2: Add rendering helper functions

**Files:**
- Modify: `core/ui/simulation.py` (add 4 new functions after `display_jenbina_image`, before `get_person_dict`)

**Step 1: Add `render_environment_ribbon()`**

```python
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
```

**Step 2: Add `render_needs_bars()`**

```python
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

        # Color gradient: red → yellow → green
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
```

**Step 3: Add `render_emotion_chips()`**

```python
def render_emotion_chips(person):
    """Render top emotions as colored pill chips."""
    emotion_icons = {
        "joy": "😊", "sadness": "😢", "anger": "😠", "fear": "😨",
        "surprise": "😮", "disgust": "🤢", "trust": "🤝", "anticipation": "🤩",
    }

    all_emotions = person.emotion_system.get_emotional_state_summary().get("emotions", {})
    # Filter to emotions with intensity > 15 and sort by intensity
    visible = sorted(
        [(name, val) for name, val in all_emotions.items() if val > 15],
        key=lambda x: x[1],
        reverse=True,
    )[:4]  # Show top 4 max

    if not visible:
        return

    chips_html = '<div class="emotion-chips">'
    for name, intensity in visible:
        icon = emotion_icons.get(name.lower(), "💭")
        chips_html += f'<span class="emotion-chip">{icon} {name.capitalize()} ({intensity:.0f})</span>'
    chips_html += "</div>"

    st.markdown(chips_html, unsafe_allow_html=True)
```

**Step 4: Add `render_action_narrative()`**

```python
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
```

**Step 5: Commit**

```bash
git add core/ui/simulation.py
git commit -m "feat(ui): add Tamagotchi rendering helpers (ribbon, bars, chips, narrative)"
```

---

### Task 3: Refactor `run_single_iteration()` layout

This is the core change. Replace the grid-based rendering with the Tamagotchi layout. The computation flow stays identical — only the `with r1c1:`, `with r2c1:`, etc. rendering blocks change.

**Files:**
- Modify: `core/ui/simulation.py:328-817` (the `run_single_iteration` function)

**Step 1: Replace the environment rendering section (lines 360-379)**

Replace the `avatar_col, env_col = st.columns([1, 2])` block and everything inside it with:

```python
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
```

Also update `display_jenbina_image` to use 350px width (change the function at line 74).

**Step 2: Replace Needs Analysis rendering (lines 394-396)**

Replace:
```python
    with r1c1:
        with _card("Needs Analysis"):
            st.write(needs_response)
```
With: (remove entirely — needs are already visible as bars, raw response goes to debug)

**Step 3: Replace the Context rendering (lines 520-539)**

After inner monologue is generated, instead of rendering in `r1c2`, render the thought bubble and needs/emotions centrally:

```python
    # Inner monologue thought bubble
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        if inner_voice_text != "No inner thoughts at the moment.":
            # Extract just the first sentence/thought for the bubble
            thought_display = inner_voice_text.split(".")[0] + "..." if "." in inner_voice_text else inner_voice_text
            st.markdown(f'<div class="thought-bubble">{thought_display}</div>', unsafe_allow_html=True)

        # Needs bars
        render_needs_bars(person)

        # Emotion chips
        render_emotion_chips(person)
```

**Step 4: Replace the Action Decision rendering (lines 571-588)**

Replace the `with r1c3:` block with the narrative card. The action narrative needs `satisfaction_after` which isn't available yet at this point, so we use a placeholder that gets filled after post-processing:

```python
    # Action narrative placeholder — filled after post-processing computes satisfaction_after
    _, action_center, _ = st.columns([1, 2, 1])
    with action_center:
        action_placeholder = st.empty()
        # Temporary display while computing
        with action_placeholder.container():
            st.markdown(f"""
            <div class="action-card">
                <div class="action-title">▶ Jenbina decided to {chosen.lower()}</div>
            </div>
            """, unsafe_allow_html=True)
```

**Step 5: Replace Checks & Analysis rendering (lines 593-641)**

Replace the 3-column `r2c1, r2c2, r2c3` grid. Safety check, state analysis, and emotion changes become hidden in a debug expander:

```python
    # Safety, State Analysis, Emotions — compute same as before, render in debug
    # (computation code stays identical, only rendering changes)
```

After the emotion adjustments are computed, instead of rendering in `r2c3`, just skip visible rendering.

**Step 6: Replace Learning row (lines 782-798) and stat displays (lines 800-806)**

After post-processing completes and `satisfaction_after` is known, update the action narrative placeholder:

```python
    # Update action narrative with final satisfaction delta
    with action_placeholder.container():
        render_action_narrative(action_response, satisfaction_before, satisfaction_after)

    # Tier 2: Auto-expanding sections
    _, tier2_center, _ = st.columns([1, 2, 1])
    with tier2_center:
        # Learning — auto-expand if new lesson or big delta
        has_new_learning = bool(learning_messages) and abs(sat_delta) > 5
        with st.expander("📚 Learning", expanded=has_new_learning):
            for msg in learning_messages:
                st.write(msg)
            if goal_messages:
                for msg in goal_messages:
                    st.write(msg)
            if plan_messages:
                for msg in plan_messages:
                    st.write(msg)

        # Goals — auto-expand if advanced
        if person.goal_system is not None:
            has_goal_updates = bool(goal_messages)
            with st.expander("🎯 Goals", expanded=has_goal_updates):
                display_goal_stats(person, iteration)

        # Plans — auto-expand if step completed
        if person.planning_system is not None:
            has_plan_updates = bool(plan_messages)
            with st.expander("📋 Plans", expanded=has_plan_updates):
                display_planning_stats(person, iteration)

        # Curiosity — auto-expand if exploring
        if getattr(person, "curiosity_system", None) is not None:
            should_explore = person.curiosity_system.get_stats().get("should_explore", False)
            with st.expander("🔎 Curiosity", expanded=should_explore):
                display_curiosity_stats(person, iteration)

    # Tier 3: Debug details (always collapsed)
    with st.expander("🔧 Debug Details", expanded=False):
        st.json({"needs_response": needs_response})
        st.json({"world_description": world_response})
        st.json({"action_decision": action_response})
        st.json({"safety_check": asimov_response})
        st.json({"state_analysis": state_response})
        if emotion_adjustments:
            st.json({"emotion_adjustments": emotion_adjustments})
        st.caption("Chain of Thought")
        trace = action_response.get("reasoning_trace", []) if isinstance(action_response, dict) else []
        for entry in trace:
            if isinstance(entry, dict):
                st.json(entry)
        display_meta_cognitive_insights(meta_cognitive_system, iteration)
        display_working_memory_stats(person, iteration)
        display_identity_stats(person, iteration)
        display_learning_stats(person, iteration)
        st.caption("Person State")
        st.json(person_dict)
        st.caption("World State")
        st.json(world_summary)
```

**Step 7: Remove the `r1c1, r1c2, r1c3 = st.columns(3)` and `r2c1, r2c2, r2c3 = st.columns(3)` column definitions**

These are no longer needed since we switched to centered single-column layout.

**Step 8: Commit**

```bash
git add core/ui/simulation.py
git commit -m "feat(ui): refactor simulation to Tamagotchi single-column layout"
```

---

### Task 4: Update `display_jenbina_image()` and `display_simulation_summary()`

**Files:**
- Modify: `core/ui/simulation.py:71-79` (`display_jenbina_image`)
- Modify: `core/ui/simulation.py:877-945` (`display_simulation_summary`)

**Step 1: Update image size to 350px**

Change `width=250` to `width=350` in both `st.image()` calls in `display_jenbina_image()`.

**Step 2: Update `display_simulation_summary()` to narrative style**

Replace the list of `st.write()` calls with a narrative summary using the action card style. For each iteration, render a mini action card instead of a bullet point.

**Step 3: Commit**

```bash
git add core/ui/simulation.py
git commit -m "feat(ui): update image size and simulation summary to match Tamagotchi style"
```

---

### Task 5: Update app.py to inject CSS and clean up controls

**Files:**
- Modify: `core/app.py:21` (page config)
- Modify: `core/app.py:31-44` (add CSS injection, style controls)

**Step 1: Add CSS injection call in `main()` after page config**

Add `inject_tamagotchi_css()` import and call it after `st.set_page_config()`.

Update the import in app.py:
```python
from core.ui.simulation import (
    inject_tamagotchi_css,
    render_simulation_controls,
    run_simulation_loop,
    display_simulation_summary,
)
```

**Step 2: Commit**

```bash
git add core/app.py core/ui/simulation.py
git commit -m "feat(ui): inject Tamagotchi CSS from app entry point"
```

---

### Task 6: Manual testing and polish

**Step 1: Run the app and verify visually**

Run: `cd /Users/wizard/Desktop/programming/projects/jenbina && python run_app.py`

Check:
- [ ] Cream background renders
- [ ] Environment ribbon shows location/time/weather in one line
- [ ] Jenbina image is centered and 350px
- [ ] Needs show as colored progress bars (red/yellow/green)
- [ ] Critical needs pulse
- [ ] Emotions show as pill chips
- [ ] Action shows as narrative card with delta
- [ ] Thought bubble shows inner monologue
- [ ] Tier 2 sections auto-expand correctly
- [ ] Debug expander contains all raw data
- [ ] No raw JSON visible at Tier 1

**Step 2: Fix any visual issues**

Adjust CSS values, spacing, colors as needed.

**Step 3: Run existing E2E tests**

Run: `cd /Users/wizard/Desktop/programming/projects/jenbina && pytest tests/e2e/test_simulation.py -v`

The E2E tests check for visible text output per stage. They may need selector updates if the text structure changed. Fix any failures.

**Step 4: Final commit**

```bash
git add -A
git commit -m "fix(ui): polish Tamagotchi layout and fix E2E tests"
```
