# Blade Runner 2049 Theme Redesign

**Date:** 2026-11-14
**Status:** Proposal (direction chosen in conversation on 2026-11-14; awaiting approval of this spec and the mockup)
**Approach:** Replace the candy arcade pixel skin with a restrained Blade Runner 2049 skin. The layout from `2026-10-28-timeline-ui-redesign.md` (chat timeline on the left, status rail on the right) stays exactly as it is. Only colors, fonts, borders, icons and the portrait frame change.

## Problem

The pixel skin from `2026-10-27-pixel-art-ui-redesign.md` (revision 2, candy arcade
palette) is too loud for what the product is.

- Every label uses Press Start 2P, which is hard to read below 10px and makes the
  rail look like a game HUD.
- Hot pink device, sky-blue screen, cream panels and nine accent colors compete
  with each other. Nothing reads as more important than anything else.
- The painterly portraits sit inside a toy frame, so the best art in the project
  looks out of place.
- The tone says "toy". Jenbina is meant to read as a mind with memory, mood and
  needs.

The messaging layout itself works and the user likes it. It is not the problem.

## Goal

Jenbina should feel like a synthetic companion living in a quiet, smoky apartment:
warm where she speaks, cold where the system speaks, and calm everywhere else.
The reference is Joi in Blade Runner 2049, an AI companion with moods, filmed in
amber haze and cold teal light.

## Non-goals

- Changing the layout, page structure, timeline logic, event log or runner.
- Changing prompts, chains or any simulation logic.
- Regenerating the portraits. They are graded by CSS in this revision.
- A light theme. The skin is dark only, by choice.

## Anti-goals (what would make this a failure even if it works)

- Low contrast body text. Chat text must pass WCAG AA (4.5:1) on its surface.
- Scanlines, glitch effects, rain or flicker on anything you read.
- Neon on every element. Glow is reserved for Jenbina's voice and the live stage.
- Movie props or logos (Wallace Corp, LAPD, Atari signs). The skin borrows light and
  color, not trademarks.
- Emoji in new markup (unchanged from the timeline spec).

## Design

### 1. Palette

Four roles, each with one job. Every color is a CSS custom property in the
theme module.

| Token | Hex | Role |
|-------|-----|------|
| `--br-smoke` | `#0D0A08` | Page background, the dark apartment |
| `--br-haze` | `#16110D` | Card and timeline surface |
| `--br-dust` | `#221A13` | Raised surface: input, Jenbina bubble, active tab |
| `--br-line` | `#3A2C20` | Hairline borders, 1px |
| `--br-text` | `#EDE3D6` | Body text (contrast 15:1 on haze) |
| `--br-muted` | `#9C8D7C` | Captions, timestamps, thoughts (contrast 6:1 on haze) |
| `--br-amber` | `#E8A25A` | Jenbina: her bubble edge, her name, her needs bars, primary button |
| `--br-ice` | `#62D2DA` | The system and the user: event rows, markers, stage pill, user bubble edge |
| `--br-joi` | `#C873E6` | Strong emotion only: mood events and the dominant emotion chip |
| `--br-rust` | `#E0573C` | Warning only: a need below 30% |

Rule of thumb: amber is her, ice is the machine and you, violet is feeling. Anything
else is a neutral.

### 2. Type

| Role | Family | Use |
|------|--------|-----|
| Display | Rajdhani 600, uppercase, letter-spacing 0.18em | Card titles, the "Today with Jenbina" header, button labels. Never body text. |
| Body | IBM Plex Sans 400/500, 15–16px, line-height 1.55 | Chat messages, event titles, mind card lines |
| Data | IBM Plex Mono 400, 11–12px, letter-spacing 0.04em | Timestamps, markers, deltas, needs percentages, kind tags, stage pill |

All three load from Google Fonts in one `@import`, with system fallbacks. Press Start 2P
and VT323 are removed.

### 3. Shell

- The pink handheld device goes away. The home screen is the dark page itself, with
  the two columns at the same `64rem` max width.
