"""
Playwright E2E tests — verify the simulation page renders correctly
on mobile viewports (iPhone SE/8 at 375x667, Android at 412x915).

These tests check the initial idle state only (no simulation run).
"""

import pytest
from playwright.sync_api import Page, expect


MOBILE_VIEWPORTS = [
    pytest.param((375, 667), id="iPhone-375x667"),
    pytest.param((412, 915), id="Android-412x915"),
]

# Streamlit sidebar is hidden by default on mobile; the hamburger menu
# toggle uses this test-id.
SIDEBAR_TOGGLE = '[data-testid="stSidebarCollapsedControl"]'


@pytest.fixture()
def mobile_page(page: Page, streamlit_server: str, request):
    """Navigate to the app at the requested mobile viewport size."""
    width, height = request.param
    page.set_viewport_size({"width": width, "height": height})
    page.goto(streamlit_server, wait_until="networkidle")
    page.wait_for_selector("text=Jenbina", timeout=30_000)
    return page


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mobile_page", MOBILE_VIEWPORTS, indirect=True)
class TestMobileSimulationPage:
    """Verify the simulation page renders correctly on mobile viewports."""

    def test_page_loads(self, mobile_page: Page):
        """Title is visible and page renders without error."""
        expect(mobile_page.locator("text=Jenbina").first).to_be_visible(
            timeout=15_000
        )

    def test_no_horizontal_overflow(self, mobile_page: Page):
        """Page body does not exceed the viewport width (no horizontal scrollbar)."""
        viewport_width = mobile_page.viewport_size["width"]
        scroll_width = mobile_page.evaluate("document.body.scrollWidth")
        assert scroll_width <= viewport_width + 5, (
            f"Horizontal overflow detected: scrollWidth={scroll_width} "
            f"exceeds viewport={viewport_width}"
        )

    def test_jenbina_image_visible(self, mobile_page: Page):
        """Character image renders and fits within the viewport."""
        img = mobile_page.locator("img").first
        expect(img).to_be_visible(timeout=15_000)

        box = img.bounding_box()
        assert box is not None, "Image has no bounding box"
        viewport_width = mobile_page.viewport_size["width"]
        assert box["x"] >= 0, f"Image overflows left: x={box['x']}"
        assert box["x"] + box["width"] <= viewport_width + 5, (
            f"Image overflows right: x+w={box['x'] + box['width']} "
            f"viewport={viewport_width}"
        )

    def test_needs_bars_visible(self, mobile_page: Page):
        """Needs bars container is visible and fits within the viewport."""
        needs = mobile_page.locator(".need-row").first
        expect(needs).to_be_visible(timeout=15_000)

        box = needs.bounding_box()
        assert box is not None, "Need row has no bounding box"
        viewport_width = mobile_page.viewport_size["width"]
        assert box["x"] + box["width"] <= viewport_width + 5, (
            f"Needs bar overflows: x+w={box['x'] + box['width']} "
            f"viewport={viewport_width}"
        )

    def test_emotion_chips_wrap(self, mobile_page: Page):
        """Emotion chips container is visible and wraps within the viewport."""
        chips = mobile_page.locator(".emotion-chips").first
        expect(chips).to_be_visible(timeout=15_000)

        box = chips.bounding_box()
        assert box is not None, "Emotion chips container has no bounding box"
        viewport_width = mobile_page.viewport_size["width"]
        assert box["x"] + box["width"] <= viewport_width + 5, (
            f"Emotion chips overflow: x+w={box['x'] + box['width']} "
            f"viewport={viewport_width}"
        )

    def test_sidebar_toggle_accessible(self, mobile_page: Page):
        """On mobile, the sidebar collapses and a toggle button is accessible."""
        toggle = mobile_page.locator(SIDEBAR_TOGGLE)
        expect(toggle).to_be_visible(timeout=15_000)

        toggle.click()
        # After opening, the "Run Single Iteration" button should be reachable
        run_btn = mobile_page.get_by_role("button", name="Run Single Iteration")
        expect(run_btn).to_be_visible(timeout=15_000)
