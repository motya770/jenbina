# Pixel Art UI Redesign

**Date:** 2026-10-27
**Status:** Approved (revision 2, 2026-10-27, applied)
**Approach:** CSS device shell + CSS-animated hand-authored sprites (no framework change, no iframe)

## Problem

The February 2026 Tamagotchi redesign made the simulation page calmer, but it still
reads as a generic Streamlit app: soft cards, gradients, emoji, and thirteen 3 MB
painterly portraits that do not match each other. The result feels clumsy rather
than like a creature living inside a device.

## Goal

Make the Simulation page a pixel-art handheld: Jenbina is a small animated sprite on
a retro screen, with needs, emotions, inner monologue and chat all inside that screen.
The other pages (Chat, Environment, Console, Debug Info, Admin) get the same shell,
fonts and colors, but their content stays as it is.

Style: full-color 16-bit. Sprites keep real colors, bars and icons use real colors.
Not Game Boy green, not a 1-bit Tamagotchi LCD.

## Design

### 1. Sprite system

**Canvas.** One state = one 96x48 PNG sheet holding two 48x48 frames side by side
(frame 0 at x=0, frame 1 at x=48). Displayed at 4x (192x192 CSS pixels) with
`image-rendering: pixelated`.

**Character.** Pixel Jenbina keeps her current identity: dark hair, silver spacesuit
with a teal collar, warm skin, coral blush.

**Palette** (`core/ui/sprites/palette.py`, one character per color in the art strings):

| Key | Name          | Hex       |
|-----|---------------|-----------|
| `.` | transparent   | —         |
| `K` | outline       | `#2B1B2E` |
| `S` | skin          | `#F5C7A1` |
| `s` | skin shadow   | `#D9986F` |
| `B` | blush / coral | `#FF8FAB` |
| `H` | hair          | `#3A2A3F` |
| `h` | hair highlight| `#5E4A66` |
| `W` | white         | `#FFFFFF` |
| `E` | iris          | `#3B6EA5` |
| `M` | mouth         | `#B5484D` |
| `A` | suit silver   | `#C9D1D9` |
| `a` | suit shadow   | `#8A94A6` |
| `T` | teal accent   | `#5FB3B3` |
| `Y` | yellow        | `#FFD93D` |
| `G` | green         | `#6BCB77` |
| `R` | red           | `#FF6B6B` |
| `N` | brown         | `#8B5A2B` |

**Layered composition.** Every frame is composed from layers drawn in order; later
layers overwrite earlier ones wherever they are not transparent:

1. `body` — shared torso, arms, suit, collar (one drawing)
2. `hair` — shared
3. one `face` overlay: `neutral`, `smile`, `sad`, `angry`, `fear`, `surprised`,
   `thinking` (eyes up), `reading` (eyes down), `asleep` (eyes closed), `blink`
   (eyes closed, mouth as neutral), `talk_open`
4. zero or one `prop` overlay: `bowl_fork_up`, `bowl_fork_down`, `cup`, `cup_tilt`,
   `book`, `speech_lines`, `legs_a`, `legs_b`
5. zero or more `effect` overlays: `sweat_drop_a`, `sweat_drop_b`, `tear`,
   `anger_mark`, `question_a`, `question_b`, `zzz_a`, `zzz_b`

**States.** File names match the existing selection logic in
`get_jenbina_image_for_emotion()` and `get_jenbina_image_for_action()`, so only the
directory changes:

| State       | Frame 0                      | Frame 1                              |
|-------------|------------------------------|--------------------------------------|
| `base`      | neutral                      | blink                                |
| `smile`     | smile                        | blink                                |
| `sad`       | sad + tear                   | blink + tear                         |
| `angry`     | angry + anger_mark           | blink + anger_mark                   |
| `scary`     | fear + sweat_drop_a          | fear + sweat_drop_b                  |
| `surprised` | surprised                    | blink                                |
| `thinking`  | thinking + question_a        | thinking + question_b                |
| `eat`       | smile + bowl_fork_up         | smile + bowl_fork_down               |
| `drink`     | neutral + cup                | neutral + cup_tilt                   |
| `read`      | reading + book               | blink + book                         |
| `sleep`     | asleep + zzz_a               | asleep + zzz_b                       |
| `talk`      | talk_open + speech_lines     | smile                                |
| `walks`     | neutral + legs_a             | neutral + legs_b, whole frame 1px up |

