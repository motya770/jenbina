# Pixel Art UI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the Simulation page into a pixel-art handheld with an animated 48x48 Jenbina sprite, pixel icons, segmented needs bars and RPG dialog boxes, and give the other pages the same shell.

**Architecture:** Sprites are authored as pixel strings in Python, composed from shared body/hair layers plus face, prop and effect overlays, and rendered to committed PNGs by a Pillow builder. A new `core/ui/pixel_theme.py` owns the CSS and the HTML helpers; the existing render functions in `core/ui/simulation.py` keep their names and call sites and only change the markup they emit.

**Tech Stack:** Python 3.10+, Streamlit 1.38.0, Pillow 10.4 (already installed with Streamlit), unittest, Playwright for the existing e2e tests.

**Spec:** `docs/plans/2026-10-27-pixel-art-ui-redesign.md`

## Global Constraints

- No new entries in `requirements.txt`. Pillow is already a Streamlit dependency.
- Streamlit is pinned at 1.38.0; CSS selectors target that version's `data-testid` values.
- Tests are `unittest.TestCase` classes in `tests/test_*.py`, run with `python -m pytest tests/test_*.py -v --tb=short`, and must not need an LLM, a database or the network. Patch `core.ui.simulation.st` / `core.ui.pixel_theme.st` / `core.ui.chat.st` the way `tests/test_greeting_generation.py` patches `core.ui.chat.st`.
- The e2e tests depend on the `.need-row` class and the button labels "🔄 Run Simulation Loop" and "▶️ Run Single Iteration". Keep both.
- Sprite sheets are 96x48 RGBA, icons 8x8 RGBA, avatar and favicon 48x48 RGBA. Sprites display at 4x (192px) with `image-rendering: pixelated`.
- Palette keys and hex values are exactly the table in spec section 1. State names and file names are exactly the thirteen in the spec's state table. Icon names are exactly the twenty-two listed in the spec.
- Fonts: `Press Start 2P` for chrome at 10–12px, `VT323` at 20px for long text, both from Google Fonts with a `monospace` fallback. Colors are the table in spec section 2. No gradients, blur, soft shadows or border radius anywhere in the new CSS.
- Every commit message uses a conventional prefix (`feat:`, `test:`, `docs:`, `chore:`) and ends with the `Co-Authored-By` line this session uses.

## Review Focus

1. A need satisfaction outside 0–100 (for example 120 or -5) must clamp to ten or zero filled segments, never raise or overflow the bar. Pinned in Task 7.
2. An emotion name with no icon (for example `curiosity`) must still render a chip with an empty icon span, never `KeyError`. Pinned in Task 7.
3. A weather description with no known keyword must fall back to the `cloudy` icon. Pinned in Task 7.
4. LLM text with `<`, `>` or `&` in the thought bubble or action card must be escaped so it cannot break the page markup. Pinned in Task 6.
5. A caller passing a legacy path (`src/images/jenbina_base.png`) or an unknown file name to `display_jenbina_image` must get the base sprite, not an empty slot. Pinned in Task 7.

---

## File Structure

| File | Responsibility |
|------|----------------|
| `core/ui/sprites/palette.py` | `PALETTE` key → RGBA table and the two shared type aliases, nothing else |
| `core/ui/sprites/art.py` | Pixel strings: body, hair, faces, props, effects, icon art, and `STATE_FRAMES` |
| `core/ui/sprites/build.py` | Compositor, PNG rendering, `--check`, CLI |
| `core/ui/sprites/__init__.py` | `STATES`, `MOTION_STATES`, `ICONS`, `SPRITES_DIR`, path helpers |
| `core/ui/pixel_theme.py` | `inject_pixel_css()` and the HTML helpers |
| `core/ui/simulation.py` | Existing render helpers, now emitting pixel markup |
| `core/ui/chat.py` | Chat avatars |
| `assets/sprites/` | Committed PNG output |
| `tests/test_sprites.py` | Builder and art tests |
| `tests/test_pixel_ui.py` | Theme helper and render helper tests |

Shared types, defined in `core/ui/sprites/palette.py` (which imports nothing from the package, so `art.py` and `build.py` can both import them without a cycle; `__init__.py` must never import `build.py`):

```python
Layer = tuple[int, int, list[str]]          # (x, y, rows); each row is a string of palette keys
FrameSpec = dict                            # {"face": str, "props": list[str], "effects": list[str], "dy": int}
```

Sprite layout grid (so overlays line up with the shared body). All coordinates are (x, y) on the 48x48 canvas:

| Region | Anchor | Size | Notes |
|--------|--------|------|-------|
| hair | (10, 2) | 28x16 | drawn after body, covers top of head |
| head | (12, 6) | 24x22 | skin with `s` shadow on the right edge |
| face overlay | (16, 14) | 16x10 | eyes in rows 2–4 of the overlay, mouth in rows 7–9 |
| torso + collar | (14, 28) | 20x14 | `A` suit, `a` shadow on the right, `T` collar in the top 3 rows |
| legs overlay | (14, 40) | 20x8 | default boots are part of the body; `legs_a` / `legs_b` overwrite them |
| hand prop | (30, 30) | 14x14 | bowl, cup, book |
| speech lines | (2, 16) | 10x10 | left of the face |
| effect (top right) | (34, 2) | 12x12 | question marks, zzz, sweat drop, anger mark |
| tear | (18, 22) | 4x6 | under the left eye |

