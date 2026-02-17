"""
Playwright E2E test — verify the simulation feedback loop:
  1. Actions affect needs (satisfaction delta is non-zero)
  2. Actions vary across iterations (not all identical)
  3. World description reflects action context

This test is intended for MANUAL runs only (via workflow_dispatch).
It runs 3 iterations with page reloads between them and checks that
the feedback loop produces observable changes.
"""

import re

import pytest
from playwright.sync_api import Page, expect


# LLM calls are slow — allow up to 5 minutes per iteration
ITERATION_TIMEOUT = 300_000  # 5 min


@pytest.fixture()
def sim_page(page: Page, streamlit_server: str):
    """Navigate to the Streamlit app and wait for it to be ready."""
    page.goto(streamlit_server, wait_until="networkidle")
    page.wait_for_selector("text=Jenbina", timeout=30_000)
    return page


def _run_one_iteration(page: Page, streamlit_url: str) -> dict:
    """Run a single simulation iteration and return observed data.

    Reloads the page before clicking to avoid stale-element issues
    with Streamlit's re-render cycle.
    """
    page.goto(streamlit_url, wait_until="networkidle")
    page.wait_for_selector("text=Jenbina", timeout=30_000)

    # Click "Run Single Iteration"
    page.get_by_role(
        "button", name=re.compile("Run Single Iteration")
    ).click()

    # Wait for the action card
    action_el = page.locator(".action-title").first
    action_el.wait_for(state="visible", timeout=ITERATION_TIMEOUT)
    action_text = action_el.inner_text()

    # Wait for iteration completion
    page.locator("text=completed in").first.wait_for(
        state="visible", timeout=ITERATION_TIMEOUT
    )

    # Extract satisfaction delta from the learning messages
    sat_delta = None
    sat_elements = page.locator("text=/Satisfaction:.*→/").all()
    for el in sat_elements:
        try:
            txt = el.inner_text()
            # Match pattern like "Satisfaction: 42.0% → 43.4% (+1.4%)"
            m = re.search(r"\(([+-]?\d+\.?\d*)%\)", txt)
            if m:
                sat_delta = float(m.group(1))
                break
        except Exception:
            continue

    # Extract chosen action name
    action_name = re.sub(
        r"^▶\s*Jenbina decided to\s*", "", action_text, flags=re.IGNORECASE
    ).strip()

    # Check that need bars are rendered
    need_bars = page.locator(".need-row").count()

    return {
        "action_name": action_name,
        "action_text": action_text,
        "sat_delta": sat_delta,
        "need_bars_count": need_bars,
    }


class TestFeedbackLoop:
    """Run multiple iterations and verify the simulation feedback loop
    produces meaningful changes in needs and varied actions."""

    @pytest.mark.timeout(1200)  # 20 min total for 3 iterations
    def test_actions_affect_needs(self, sim_page: Page, streamlit_server: str):
        """At least one iteration should produce a non-zero satisfaction delta,
        confirming that actions feed back into the needs system."""
        results = []
        for _ in range(3):
            result = _run_one_iteration(sim_page, streamlit_server)
            results.append(result)

        # At least one iteration should have a measurable satisfaction change
        deltas = [r["sat_delta"] for r in results if r["sat_delta"] is not None]
        assert len(deltas) > 0, (
            f"No satisfaction deltas found in any iteration. "
            f"Actions were: {[r['action_name'] for r in results]}"
        )

        has_nonzero = any(abs(d) >= 0.05 for d in deltas)
        assert has_nonzero, (
            f"All satisfaction deltas were effectively zero: {deltas}. "
            f"Action effects are not propagating to needs."
        )

    @pytest.mark.timeout(1200)
    def test_actions_vary_across_iterations(
        self, sim_page: Page, streamlit_server: str
    ):
        """Over 5 iterations, Jenbina should not repeat the exact same action
        every single time."""
        results = []
        for _ in range(5):
            result = _run_one_iteration(sim_page, streamlit_server)
            results.append(result)

        action_names = [r["action_name"] for r in results]
        unique_actions = len(set(action_names))

        assert unique_actions >= 2, (
            f"Jenbina repeated the exact same action all {len(action_names)} times: "
            f"'{action_names[0]}'. The feedback loop should produce variety."
        )

    @pytest.mark.timeout(600)
    def test_need_bars_rendered(self, sim_page: Page, streamlit_server: str):
        """After running an iteration, need bars should be visible in the UI."""
        result = _run_one_iteration(sim_page, streamlit_server)

        assert result["need_bars_count"] > 0, (
            "No need bars (.need-row elements) found after running an iteration."
        )