`MOTION_STATES = {scary, thinking, eat, drink, sleep, talk, walks}` use the
`.px-anim-motion` class; every other state uses `.px-anim-blink`.

**Icons.** 8x8 PNGs in the same palette, replacing emoji:

- needs (keyed by need name): `hunger`, `sleep`, `security`, `love`, `esteem`,
  `self_actualization`
- emotions: `joy`, `sadness`, `anger`, `fear`, `surprise`, `disgust`, `trust`,
  `anticipation`
- weather: `sunny`, `cloudy`, `rain`, `storm`, `snow`, `fog`, `wind`
- `player` (the human in chat)

**Pipeline.** Art lives as pixel strings in `core/ui/sprites/art.py`. A Pillow
compositor in `core/ui/sprites/build.py` renders every state and icon and writes:

```
assets/sprites/jenbina_<state>.png     96x48, RGBA
assets/sprites/jenbina_avatar.png      48x48, frame 0 of `base` (chat avatar)
assets/sprites/icons/<name>.png         8x8, RGBA
assets/favicon.png                      48x48, same image as the avatar
```

`python -m core.ui.sprites.build` regenerates them; `--check` exits non-zero when
any committed file differs from a fresh render. Output is deterministic (no
timestamps, fixed PNG encoder settings). The PNGs are committed; the app never runs
the builder at runtime.

`core/ui/sprites/__init__.py` exposes `STATES`, `ICONS`, `sprite_path(state)` and
`icon_path(name)`.

### 2. Device shell and visual language

**Fonts** (Google Fonts, with a monospace fallback stack):

- `Press Start 2P`, 10–12px — chrome only: page title, section labels, bar labels,
  buttons, chips, environment ribbon.
- `VT323`, 20px — anything read at length: inner monologue, action card, chat
  messages, expander bodies.

**Colors:**

| Role                   | Hex       |
|------------------------|-----------|
| page background        | `#0E0F16` |
| device body            | `#2A2D3A` |
| bezel highlight        | `#3E4254` |
| bezel shadow           | `#1A1C25` |
| screen background      | `#1B1F3B` |
| screen inner border    | `#5FB3B3` |
| text                   | `#F2EFE6` |
| muted text             | `#A9B0C3` |
| accent                 | `#FF8FAB` |
| dialog box background  | `#10132A` |
| need good / mid / low  | `#6BCB77` / `#FFD93D` / `#FF6B6B` |

No gradients, no blur, no soft shadows, no border radius anywhere. Depth comes from
hard 4px bevels (`box-shadow` with zero blur).

**The handheld.** `inject_pixel_css()` in `core/ui/pixel_theme.py` styles Streamlit
1.38 containers:

- `.stApp` — page background.
- main `.block-container` — the device and its screen on one element: a 14px solid
  border in the device body color is the bezel (with hard bevel shadows and a 4px
  outline), the element background is the screen color, a 2px inset teal line marks
  the screen edge, a "JENBINA-16" badge is rendered with `::before`, and a scanline
  overlay with `::after` (`repeating-linear-gradient`, 3px period, 6% black,
  `pointer-events: none`). No wrapper element is needed.
- `[data-testid="stSidebar"]` — the control pad: device body color, pixel-styled
  number inputs and two chunky buttons. Button labels ("🔄 Run Simulation Loop",
  "▶️ Run Single Iteration") stay unchanged for the e2e tests.
- `[data-testid="stChatInput"]` and the bottom block — the device's bottom bar.
- `[data-testid="stChatMessage"]` — dialog rows; avatar images pixelated.
- buttons, number inputs, expanders, checkboxes, dividers, links — pixel borders,
  chrome font, screen colors.