---

### Task 1: Palette and compositor

**Files:**
- Create: `core/ui/sprites/__init__.py` (empty for now), `core/ui/sprites/palette.py`, `core/ui/sprites/build.py`
- Test: `tests/test_sprites.py`

**Interfaces:**
- Produces: `PALETTE: dict[str, tuple[int, int, int, int]]` with the seventeen keys from the spec table, `"."` mapped to `(0, 0, 0, 0)`, plus the `Layer` and `FrameSpec` aliases from File Structure, all in `palette.py`.
- Produces: `compose(layers: list[Layer], size: tuple[int, int] = (48, 48), dy: int = 0) -> PIL.Image.Image` in `build.py`. Draws layers in order; a `"."` pixel leaves what is underneath; `dy` shifts the whole result vertically (negative is up, exposed rows are transparent); a key not in `PALETTE` raises `ValueError` naming the key; a row that runs past the canvas raises `ValueError`.

- [ ] **Step 1: Write the failing tests**

```python
class TestPalette(unittest.TestCase):
    def test_has_seventeen_keys_with_transparent_dot(self):
        self.assertEqual(len(PALETTE), 17)
        self.assertEqual(PALETTE["."], (0, 0, 0, 0))
        self.assertEqual(PALETTE["B"], (0xFF, 0x8F, 0xAB, 255))

class TestCompose(unittest.TestCase):
    def test_later_layer_overwrites_but_dot_is_transparent(self):
        img = compose([(0, 0, ["SS", "SS"]), (0, 0, [".K", ".."])], size=(2, 2))
        self.assertEqual(img.getpixel((0, 0)), PALETTE["S"])
        self.assertEqual(img.getpixel((1, 0)), PALETTE["K"])
    def test_offset_layer(self):
        img = compose([(1, 1, ["K"])], size=(2, 2))
        self.assertEqual(img.getpixel((1, 1)), PALETTE["K"])
        self.assertEqual(img.getpixel((0, 0)), (0, 0, 0, 0))
    def test_dy_shifts_up_and_exposes_transparent_row(self):
        img = compose([(0, 0, ["..", "KK"])], size=(2, 2), dy=-1)
        self.assertEqual(img.getpixel((0, 0)), PALETTE["K"])
        self.assertEqual(img.getpixel((0, 1)), (0, 0, 0, 0))
    def test_unknown_key_raises(self):
        with self.assertRaises(ValueError): compose([(0, 0, ["Z"])], size=(1, 1))
    def test_overflow_raises(self):
        with self.assertRaises(ValueError): compose([(1, 0, ["KK"])], size=(2, 1))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_sprites.py -v`
Expected: FAIL with `ModuleNotFoundError: core.ui.sprites.palette`

- [ ] **Step 3: Implement `PALETTE` in `palette.py` and `compose()` in `build.py`**

Use `Image.new("RGBA", size, (0, 0, 0, 0))` and `putpixel`; apply `dy` with `Image.transform` or by composing onto a shifted canvas.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_sprites.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add core/ui/sprites tests/test_sprites.py
git commit -m "feat(sprites): palette and layer compositor"
```

---

### Task 2: Body, hair, faces and the emotion states

**Files:**
- Create: `core/ui/sprites/art.py`
- Modify: `core/ui/sprites/build.py`
- Test: `tests/test_sprites.py`

**Interfaces:**
- Consumes: `compose()` from Task 1.
- Produces in `art.py`: `BODY: Layer`, `HAIR: Layer`, `FACES: dict[str, Layer]` with keys `neutral, smile, sad, angry, fear, surprised, thinking, reading, asleep, blink, talk_open`, `PROPS: dict[str, Layer]` (empty until Task 3), `EFFECTS: dict[str, Layer]` with keys `tear, anger_mark, sweat_drop_a, sweat_drop_b, question_a, question_b` (`zzz_a, zzz_b` come in Task 3), and `STATE_FRAMES: dict[str, tuple[FrameSpec, FrameSpec]]` for `base, smile, sad, angry, scary, surprised, thinking` exactly as the spec's state table.
- Produces in `build.py`: `frame_layers(spec: FrameSpec) -> list[Layer]` (body, hair, face, props, effects in that order), `render_frame(spec: FrameSpec) -> Image.Image` (48x48), `render_sheet(state: str) -> Image.Image` (96x48, frame 0 at x=0, frame 1 at x=48; unknown state raises `KeyError`).

- [ ] **Step 1: Write the failing tests**

```python
EMOTION_STATES = ["base", "smile", "sad", "angry", "scary", "surprised", "thinking"]

