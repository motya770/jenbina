"""Who may open the admin panel.

The panel lists every registered user, so the gate must hold on a public
deployment. Request headers (``Host``, ``Origin``) are not evidence of a local
request: behind a reverse proxy every request is remote, and a client sets
``Origin`` to whatever it likes. Access is therefore granted only to the signed-in
admin account, or in explicit local development mode (``JENBINA_SKIP_AUTH=1``),
which must never be set on a public URL.
"""
import os
from typing import Mapping, Optional

ADMIN_EMAIL = "matvei.kudelin@gmail.com"


def is_dev_mode(env: Optional[Mapping[str, str]] = None) -> bool:
    """True when sign-in is disabled for local development and E2E tests."""
    env = os.environ if env is None else env
    return env.get("JENBINA_SKIP_AUTH") == "1"


def is_admin(user: Optional[Mapping], env: Optional[Mapping[str, str]] = None) -> bool:
    """Return True if ``user`` (the signed-in user, or None) may see the admin panel."""
    if is_dev_mode(env):
        return True
    return bool(user) and user.get("email") == ADMIN_EMAIL