**Elements** (all emitted as HTML strings by the existing render functions):

- Sprite: `<div class="px-sprite px-anim-blink" style="background-image:url(data:...)">`.
  Two animation classes: `.px-anim-blink` (period 2.4s, frame 1 for the last 15%)
  for emotion states, `.px-anim-motion` (period 1.2s, 50/50) for action states.
  Frames are switched with `steps(1, end)` on `background-position`.
- Needs bars: keep `.need-row`; inside, an 8x8 icon, a label, ten `.need-seg`
  blocks (filled count = round(pct / 10)), and the percentage. Rows under 30% get
  `.need-critical`, whose filled segments blink with `steps(1)` (no fade).
- Emotion chips: `.emotion-chip` becomes a square badge with the 8x8 icon, name and
  intensity. Still at most four, still only above 15.
- Mood badge: same markup family, green for positive emotions, red otherwise.
- Thought bubble and action card: `.px-dialog` boxes — dialog background, 3px
  off-white border, stepped tail drawn with `box-shadow`. The action card keeps its
  title, reasoning, lessons and satisfaction delta lines.
- Environment ribbon: one-line `.env-ribbon` status bar at the top of the screen
  with the matching weather icon.
- Chat: `st.chat_message(..., avatar=<path>)` with `jenbina_avatar.png` for the
  assistant and the `player` icon for the user.

**Other pages.** Each page under `core/pages/` calls `inject_pixel_css()` right after
`st.set_page_config(...)`. `.streamlit/config.toml` switches to the screen palette so
native widgets that CSS does not reach (toggles, selects, toasts) match.

### 3. Code changes

**New**

- `core/ui/sprites/__init__.py`, `palette.py`, `art.py`, `build.py`
- `core/ui/pixel_theme.py` — `inject_pixel_css()`, `sprite_html(state, caption)`,
  `icon_html(name, alt)`, `dialog_html(body, kind)`; data URIs cached with
  `functools.lru_cache`.
- `assets/sprites/*.png`, `assets/sprites/icons/*.png`
- `tests/test_sprites.py`, `tests/test_pixel_ui.py`

**Modified**

- `core/ui/simulation.py`
  - `inject_tamagotchi_css()` becomes a thin alias that calls `inject_pixel_css()`.
  - `IMAGES_DIR` points at `assets/sprites`.
  - `display_jenbina_image(image_path, caption)` keeps its signature, derives the
    state from the file name (`jenbina_<state>.png`) and emits `sprite_html()`
    instead of `st.image`, so all existing call sites keep working.
  - `render_environment_ribbon()`, `render_needs_bars()`, `render_emotion_chips()`,
    `render_mood_indicator()`, `render_action_narrative()` emit the pixel markup
    above, using icons instead of emoji.
  - The inline thought-bubble markup in `run_single_iteration()` uses `dialog_html()`.
- `core/ui/chat.py` — `render_chat_simple()` and `render_chat_interface()` pass
  avatars to `st.chat_message`.
- `core/pages/2_💬_Chat.py`, `3_🌍_Environment.py`, `4_📋_Console.py`,
  `5_🔧_Debug_Info.py`, `6_🔑_Admin.py` — one `inject_pixel_css()` call each.
- `.streamlit/config.toml` — screen palette.
- `assets/favicon.png` — replaced by the 48x48 base frame.

**Removed**

- `src/images/jenbina_*.png` (thirteen painterly portraits, ~40 MB). Nothing else
  references them after this change.

**Untouched**

- Cognition, needs, memory, emotions, goals, learning, planning.
- The computation flow and LLM call order in `run_single_iteration()`.
- Session state keys in `core/ui/shared_init.py`, the auth gate, the launcher scripts.
- Content of the Chat, Environment, Console, Debug Info and Admin pages.

### 4. Error handling

- `sprite_path()` for an unknown or missing state returns the `base` sheet; if that is
  missing too, `sprite_html()` returns a text placeholder (`[Jenbina]`) instead of
  raising. `icon_html()` for a missing icon returns an empty span.
