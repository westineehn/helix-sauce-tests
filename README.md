# helix-sauce-tests

Automated UI tests for [Helix.cs](https://helix-cx.vercel.app/) — an AI-powered customer health scoring engine — running on **Sauce Labs**.

---

## Why this exists

I built Helix.cs as a portfolio tool demonstrating how a CSM thinks about account health at scale. These tests exist because talking about test automation in a customer conversation is very different from having run it yourself.

Writing Selenium tests against my own app gave me firsthand experience with what engineering teams go through — test flakiness, async rendering, dynamic state, and the value of a reliable cross-browser cloud. That makes me a more credible partner when a customer is evaluating whether Sauce fits their workflow.

---

## What's being tested

| Suite | What it covers |
|---|---|
| `TestHelixPageLoad` | App shell renders — brand, sidebar, portfolio summary |
| `TestSidebarCategorization` | At Risk / Expansion / Stable grouping and P1/P2/P3 labels |
| `TestAccountSelection` | Clicking accounts updates main panel (React state binding) |
| `TestSignalCards` | All 6 signal cards render with correct labels |
| `TestAnalyzeButton` | Analyze CTA present, enabled, triggers two-phase loading state |
| `TestFooterAndAttribution` | Footer version, Claude attribution, LinkedIn/GitHub links |

---

## Stack

- **Python 3.9+**
- **selenium 4.x** (remote WebDriver)
- **pytest**
- **Sauce Labs OnDemand** (Chrome latest / Windows 11)

---

## Setup

```bash
# Install dependencies
pip install selenium pytest

# Set credentials (never hardcode these)
export SAUCE_USERNAME="your_sauce_username"
export SAUCE_ACCESS_KEY="your_sauce_access_key"
```

Update `test_helix.py` lines 28–29 to read from env vars:

```python
import os
SAUCE_USERNAME   = os.environ["SAUCE_USERNAME"]
SAUCE_ACCESS_KEY = os.environ["SAUCE_ACCESS_KEY"]
```

---

## Run

```bash
pytest test_helix.py -v
```

View results in your [Sauce Labs dashboard](https://app.saucelabs.com) — each run is tagged `helix`, `csm-portfolio`, `selenium`.

---

## App under test

**Helix.cs** — [helix-cx.vercel.app](https://helix-cx.vercel.app/)

- 7-signal weighted health scoring model
- Real company accounts (Netflix, Oracle, Anthropic, FedEx, etc.)
- Two-call Claude API split for performance
- Live news integration via Serper API
- P1/P2/P3 sub-prioritization within At Risk / Expansion / Stable categories

Source: [github.com/westineehn/helix-cx-local](https://github.com/westineehn/helix-cx-local)

---

Built by [Westin Eehn](https://linkedin.com/in/westineehn)