class TestArtLayers(unittest.TestCase):
    def test_every_layer_fits_the_canvas_and_uses_palette_keys(self):
        for name, (x, y, rows) in all_layers().items():   # helper in the test: BODY, HAIR, *FACES, *PROPS, *EFFECTS
            for row in rows:
                self.assertLessEqual(x + len(row), 48, name)
                self.assertTrue(set(row) <= set(PALETTE), name)
            self.assertLessEqual(y + len(rows), 48, name)
    def test_faces_sit_in_the_face_region(self):
        for name, (x, y, rows) in FACES.items():
            self.assertEqual((x, y), (16, 14), name)
            self.assertEqual((len(rows), len(rows[0])), (10, 16), name)

class TestEmotionSheets(unittest.TestCase):
    def test_sheets_are_96x48_rgba(self):
        for s in EMOTION_STATES:
            self.assertEqual((render_sheet(s).size, render_sheet(s).mode), ((96, 48), "RGBA"), s)
    def test_frame_one_differs_from_frame_zero(self):
        for s in EMOTION_STATES:
            sheet = render_sheet(s)
            self.assertNotEqual(sheet.crop((0, 0, 48, 48)).tobytes(), sheet.crop((48, 0, 96, 48)).tobytes(), s)
    def test_each_state_differs_from_base(self):
        base = render_sheet("base").crop((0, 0, 48, 48)).tobytes()
        for s in EMOTION_STATES[1:]:
            self.assertNotEqual(render_sheet(s).crop((0, 0, 48, 48)).tobytes(), base, s)
    def test_unknown_state_raises(self):
        with self.assertRaises(KeyError): render_sheet("dancing")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_sprites.py -v`
Expected: FAIL with `ImportError` on `art`

- [ ] **Step 3: Draw `BODY`, `HAIR` and the eleven faces in `art.py`, then add the seven emotion `STATE_FRAMES`**

Follow the layout grid above. Dark hair `H` with `h` highlights, skin `S` with `s` on the right edge, suit `A` with `a` shadow, `T` collar, coral `B` blush (two pixels under each eye in every face except `asleep`). `blink` is `neutral` with closed eyes (a 2px `K` line per eye). `thinking` eyes look up-right, `reading` eyes look down.

- [ ] **Step 4: Implement `frame_layers()`, `render_frame()` and `render_sheet()` in `build.py`**

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_sprites.py -v`
Expected: all passed

- [ ] **Step 6: Look at the art**

Run: `d=$(mktemp -d) && python -c "from core.ui.sprites.build import render_sheet; render_sheet('smile').resize((384,192), 0).save('$d/smile.png')" && echo $d/smile.png`, then view that PNG. Expected: a recognisable dark-haired girl in a silver suit, smiling, with the blink frame on the right. Adjust pixels until it reads at 4x.

- [ ] **Step 7: Commit**

```bash
git add core/ui/sprites tests/test_sprites.py
git commit -m "feat(sprites): body, hair, faces and emotion states"
```

---

### Task 3: Props, effects and the action states

**Files:**
- Modify: `core/ui/sprites/art.py`
- Test: `tests/test_sprites.py`

**Interfaces:**
- Consumes: `render_sheet()` from Task 2.
- Produces: `PROPS` keys `bowl_fork_up, bowl_fork_down, cup, cup_tilt, book, speech_lines, legs_a, legs_b`; `EFFECTS` gains `zzz_a, zzz_b`; `STATE_FRAMES` gains `eat, drink, read, sleep, talk, walks` exactly as the spec table, with `walks` frame 1 using `dy=-1`.

- [ ] **Step 1: Write the failing tests**

```python
ACTION_STATES = ["eat", "drink", "read", "sleep", "talk", "walks"]

class TestActionSheets(unittest.TestCase):
    def test_all_thirteen_states_present_in_spec_order(self):
        self.assertEqual(list(STATE_FRAMES), EMOTION_STATES + ACTION_STATES)
    def test_action_sheets_render_and_animate(self):
        for s in ACTION_STATES:
            sheet = render_sheet(s)
            self.assertEqual(sheet.size, (96, 48), s)
            self.assertNotEqual(sheet.crop((0, 0, 48, 48)).tobytes(), sheet.crop((48, 0, 96, 48)).tobytes(), s)
    def test_walks_frame_one_is_shifted_up(self):
        self.assertEqual(STATE_FRAMES["walks"][1]["dy"], -1)
        self.assertEqual(render_frame(STATE_FRAMES["walks"][1]).getpixel((24, 47)), (0, 0, 0, 0))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_sprites.py -v`
Expected: FAIL on the state list and `KeyError: 'eat'`

- [ ] **Step 3: Draw the eight props and two `zzz` effects, add the six action frames**