- Surfaces get a 1px `--br-line` border and a 2px radius. No hard drop shadows.
- A very faint film grain sits on the page background only (an inline SVG noise
  data URI at 4% opacity). It never covers text surfaces.
- A soft amber radial haze sits behind the top of the rail, like light through
  smog. It is a background gradient, not an animation.
- Streamlit's own widgets (radio, tabs, number inputs, buttons, chat input) are
  restyled in the same CSS so nothing default-looking remains.

### 4. Timeline

- **Jenbina's messages:** `--br-dust` bubble, 2px amber left edge, a faint amber
  outer glow (`box-shadow: 0 0 24px rgba(232,162,90,.08)`). Her avatar becomes a
  small round crop of the current portrait.
- **User messages:** right-aligned, transparent bubble with a 1px ice border. The
  avatar is a plain ice initial circle.
- **Event rows** (action, move, goal, plan): no box. One line with a mono kind tag
  in ice (`ACT`, `MOVE`, `GOAL`, `PLAN`), the title in body text, the meta and
  delta in mono on the right. The `why?` details stay.
- **Mood rows:** same shape, kind tag `MOOD` in violet.
- **Thoughts:** italic muted text with a thin vertical amber line on the left, like
  an inner voice. `more` stays.
- **Markers:** a hairline with the text centered in mono ice, uppercase:
  `23:38 · JENBINA'S HOUSE · NIGHT · CLEAR 15°C`.
- **Input:** `--br-dust` field, amber caret and focus ring, placeholder "Talk to
  Jenbina".

The 8x8 pixel icons are dropped from the timeline. The kind tags replace them and
carry the same information in a form the new skin can hold.

### 5. Status rail

- **Now card:** the stage pill becomes a mono ice capsule with a small pulsing dot
  while a stage runs (`prefers-reduced-motion` turns the pulse off). The portrait
  sits in a thin frame with a warm grade: `filter: sepia(.35) saturate(.85)
  contrast(1.05)` plus an amber overlay at low opacity, so the painterly portraits
  read as a memory projection.
- **Needs bars:** 3px tall lines on a `--br-line` track, filled in amber, with the
  percentage in mono on the right. A need below 30% turns rust.
- **Emotion chips:** text chips with a 1px border. The dominant emotion is violet,
  the rest are neutral.
- **Let her live:** "Step once" is the amber primary button, "Run N" is a ghost
  button with an amber border.
- **Mind card:** tabs become uppercase Rajdhani labels with an amber underline on the
  active tab.

### 6. Code changes

- `core/ui/pixel_theme.py`: replace the `:root` tokens and the CSS body with the new
  skin. Keep the public helpers (`inject_pixel_css`, `event_html`, `marker_html`,
  `stage_pill_html`, `delta_badge_html`, `dialog_html`) and the `.px-*` class names,
  so callers, unit tests and E2E selectors keep working. `event_html` emits a kind
  tag instead of `icon_html`. A later cleanup may rename the module to `theme.py`.
- `.streamlit/config.toml`: `primaryColor = "#E8A25A"`, `backgroundColor =
  "#0D0A08"`, `secondaryBackgroundColor = "#16110D"`, `textColor = "#EDE3D6"`,
  `font = "sans serif"`, and `base = "dark"`.
- `core/ui/sprites/__init__.py`: `avatar_path()` returns a round portrait crop
  generated once by the build script; the pixel sprites stay in the repository but
  the home screen no longer uses them.
- Other pages (Environment, Console, Debug Info) get the new skin for free through
  `inject_pixel_css`.
- Tests: update assertions in `tests/test_pixel_ui.py`, `tests/test_timeline.py` and
  `tests/test_rail.py` that check for icon markup or old colors. No new behavior to
  test beyond the kind tags.

## Mockup

An interactive mockup of the home screen in this skin was published alongside the
proposal. It uses example content and one real portrait.

## Open questions

- Should the portraits eventually be regenerated in a 2049 style (amber haze,
  cinematic, less retro space-age)? The CSS grade is meant to be good enough for now.
- Should the needs bars use one amber for every need, or a subtle hue per Maslow
  level? One amber is calmer; per-level hues are easier to scan.
