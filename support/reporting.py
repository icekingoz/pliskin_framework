"""Attach failure evidence to whichever reporters happen to be installed.

Two sinks, deliberately decoupled:

* **Allure** -- the published report. Attachments show up inline on the test's
  page, which is the whole reason the screenshots exist.
* **pytest-html** -- the fallback artifact. Embedding is best-effort: the extras
  API changed shape between pytest-html 3.x (``report.extra``) and 4.x
  (``report.extras``), so both spellings are attempted.

Everything here is defensive on purpose. A reporting helper must never be the
reason a test run dies -- if an attachment fails, the *test result* is still the
thing that matters, and a broken screenshot should never turn a real failure
into a confusing error. Hence the bare ``except Exception`` blocks below, which
would be wrong almost anywhere else in this codebase.
"""

from __future__ import annotations

import base64
from typing import Any

try:  # allure-pytest is optional; the suite runs fine without it
    import allure
    from allure_commons.types import AttachmentType

    _ALLURE = True
except ImportError:  # pragma: no cover
    _ALLURE = False


# --- Allure -----------------------------------------------------------------
def _allure_attach(name: str, payload: Any, attachment_type: Any) -> None:
    if not _ALLURE:
        return
    try:
        allure.attach(payload, name=name, attachment_type=attachment_type)
    except Exception:  # pragma: no cover - never break a run over a screenshot
        pass


# --- pytest-html ------------------------------------------------------------
def _html_attach(item: Any, report: Any, extra: Any) -> None:
    """Append one extra to the report, tolerating both plugin generations."""
    if item is None or report is None or extra is None:
        return
    try:
        for attr in ("extras", "extra"):
            if hasattr(report, attr):
                setattr(report, attr, [*getattr(report, attr), extra])
                return
        # Neither present: 4.x creates `extras` lazily, so seed it.
        report.extras = [extra]
    except Exception:  # pragma: no cover
        pass


def _html_plugin(item: Any) -> Any:
    try:
        return item.config.pluginmanager.getplugin("html")
    except Exception:  # pragma: no cover
        return None


# --- public API -------------------------------------------------------------
def attach_png(
    name: str, data: bytes, item: Any = None, report: Any = None
) -> None:
    """Attach a PNG (screenshot) to every available reporter."""
    if not data:
        return
    _allure_attach(name, data, AttachmentType.PNG if _ALLURE else None)

    plugin = _html_plugin(item)
    if plugin is None:
        return
    try:
        encoded = base64.b64encode(data).decode("ascii")
        _html_attach(item, report, plugin.extras.image(encoded, name=name))
    except Exception:  # pragma: no cover
        pass


def attach_text(
    name: str, body: str, item: Any = None, report: Any = None
) -> None:
    """Attach a block of plain text (HTTP exchanges, page URL, DOM dump)."""
    if not body:
        return
    _allure_attach(name, body, AttachmentType.TEXT if _ALLURE else None)

    plugin = _html_plugin(item)
    if plugin is None:
        return
    try:
        _html_attach(item, report, plugin.extras.text(body, name=name))
    except Exception:  # pragma: no cover
        pass


def attach_html(
    name: str, markup: str, item: Any = None, report: Any = None
) -> None:
    """Attach captured page source. Allure renders it; pytest-html links it."""
    if not markup:
        return
    _allure_attach(name, markup, AttachmentType.HTML if _ALLURE else None)