Bowl is `W` with `R` food and a `K` fork; cup `W` with `T` liquid; book `N` cover with `W` pages; speech lines three short `W` dashes; `legs_a`/`legs_b` swap which boot is forward.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_sprites.py -v`
Expected: all passed

- [ ] **Step 5: Look at the art**

Run the Task 2 Step 6 command for `eat`, `sleep` and `walks`. Expected: the prop is readable at 4x and the two frames read as motion.

- [ ] **Step 6: Commit**

```bash
git add core/ui/sprites/art.py tests/test_sprites.py
git commit -m "feat(sprites): props, effects and action states"
```

---

### Task 4: Icons

**Files:**
- Modify: `core/ui/sprites/art.py`, `core/ui/sprites/build.py`
- Test: `tests/test_sprites.py`

**Interfaces:**
- Produces: `ICON_ART: dict[str, list[str]]` with exactly these twenty-two keys, each eight rows of eight: `hunger, sleep, security, love, esteem, self_actualization, joy, sadness, anger, fear, surprise, disgust, trust, anticipation, sunny, cloudy, rain, storm, snow, fog, wind, player`.
- Produces: `render_icon(name: str) -> Image.Image` (8x8 RGBA; unknown name raises `KeyError`).

- [ ] **Step 1: Write the failing tests**

```python
ICON_NAMES = ["hunger", "sleep", "security", "love", "esteem", "self_actualization",
              "joy", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation",
              "sunny", "cloudy", "rain", "storm", "snow", "fog", "wind", "player"]

class TestIcons(unittest.TestCase):
    def test_exactly_the_spec_icons(self):
        self.assertEqual(sorted(ICON_ART), sorted(ICON_NAMES))
    def test_icons_are_8x8_and_not_empty(self):
        for name in ICON_NAMES:
            img = render_icon(name)
            self.assertEqual((img.size, img.mode), ((8, 8), "RGBA"), name)
            self.assertTrue(any(px[3] for px in img.getdata()), name)
    def test_unknown_icon_raises(self):
        with self.assertRaises(KeyError): render_icon("banana")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_sprites.py -v`
Expected: FAIL with `ImportError: ICON_ART`

- [ ] **Step 3: Draw the twenty-two icons and implement `render_icon()` with `compose(..., size=(8, 8))`**

Needs: burger (`N`/`G`/`R`), crescent moon (`Y`), shield (`T`/`A`), heart (`B`), star (`Y`), sprout (`G`/`N`). Emotions: small faces in `Y` with `K` features, `anger` red, `sadness` with a `E` tear, `trust` two `B` hearts, `anticipation` a `Y` sparkle. Weather: sun `Y`, cloud `W`/`a`, rain cloud with `E` drops, storm with `Y` bolt, snow `W` flakes, fog `a` bands, wind `W` streaks. `player`: a `S` face with `H` hair.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_sprites.py -v`
Expected: all passed

- [ ] **Step 5: Commit**

```bash
git add core/ui/sprites tests/test_sprites.py
git commit -m "feat(sprites): 8x8 icon set"
```

---

### Task 5: Build CLI, committed assets and path helpers

**Files:**
- Modify: `core/ui/sprites/build.py`, `core/ui/sprites/__init__.py`
- Create: `assets/sprites/*.png`, `assets/sprites/icons/*.png`, `assets/sprites/jenbina_avatar.png`
- Replace: `assets/favicon.png`
- Test: `tests/test_sprites.py`

**Interfaces:**
- Produces in `__init__.py`: `STATES: tuple[str, ...]` (the thirteen, spec order), `MOTION_STATES: frozenset[str] = {"scary", "thinking", "eat", "drink", "sleep", "talk", "walks"}`, `ICONS: tuple[str, ...]` (the twenty-two), `SPRITES_DIR: str` (absolute path of `assets/sprites`), `sprite_path(state: str) -> str` (returns the `base` sheet path for any state not in `STATES`), `icon_path(name: str) -> str`, `avatar_path() -> str`.
- Produces in `build.py`: `render_all() -> dict[str, Image.Image]` keyed by path relative to `assets/sprites` (`jenbina_<state>.png`, `jenbina_avatar.png`, `icons/<name>.png`), `png_bytes(img: Image.Image) -> bytes` (`save(format="PNG", optimize=False)`), `write_all(out_dir: Path, favicon: Path | None) -> list[Path]`, `check(out_dir: Path, favicon: Path | None) -> list[str]` (relative paths that are missing or differ), `main(argv: list[str] | None = None) -> int` accepting `--check`, `--out` (default `assets/sprites`), `--favicon` (default `assets/favicon.png`); returns 1 when `--check` finds differences.

- [ ] **Step 1: Write the failing tests**

```python
class TestBuild(unittest.TestCase):
    def test_render_all_has_every_output(self):
        out = render_all()
        self.assertEqual(sorted(out), sorted([f"jenbina_{s}.png" for s in STATES] + ["jenbina_avatar.png"] + [f"icons/{i}.png" for i in ICONS]))
        self.assertEqual(out["jenbina_avatar.png"].size, (48, 48))
    def test_png_bytes_is_deterministic(self):
        self.assertEqual(png_bytes(render_sheet("base")), png_bytes(render_sheet("base")))
    def test_write_then_check_is_clean_and_edit_is_detected(self):
        with tempfile.TemporaryDirectory() as d:
            out, fav = Path(d) / "sprites", Path(d) / "favicon.png"
            write_all(out, fav)
            self.assertEqual(check(out, fav), [])
            (out / "icons" / "joy.png").write_bytes(b"corrupt")
            self.assertEqual(check(out, fav), ["icons/joy.png"])
    def test_committed_assets_are_fresh(self):
        self.assertEqual(check(Path(SPRITES_DIR), Path(SPRITES_DIR).parent / "favicon.png"), [])

class TestPaths(unittest.TestCase):
    def test_sprite_path_falls_back_to_base(self):
        self.assertTrue(sprite_path("nope").endswith("jenbina_base.png"))
        self.assertTrue(sprite_path("eat").endswith("jenbina_eat.png"))
    def test_motion_states(self):
        self.assertEqual(MOTION_STATES, frozenset({"scary", "thinking", "eat", "drink", "sleep", "talk", "walks"}))
    def test_constants_match_the_art(self):
        self.assertEqual(STATES, tuple(STATE_FRAMES))
        self.assertEqual(sorted(ICONS), sorted(ICON_ART))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_sprites.py -v`