- The font stack declares `monospace` fallbacks, so an offline run stays coherent.
- The builder raises a clear error if Pillow is missing; the runtime never imports it
  beyond what Streamlit already needs.
- Data URIs are built once per state and cached for the process lifetime.

### 5. Testing

**Unit (`tests/test_sprites.py`)**

- every state in `STATES` and every icon in `ICONS` renders
- sheets are 96x48 RGBA, icons 8x8 RGBA, favicon 48x48
- rendering twice yields identical bytes
- every state's frame 0 differs from `base` frame 0, and frame 1 differs from frame 0
- `build --check` passes against the committed files (fails CI on stale assets)

**Unit (`tests/test_pixel_ui.py`)**, with `core.ui.simulation.st.markdown` patched and
a small fake person exposing `maslow_needs.get_need_satisfaction()` and
`emotion_system.get_emotional_state_summary()` / `get_dominant_emotions()`:

- `render_needs_bars()` emits six `.need-row` elements, ten `.need-seg` each,
  the right filled count, and `.need-critical` only below 30%
- `render_emotion_chips()` caps at four chips and skips intensities of 15 or less
- `render_action_narrative()` and the thought bubble wrap content in `.px-dialog`
- `sprite_html()` falls back to `base`, then to the text placeholder

**End to end**

- `tests/e2e/test_simulation.py` and `tests/e2e/test_feedback_loop.py` run unchanged
  (button names and `.need-row` survive).

**Visual check**

- Launch the app and screenshot the idle state, a running iteration (thinking, action,
  result), and a chat exchange; compare against sections 1–2.

## Out of scope

- Redesigning the content of the Environment, Console, Debug Info and Admin pages.
- Sound, a sprite editor, or more than two animation frames per state.
- Replacing Streamlit or adding a Node build step.

## Revision 2 — portrait + sprite, candy arcade palette

Applied after the first implementation was reviewed in the browser. Two changes;
everything else above stands.

**The painterly portraits return.** The thirteen `jenbina_<state>.png` portraits live
in `assets/portraits/` (same names as before, so `get_jenbina_image_for_emotion()` and
`get_jenbina_image_for_action()` are untouched; `IMAGES_DIR` points there).
`display_jenbina_image()` shows the portrait as the main character display through
`st.image(..., width=256)` inside a game-window frame (4px ink border, cream mat, hard
shadow), and under it a status strip: the pixel sprite at half size (`sprite_html(...,
scale=2)` → `.px-sprite-2x`, 96px, still animated) beside the caption. Missing portrait
→ `base` portrait → sprite strip only. The pixel sprite remains the chat avatar and the
favicon. Section 3's "Removed" list no longer applies to the portraits.

**Candy arcade palette** replaces the section 2 table:

| Role                      | Hex       |
|---------------------------|-----------|
| page background           | `#22184A` |
| device body               | `#FF6B9D` |
| bezel highlight / shadow  | `#FFA8C9` / `#B3285C` |
| screen background         | `#4FC3F7` |
| screen inner line         | `#FFFFFF` |
| ink (text)                | `#1E1B3A` |
| muted text                | `#4A4670` |
| panels (dialogs, chat, ribbon, inputs) | `#FFF6D5`, shade `#E8DCC0` |
| control pad (sidebar)     | `#2A1F5E` |
| accent / deep accent      | `#FF3E8A` / `#C2185B` |
| secondary button          | `#5BE36A` |
| hover                     | `#FFD93D` |
| critical / negative       | `#FF4757` |

Each need bar has its own fill: hunger `#FF8C42`, sleep `#9B6BFF`, safety `#2EC4B6`,
social `#FF5DA2`, esteem `#FFD93D`, growth `#5BE36A` (`.need-<name>` on the row;
critical rows still blink red). Emotion chips are colored tiles (`.emotion-<name>`):
joy yellow, sadness blue, anger red, fear purple, surprise orange, disgust green, trust
teal, anticipation pink. Fonts, scanlines, bevels and the no-gradient / no-radius rules
are unchanged. `.streamlit/config.toml` carries the screen palette.
