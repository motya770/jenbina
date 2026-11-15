"""
Playwright E2E test — run a single simulation iteration on the home screen and
verify the rail and the timeline show its output.
"""

import re

import pytest
from playwright.sync_api import Page, expect


# Generous timeout: LLM calls can be slow
STAGE_TIMEOUT = 300_000  # 5 minutes: a beat takes about two, and one may already be in flight


@pytest.fixture()
def sim_page(page: Page, streamlit_server: str):
    """Navigate to the Streamlit app and wait for it to be ready."""
    page.goto(streamlit_server, wait_until="networkidle")
    # Wait for Streamlit to finish initial render (title appears)
    page.wait_for_selector("text=Jenbina", timeout=30_000)
    return page


class TestSingleIteration:
    """Run one iteration via the UI and check that each simulation stage
    renders non-empty output."""

    def test_page_loads(self, sim_page: Page):
        """Sanity check — the home screen loads with the timeline and heartbeat card."""
        expect(sim_page.locator("text=Today with Jenbina")).to_be_visible(
            timeout=15_000
        )
        expect(
            sim_page.get_by_role("button", name=re.compile("Step once"))
        ).to_be_visible()

    def test_single_iteration_produces_output(self, sim_page: Page):
        """Click 'Step once' and verify the rail and the timeline fill in."""

        action_count = sim_page.locator(".px-event-action").count()
        sim_page.get_by_role("button", name=re.compile("Step once")).click()
        expect(sim_page.locator(".px-event-action")).to_have_count(
            action_count + 1, timeout=STAGE_TIMEOUT
        )

        # ── The rail: needs bars are always there ─────────────────────
        needs_bar = sim_page.locator("text=Hunger").first
        expect(needs_bar).to_be_visible(timeout=STAGE_TIMEOUT)

        # ── The timeline: the action row shows what Jenbina chose to do ─
        action_row = sim_page.locator(".px-event-action .px-event-title").last
        expect(action_row).to_be_visible(timeout=STAGE_TIMEOUT)
        expect(action_row).to_contain_text("Jenbina decided to")