Expected: FAIL with `ImportError` on `render_all` / `STATES`

- [ ] **Step 3: Implement the `__init__.py` constants and helpers, then `render_all()`, `png_bytes()`, `write_all()`, `check()` and `main()`**

`write_all` creates `icons/` and writes the favicon as a copy of the avatar bytes when `favicon` is given. `check` compares `png_bytes(render)` to the file bytes.

- [ ] **Step 4: Generate the assets**

Run: `python -m core.ui.sprites.build && python -m core.ui.sprites.build --check; echo exit=$?`
Expected: `exit=0`; `ls assets/sprites | wc -l` prints 15 and `ls assets/sprites/icons | wc -l` prints 22; `assets/favicon.png` is 48x48.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_sprites.py -v`
Expected: all passed

- [ ] **Step 6: Commit**

```bash
git add core/ui/sprites tests/test_sprites.py assets/sprites assets/favicon.png
git commit -m "feat(sprites): build CLI with --check and committed pixel assets"
```

---

### Task 6: Pixel theme CSS and HTML helpers

**Files:**
- Create: `core/ui/pixel_theme.py`
- Test: `tests/test_pixel_ui.py`

**Interfaces:**
- Consumes: `sprite_path`, `icon_path`, `MOTION_STATES`, `STATES` from Task 5.
- Produces: `inject_pixel_css() -> None` (one `st.markdown(css, unsafe_allow_html=True)` call), `sprite_html(state: str, caption: str | None = None) -> str`, `icon_html(name: str, alt: str = "") -> str`, `dialog_html(body: str, kind: str = "thought") -> str` (`kind` is `"thought"` or `"action"`), `PLACEHOLDER = "[Jenbina]"`, and `_data_uri(path: str) -> str` wrapped in `functools.lru_cache`. Import `sprite_path`, `icon_path` and `MOTION_STATES` by name (`from core.ui.sprites import ...`) so tests can patch `core.ui.pixel_theme.sprite_path`.
- Markup contract: `sprite_html` returns `<div class="px-sprite-wrap"><div class="px-sprite px-anim-blink|px-anim-motion" style="background-image:url(data:image/png;base64,...)"></div><div class="px-caption">…</div></div>`; caption is `html.escape`d and omitted when `None`. If the resolved sheet file is missing, it returns `<div class="px-sprite-wrap"><span class="px-placeholder">[Jenbina]</span></div>`. `icon_html` returns `<img class="px-icon" alt="…" src="data:…">` or `<span class="px-icon px-icon-missing"></span>` when the file is missing. `dialog_html` returns `<div class="px-dialog px-dialog-thought|px-dialog-action">…</div>` with the body `html.escape`d and newlines turned into `<br>`.

- [ ] **Step 1: Write the failing tests**

```python
class TestSpriteHtml(unittest.TestCase):
    def test_blink_and_motion_classes(self):
        self.assertIn("px-anim-blink", sprite_html("smile"))
        self.assertIn("px-anim-motion", sprite_html("walks"))
    def test_embeds_png_data_uri_and_escapes_caption(self):
        html_ = sprite_html("base", caption="Jen <3 & co")
        self.assertIn("data:image/png;base64,", html_)
        self.assertIn("Jen &lt;3 &amp; co", html_)
    def test_unknown_state_uses_base_sheet(self):
        self.assertEqual(sprite_html("nope"), sprite_html("base"))
    def test_missing_sheet_falls_back_to_placeholder(self):
        with patch("core.ui.pixel_theme.sprite_path", return_value="/nonexistent/jenbina_base.png"):
            self.assertIn(PLACEHOLDER, sprite_html("base"))

class TestIconAndDialog(unittest.TestCase):
    def test_icon_html_and_missing_icon(self):
        self.assertIn('class="px-icon"', icon_html("joy", alt="Joy"))
        self.assertIn("px-icon-missing", icon_html("curiosity"))
    def test_dialog_escapes_and_breaks_lines(self):
        out = dialog_html("a < b\nc & d", kind="action")
        self.assertIn("px-dialog-action", out)
        self.assertIn("a &lt; b<br>c &amp; d", out)

