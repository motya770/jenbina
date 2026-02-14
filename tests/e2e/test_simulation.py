"""
Playwright E2E test — run a single simulation iteration and verify each stage
produces visible output in the browser.
"""

import re

import pytest
from playwright.sync_api import Page, expect


# Generous timeout: LLM calls can be slow
STAGE_TIMEOUT = 180_000  # 3 minutes per stage


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
        """Sanity check — the simulation page loads and shows controls."""
        expect(sim_page.locator("text=Simulation Controls")).to_be_visible(
            timeout=15_000
        )
        expect(
            sim_page.get_by_role("button", name=re.compile("Run Single Iteration"))
        ).to_be_visible()

    def test_single_iteration_produces_output(self, sim_page: Page):
        """Click 'Run Single Iteration' and verify each stage card appears
        with content."""

        # Click the single-run button
        sim_page.get_by_role(
            "button", name=re.compile("Run Single Iteration")
        ).click()

        # ── Stage 1: Environment ──────────────────────────────────────
        # Person State card
        person_card = sim_page.locator("text=Person State").first
        expect(person_card).to_be_visible(timeout=STAGE_TIMEOUT)

        # World State card
        world_card = sim_page.locator("text=World State").first
        expect(world_card).to_be_visible(timeout=STAGE_TIMEOUT)

        # ── Stage 2: Perception & Context ─────────────────────────────
        # Needs Analysis card
        needs_card = sim_page.locator("text=Needs Analysis").first
        expect(needs_card).to_be_visible(timeout=STAGE_TIMEOUT)

        # Context card (working memory / goals / lessons)
        context_card = sim_page.locator("text=Context").first
        expect(context_card).to_be_visible(timeout=STAGE_TIMEOUT)

        # ── Stage 3: Action Decision ──────────────────────────────────
        action_card = sim_page.locator("text=Action Decision").first
        expect(action_card).to_be_visible(timeout=STAGE_TIMEOUT)

        # ── Stage 4: Checks & Analysis ────────────────────────────────
        safety_card = sim_page.locator("text=Safety Check").first
        expect(safety_card).to_be_visible(timeout=STAGE_TIMEOUT)

        state_card = sim_page.locator("text=State Analysis").first
        expect(state_card).to_be_visible(timeout=STAGE_TIMEOUT)

        emotions_card = sim_page.locator("text=Emotions").first
        expect(emotions_card).to_be_visible(timeout=STAGE_TIMEOUT)

        # ── Stage 5: Learning & Updates ───────────────────────────────
        learning_card = sim_page.locator("text=Learning").first
        expect(learning_card).to_be_visible(timeout=STAGE_TIMEOUT)

        # ── Completion ────────────────────────────────────────────────
        # The iteration prints a success banner
        completion = sim_page.locator("text=completed in").first
        expect(completion).to_be_visible(timeout=STAGE_TIMEOUT)

    def test_simulation_summary_appears(self, sim_page: Page):
        """After running, the simulation summary section should appear."""

        sim_page.get_by_role(
            "button", name=re.compile("Run Single Iteration")
        ).click()

        # Wait for the full iteration to finish
        completion = sim_page.locator("text=completed in").first
        expect(completion).to_be_visible(timeout=STAGE_TIMEOUT)

        # The summary banner
        summary = sim_page.locator("text=Completed").first
        expect(summary).to_be_visible(timeout=30_000)
