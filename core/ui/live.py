"""Periodic UI drawing that tolerates changes to the live mind."""

from typing import Callable

import streamlit as st

REFRESH_SECONDS = 5


def draw_guarded(draw: Callable[[], None]) -> bool:
    try:
        draw()
        return True
    except Exception as exc:
        print(f"Live refresh failed: {exc}")
        st.caption("…")
        return False