class TestInjectCss(unittest.TestCase):
    @patch("core.ui.pixel_theme.st")
    def test_injects_once_with_fonts_and_sprite_rules(self, st):
        inject_pixel_css()
        st.markdown.assert_called_once()
        css, kwargs = st.markdown.call_args[0][0], st.markdown.call_args[1]
        self.assertTrue(kwargs.get("unsafe_allow_html"))
        for needle in ["Press+Start+2P", "VT323", ".px-sprite", "image-rendering: pixelated",
                       ".need-seg", ".px-dialog", "steps(1", "#1B1F3B", "#FF8FAB"]:
            self.assertIn(needle, css)
        self.assertNotRegex(css, r"border-radius:\s*[1-9]")   # only `border-radius: 0` overrides are allowed
        self.assertNotIn("linear-gradient(135", css)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_pixel_ui.py -v`
Expected: FAIL with `ModuleNotFoundError: core.ui.pixel_theme`

- [ ] **Step 3: Implement the helpers, then write the CSS from spec section 2**

CSS targets, in this order: `@import` for both fonts; `.stApp` page background; `.stApp .block-container` as device + screen (14px border in device body color, hard bevel `box-shadow`s with zero blur, 4px `outline`, screen background, `::before` badge "JENBINA-16", `::after` scanlines with `repeating-linear-gradient(0deg, rgba(0,0,0,.06) 0 1px, transparent 1px 3px)` and `pointer-events: none`); `[data-testid="stSidebar"]` as control pad; headings, `p`, `label`, links; buttons; `[data-testid="stNumberInput"]`; `[data-testid="stExpander"]`; `[data-testid="stChatInput"]`, `[data-testid="stBottomBlockContainer"]`, `[data-testid="stChatMessage"]` and its `img` (pixelated); then `.env-ribbon`, `.px-sprite-wrap`, `.px-sprite` (192x192, `background-size: 384px 192px`), `@keyframes px-blink` (0–85% position `0 0`, 85–100% `-192px 0`) and `@keyframes px-motion` (50/50), both `steps(1, end)`, 2.4s and 1.2s; `.px-caption`; `.need-row`, `.need-icon`, `.need-label`, `.need-segs`, `.need-seg`, `.need-seg.on`, `.need-pct`, `.need-critical .need-seg.on` blinking with `steps(1)`; `.emotion-chips`, `.emotion-chip`; `.mood-badge`; `.px-dialog`, `.px-dialog-thought` tail, `.px-dialog-action`, `.action-title`, `.action-reasoning`, `.satisfaction-delta` with `.delta-positive|negative|neutral` as flat fills; `.px-icon` (16x16, pixelated).

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_pixel_ui.py -v`
Expected: all passed

- [ ] **Step 5: Commit**

```bash
git add core/ui/pixel_theme.py tests/test_pixel_ui.py
git commit -m "feat(ui): pixel theme CSS and sprite/icon/dialog helpers"
```

---

### Task 7: Simulation page renderers

**Files:**
- Modify: `core/ui/simulation.py:21-265` (CSS function and `IMAGES_DIR`), `:317-326` (`display_jenbina_image`), `:328-475` (ribbon, needs, chips, mood, action card), `:996` (thought bubble)
- Test: `tests/test_pixel_ui.py`

**Interfaces:**
- Consumes: everything from Task 6; `SPRITES_DIR` from Task 5.
- Produces: same function names and signatures as today. `inject_tamagotchi_css()` becomes a one-line alias calling `inject_pixel_css()` (keep the name; `core/ui/__init__.py` and `app.py` import it). `IMAGES_DIR = SPRITES_DIR`. `display_jenbina_image(image_path, caption=None)` derives the state from `os.path.basename(image_path)` by stripping `jenbina_` and `.png`, then `st.markdown(sprite_html(state, caption), unsafe_allow_html=True)`. New module constant `_WEATHER_ICONS: dict[str, str]` mapping keywords `sunny, clear → sunny; cloudy, overcast → cloudy; rain → rain; storm → storm; snow → snow; fog → fog; wind → wind`, default `cloudy`.
- Markup contract: `render_needs_bars` emits six `<div class="need-row">` (or `<div class="need-row need-critical">` below 30%) each containing `icon_html(need, alt=label)`, `<span class="need-label">`, `<div class="need-segs">` holding ten spans, `<span class="need-seg on"></span>` for filled and `<span class="need-seg"></span>` for empty, where the filled count is `round(clamp(pct, 0, 100) / 10)`, and `<span class="need-pct">`. `render_emotion_chips` emits `<span class="emotion-chip">` with `icon_html(name, alt=name)` (at most four, intensity > 15). `render_mood_indicator` emits `<span class="mood-badge mood-positive">` for `joy, trust, anticipation, surprise` and `mood-negative` otherwise. `render_environment_ribbon` emits `<div class="env-ribbon">` starting with `icon_html(icon, alt=icon)` for the matched weather icon. `render_action_narrative` does not call `dialog_html` (its body is markup, not text); it emits `<div class="px-dialog px-dialog-action">` itself with `html.escape` applied to `chosen`, `reasoning` and `lessons`, keeping the `action-title`, `action-reasoning` and `satisfaction-delta` elements. The thought bubble at line 996 becomes `st.markdown(dialog_html(thought_display, kind="thought"), unsafe_allow_html=True)`.

- [ ] **Step 1: Write the failing tests** (add to `tests/test_pixel_ui.py`)

