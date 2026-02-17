# Mobile Display Tests Design

## Goal

Proactively verify the simulation page renders correctly on mobile viewports before users encounter issues.

## Approach

Extend the existing Playwright E2E test infrastructure with a new test file that sets mobile viewport sizes and checks structural/visibility properties of key UI elements.

## Target Viewports

- iPhone SE/8: 375x667
- Android (common): 412x915

## Test Scope

Main simulation page only (initial idle state, no simulation run).

## Test Cases

| Test | What it checks |
|------|---------------|
| `test_page_loads` | Title "Jenbina" is visible |
| `test_no_horizontal_overflow` | `document.body.scrollWidth` does not exceed viewport width |
| `test_jenbina_image_visible` | Character image renders and fits within viewport bounds |
| `test_needs_bars_visible` | Need bars container is visible and not clipped |
| `test_emotion_chips_wrap` | Emotion chips container wraps within viewport |
| `test_sidebar_toggle_accessible` | Sidebar toggle is reachable and opens to reveal controls |

## Implementation

- File: `tests/e2e/test_mobile_display.py`
- Uses `@pytest.mark.parametrize` with `indirect=True` to pass viewport sizes to a `mobile_page` fixture
- Reuses existing `streamlit_server` session fixture from `conftest.py`
- 12 total tests (6 tests x 2 viewports)

## Out of Scope

- Full simulation output on mobile (depends on LLM, too slow)
- Other pages (Chat, Environment, Console, Debug)
- Visual/screenshot regression testing