```python
class FakeNeeds:
    def __init__(self, v): self.v = v
    def get_need_satisfaction(self, n): return self.v.get(n, 0)
class FakeEmotions:
    def __init__(self, e): self.e = e
    def get_emotional_state_summary(self): return {"emotions": self.e}
    def get_dominant_emotions(self, n):
        return [{"name": k, "intensity": v} for k, v in sorted(self.e.items(), key=lambda kv: -kv[1])[:n]]
class FakePerson:
    name = "Jenbina"
    def __init__(self, needs, emotions):
        self.maslow_needs, self.emotion_system = FakeNeeds(needs), FakeEmotions(emotions)

def rendered(fn, *a):
    with patch("core.ui.simulation.st") as st:
        fn(*a)
        return st.markdown.call_args[0][0]

class TestNeedsBars(unittest.TestCase):
    def test_six_rows_ten_segments_and_fill_count(self):
        html_ = rendered(render_needs_bars, FakePerson({"hunger": 60, "sleep": 43, "security": 80, "love": 0, "esteem": 120, "self_actualization": -5}, {}))
        self.assertEqual(html_.count('class="need-row'), 6)
        self.assertEqual(html_.count('<span class="need-seg'), 60)
        self.assertEqual(html_.count('need-seg on'), 6 + 4 + 8 + 0 + 10 + 0)
    def test_critical_only_below_thirty(self):
        html_ = rendered(render_needs_bars, FakePerson({"hunger": 29, "sleep": 30}, {}))
        self.assertEqual(html_.count("need-critical"), 1 + 4)   # hunger, plus the four needs missing from the dict (0%)

class TestChipsMoodRibbon(unittest.TestCase):
    def test_chips_cap_at_four_skip_low_and_survive_unknown_emotion(self):
        html_ = rendered(render_emotion_chips, FakePerson({}, {"joy": 90, "trust": 80, "fear": 70, "curiosity": 60, "anger": 50, "sadness": 15}))
        self.assertEqual(html_.count('class="emotion-chip"'), 4)
        self.assertIn("px-icon-missing", html_)
        self.assertNotIn("Sadness", html_)
    def test_mood_badge_polarity(self):
        self.assertIn("mood-positive", rendered(render_mood_indicator, FakePerson({}, {"joy": 50})))
        self.assertIn("mood-negative", rendered(render_mood_indicator, FakePerson({}, {"anger": 50})))
    def test_ribbon_weather_icon_and_fallback(self):
        ws = lambda d: {"location": {"name": "Palo Alto"}, "time": {"time_of_day": "night"}, "weather": {"description": d, "temperature": 18}}
        self.assertIn('alt="rain"', rendered(render_environment_ribbon, ws("light rain")))
        self.assertIn('alt="cloudy"', rendered(render_environment_ribbon, ws("volcanic ash")))

class TestActionAndSprite(unittest.TestCase):
    def test_action_card_is_a_dialog_and_escapes(self):
        html_ = rendered(render_action_narrative, {"chosen_action": "Eat <soup>", "reasoning": "a & b"}, 60.0, 68.0)
        self.assertIn("px-dialog-action", html_)
        self.assertIn("eat &lt;soup&gt;", html_)
        self.assertIn("delta-positive", html_)
    def test_display_jenbina_image_derives_state_from_any_path(self):
        self.assertIn("px-anim-motion", rendered(display_jenbina_image, "/old/src/images/jenbina_eat.png", "Jenbina"))
        self.assertEqual(rendered(display_jenbina_image, "whatever.png"), rendered(display_jenbina_image, "jenbina_base.png"))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_pixel_ui.py -v`
Expected: the new classes FAIL (old emoji/`need-bar-fill` markup)

- [ ] **Step 3: Rewrite the six helpers, the alias, `IMAGES_DIR`, `_WEATHER_ICONS` and line 996 as specified in Interfaces**

Delete the old CSS body from `inject_tamagotchi_css()` entirely.

- [ ] **Step 4: Run the whole unit suite**

Run: `python -m pytest tests/test_*.py -v --tb=short`
Expected: all passed (watch `tests/test_greeting_generation.py`, which imports `core.ui.chat`)

- [ ] **Step 5: Commit**

```bash
git add core/ui/simulation.py tests/test_pixel_ui.py
git commit -m "feat(ui): pixel markup for sprite, needs, emotions, ribbon and action card"
```

---

### Task 8: Chat avatars

**Files:**
- Modify: `core/ui/chat.py:257` and `:457`
- Test: `tests/test_pixel_ui.py`

**Interfaces:**
- Consumes: `avatar_path()`, `icon_path("player")` from Task 5.
- Produces: both `st.chat_message` calls pass `avatar=avatar_path()` for the assistant and `avatar=icon_path("player")` for the user.

- [ ] **Step 1: Write the failing test**

```python
class TestChatAvatars(unittest.TestCase):
    @patch("core.ui.chat.handle_user_input")
    @patch("core.ui.chat.send_proactive_message", return_value=None)
    @patch("core.ui.chat.check_return_greeting", return_value=None)
    @patch("core.ui.chat._get_user_display_name", return_value="Matt")
    @patch("core.ui.chat.st")
    def test_history_rows_get_sprite_avatars(self, st, *_):
        st.session_state = {"proactive_checked": True}
        Msg = namedtuple("Msg", "sender content")
        person = SimpleNamespace(name="Jenbina", send_message=lambda *a: None,
                                 get_conversation_history=lambda *a, **k: [Msg("Matt", "hi"), Msg("person", "hello")])
        render_chat_simple(person, None, None, False)
        avatars = [c.kwargs.get("avatar") for c in st.chat_message.call_args_list]
        self.assertTrue(avatars[0].endswith("icons/player.png"))
        self.assertTrue(avatars[1].endswith("jenbina_avatar.png"))
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest tests/test_pixel_ui.py::TestChatAvatars -v`
Expected: FAIL, `avatar` is `None`

- [ ] **Step 3: Add the `avatar=` arguments at lines 257 and 457**

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_pixel_ui.py tests/test_greeting_generation.py -v`
Expected: all passed

- [ ] **Step 5: Commit**

```bash
git add core/ui/chat.py tests/test_pixel_ui.py
git commit -m "feat(ui): pixel avatars in chat"
```

---

### Task 9: Theme on every page, Streamlit config, remove old portraits

**Files:**
- Modify: `core/pages/2_💬_Chat.py:12`, `core/pages/3_🌍_Environment.py:18`, `core/pages/4_📋_Console.py:11`, `core/pages/5_🔧_Debug_Info.py:10`, `core/pages/6_🔑_Admin.py:16` (add one line after each), `.streamlit/config.toml`
- Delete: `src/images/jenbina_*.png` (thirteen files) and the now-empty `src/` tree
- Modify: `CLAUDE.md` (repository structure and the Existing Plans table)

**Interfaces:**
- Consumes: `inject_pixel_css()` from Task 6.

- [ ] **Step 1: Add `from core.ui.pixel_theme import inject_pixel_css` and a call to `inject_pixel_css()` immediately after `st.set_page_config(...)` on each of the five pages**

- [ ] **Step 2: Replace the theme in `.streamlit/config.toml`**

```toml
[theme]
primaryColor = "#FF8FAB"
backgroundColor = "#1B1F3B"
secondaryBackgroundColor = "#2A2D3A"
textColor = "#F2EFE6"
font = "monospace"
```

- [ ] **Step 3: Delete the old portraits and confirm nothing references them**

Run: `git rm -q src/images/jenbina_*.png && rmdir src/images src 2>/dev/null; grep -rn "src/images\|src', 'images\|\"src\", \"images\"" core tests README.md INSTALL.md; echo grep_exit=$?`
Expected: `grep_exit=1` (no matches; older plan documents under `docs/` may still mention the old folder and that is fine)

- [ ] **Step 4: Update `CLAUDE.md`**

In the repository tree replace the `assets/` and `src/` lines with `assets/sprites/` (committed pixel assets) and add `core/ui/sprites/` and `core/ui/pixel_theme.py`; add two rows to the Existing Plans table for `2026-10-27-pixel-art-ui-redesign.md` and `2026-10-27-pixel-art-ui-implementation.md`.

- [ ] **Step 5: Run the unit suite**

Run: `python -m pytest tests/test_*.py -v --tb=short`
Expected: all passed

- [ ] **Step 6: Commit**

```bash
git add core/pages .streamlit/config.toml CLAUDE.md
git commit -m "feat(ui): pixel theme on every page; drop painterly portraits"
```

---

### Task 10: Visual verification and e2e

**Files:**
- Modify: `core/ui/pixel_theme.py` only if a selector or size needs correcting

- [ ] **Step 1: Launch the app**

Run from the project root in the background: `JENBINA_SKIP_AUTH=1 .venv/bin/python -m streamlit run core/app.py --server.headless true --server.port 8501`
Expected: `Local URL: http://localhost:8501` in the log.

- [ ] **Step 2: Screenshot the idle state**

Open `http://localhost:8501`, wait for the first iteration to finish. Expected: dark bezel around a navy screen with scanlines, the title in Press Start 2P, a 192px pixel Jenbina blinking, six segmented bars with 8x8 icons, square emotion chips, the chat input styled as the bottom bar. No emoji anywhere on the page.

- [ ] **Step 3: Screenshot a running iteration**

Click "▶️ Run Single Iteration" in the sidebar. Expected: thought bubble as a bordered dialog box with a tail, the sprite switching to `thinking` and then to the action sprite with motion animation, the action card as a dialog box with a flat delta badge.

- [ ] **Step 4: Screenshot a chat exchange**

Type a message in the chat input. Expected: the user row shows the `player` icon, Jenbina's row shows the avatar, both pixelated, text in VT323.

- [ ] **Step 5: Check the other pages**

Open Chat, Environment, Console, Debug Info and Admin from the sidebar. Expected: same bezel, fonts and colors; content unchanged and readable.

- [ ] **Step 6: Run the e2e tests if Playwright is installed**

Run: `.venv/bin/python -m pytest tests/e2e -v --tb=short`
Expected: all passed, or `ModuleNotFoundError: playwright` (then skip with a note in the final report).

- [ ] **Step 7: Fix and commit any selector or sizing corrections**

```bash
git add core/ui/pixel_theme.py
git commit -m "fix(ui): selector and sizing corrections after visual check"
```
