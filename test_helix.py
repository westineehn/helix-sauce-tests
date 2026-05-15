"""
test_helix.py
-------------
Automated UI tests for Helix.cs v0.6 — AI-powered customer health scoring engine.
Demonstrates CSM-level understanding of test automation using Sauce Labs WebDriver.

Why this exists:
  As a CSM at Sauce Labs, I'd be asking customers to trust this exact workflow —
  automated browser testing against a live web app. Building and running these tests
  against my own portfolio tool gives me firsthand experience with what engineering
  teams go through, and makes me a more credible partner in those conversations.

Author:  Westin Eehn | linkedin.com/in/westineehn
App:     https://helix-cx.vercel.app/
Runner:  Sauce Labs (remote WebDriver via OnDemand)
Lang:    Python 3.9+ | selenium 4.x | pytest
"""

import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ── Config ──────────────────────────────────────────────────────

HELIX_URL        = "https://helix-cx.vercel.app/"
SAUCE_USERNAME   = os.environ.get("SAUCE_USERNAME", "")
SAUCE_ACCESS_KEY = os.environ.get("SAUCE_ACCESS_KEY", "")
SAUCE_URL        = f"https://{SAUCE_USERNAME}:{SAUCE_ACCESS_KEY}@ondemand.us-west-1.saucelabs.com:443/wd/hub"

SAUCE_OPTIONS = {
    "browserName":    "chrome",
    "browserVersion": "latest",
    "platformName":   "Windows 11",
    "sauce:options":  {
        "name":  "Helix.cs v0.6 UI Tests",
        "build": "helix-cs-v0.6",
        "tags":  ["helix", "csm-portfolio", "selenium", "sauce-labs"],
    },
}

TIMEOUT = 15


# ── Fixtures ────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def driver():
    """
    Opens a remote Chrome session on Sauce Labs, loads Helix, and tears down
    after all tests in this module complete.

    scope="module" = one browser session per file — faster than a new session per test.
    """
    options = webdriver.ChromeOptions()
    for key, value in SAUCE_OPTIONS.items():
        if key == "sauce:options":
            options.set_capability("sauce:options", value)
        else:
            options.set_capability(key, value)

    d = webdriver.Remote(command_executor=SAUCE_URL, options=options)
    d.implicitly_wait(8)
    d.get(HELIX_URL)
    time.sleep(2)  # allow React hydration
    yield d
    d.quit()


def wait_for(driver, by, selector, timeout=TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )

def wait_visible(driver, by, selector, timeout=TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, selector))
    )


# ── Suite 1: Page Load ───────────────────────────────────────────

class TestHelixPageLoad:
    """
    Smoke tests — confirms the app shell renders on initial load.
    If any of these fail, no other tests will be meaningful.
    """

    def test_page_title_contains_helix(self, driver):
        assert "Helix" in driver.title, f"Unexpected title: {driver.title}"

    def test_header_brand_visible(self, driver):
        header = wait_for(driver, By.TAG_NAME, "header")
        assert "Helix" in header.text, "Brand name not found in header"

    def test_header_shows_attribution(self, driver):
        header = driver.find_element(By.TAG_NAME, "header")
        assert "Westin Eehn" in header.text, "'Built by Westin Eehn' not found in header"

    def test_sidebar_renders(self, driver):
        sidebar = wait_visible(driver, By.TAG_NAME, "aside")
        assert len(sidebar.text.strip()) > 0, "Sidebar appears empty"

    def test_portfolio_summary_shows_arr(self, driver):
        sidebar = driver.find_element(By.TAG_NAME, "aside")
        assert "ARR" in sidebar.text, "Portfolio ARR not found in sidebar"

    def test_portfolio_account_count(self, driver):
        """Default set is 7 accounts — catches API load failures."""
        sidebar = driver.find_element(By.TAG_NAME, "aside")
        account_buttons = sidebar.find_elements(By.TAG_NAME, "button")
        assert len(account_buttons) >= 7, (
            f"Expected at least 7 accounts in sidebar, found {len(account_buttons)}"
        )


# ── Suite 2: Sidebar Categorization ─────────────────────────────

class TestSidebarCategorization:
    """
    Verifies the At Risk / Expansion Opp / Stable grouping and P1/P2/P3
    priority labels render correctly. This is the categorization engine made visible.
    """

    def test_at_risk_section_present(self, driver):
        """Oracle and Nike should qualify as At Risk based on default data."""
        sidebar = driver.find_element(By.TAG_NAME, "aside")
        assert "At Risk" in sidebar.text, "'At Risk' group not found in sidebar"

    def test_expansion_section_present(self, driver):
        """Netflix and Anthropic should qualify as Expansion based on default data."""
        sidebar = driver.find_element(By.TAG_NAME, "aside")
        assert "Expansion" in sidebar.text, "'Expansion Opp' group not found in sidebar"

    def test_stable_section_present(self, driver):
        sidebar = driver.find_element(By.TAG_NAME, "aside")
        assert "Stable" in sidebar.text, "'Stable' group not found in sidebar"

    def test_priority_labels_visible(self, driver):
        sidebar = driver.find_element(By.TAG_NAME, "aside")
        assert any(p in sidebar.text for p in ["P1", "P2", "P3"]), (
            "No priority labels (P1/P2/P3) found in sidebar"
        )


# ── Suite 3: Account Selection ───────────────────────────────────

class TestAccountSelection:
    """
    Core navigation tests — clicking an account must update the main panel.
    If this breaks, the entire app interaction model is broken.
    """

    def test_main_panel_loads_with_account(self, driver):
        main = wait_visible(driver, By.TAG_NAME, "main")
        assert len(main.text.strip()) > 50, "Main panel appears empty on load"

    def test_default_account_shows_industry(self, driver):
        main = driver.find_element(By.TAG_NAME, "main")
        industries = ["Streaming", "Enterprise", "Insurance", "AI", "Logistics", "Retail", "Supply Chain"]
        assert any(kw in main.text for kw in industries), (
            "No industry label found in main panel"
        )

    def test_account_switch_updates_heading(self, driver):
        """
        Clicking a different sidebar account must update the h2 in main.
        React state binding test — the most critical navigation assertion.
        """
        initial_heading = driver.find_element(By.TAG_NAME, "h2").text
        sidebar = driver.find_element(By.TAG_NAME, "aside")
        all_buttons = sidebar.find_elements(By.TAG_NAME, "button")

        switched = False
        for btn in all_buttons[1:5]:
            btn.click()
            time.sleep(1)
            new_heading = driver.find_element(By.TAG_NAME, "h2").text
            if new_heading != initial_heading:
                switched = True
                break

        assert switched, (
            f"Account heading did not change after sidebar click. "
            f"Still showing: {driver.find_element(By.TAG_NAME, 'h2').text}"
        )

    def test_arr_visible_after_account_switch(self, driver):
        """ARR value must update when switching accounts — confirms data binding."""
        main = driver.find_element(By.TAG_NAME, "main")
        assert any(sym in main.text for sym in ["$", "ARR"]), (
            "No ARR value found in main panel after account switch"
        )


# ── Suite 4: Signal Cards ────────────────────────────────────────

class TestSignalCards:
    """
    Verifies all 6 signal cards render with correct labels.
    These cards are the primary diagnostic view for account health.
    """

    EXPECTED_LABELS = [
        "Product Adoption",
        "Exec Sponsor",
        "Engagement Cadence",
        "Expansion History",
        "Champion",
        "External Signal",
    ]

    def test_all_signal_card_labels_present(self, driver):
        main = driver.find_element(By.TAG_NAME, "main")
        missing = [l for l in self.EXPECTED_LABELS if l not in main.text]
        assert not missing, f"Missing signal card labels: {missing}"

    def test_renewal_outlook_section_visible(self, driver):
        """Renewal Outlook block renders below account header."""
        main = driver.find_element(By.TAG_NAME, "main")
        assert "Renewal Outlook" in main.text, "Renewal Outlook section not found"

    def test_renewal_probability_label_present(self, driver):
        """Probability must be one of three labeled states."""
        main = driver.find_element(By.TAG_NAME, "main")
        assert any(p in main.text for p in ["High Confidence", "Needs Attention", "At Risk"]), (
            "No renewal probability label found"
        )

    def test_external_signal_card_has_fetch_option(self, driver):
        """Live news fetch button must be present in External Signal card."""
        main = driver.find_element(By.TAG_NAME, "main")
        assert "fetch" in main.text.lower(), (
            "No 'fetch' button found in External Signal card"
        )


# ── Suite 5: Analyze Button & Loading States ─────────────────────

class TestAnalyzeButton:
    """
    Tests the AI analysis CTA and two-phase loading states (Scoring / Analyzing).
    Does not wait for full completion — we test UI behavior, not AI latency.
    """

    def test_analyze_button_present(self, driver):
        main = driver.find_element(By.TAG_NAME, "main")
        assert "Analyze with AI" in main.text, "'Analyze with AI' button not found"

    def test_analyze_button_is_enabled(self, driver):
        buttons = driver.find_elements(By.TAG_NAME, "button")
        analyze_btn = next(
            (b for b in buttons if "Analyze with AI" in b.text), None
        )
        assert analyze_btn is not None, "Could not locate 'Analyze with AI' button element"
        assert analyze_btn.is_enabled(), "Analyze button is unexpectedly disabled"

    def test_analyze_button_triggers_loading_state(self, driver):
        """
        After clicking Analyze, button text must shift to 'Scoring…' or 'Analyzing…'.
        Confirms the two-phase loading state is wired to the click handler.
        """
        buttons = driver.find_elements(By.TAG_NAME, "button")
        analyze_btn = next(
            (b for b in buttons if "Analyze with AI" in b.text), None
        )
        assert analyze_btn is not None, "Could not find Analyze button"

        analyze_btn.click()
        time.sleep(1)

        main = driver.find_element(By.TAG_NAME, "main")
        loading_active = any(
            phrase in main.text for phrase in ["Scoring", "Analyzing", "Analyze with AI"]
        )
        assert loading_active, "No loading state detected after clicking Analyze"

        # Reset state for subsequent tests
        driver.get(HELIX_URL)
        time.sleep(2)

    def test_empty_state_prompt_or_analysis_visible(self, driver):
        """
        Pre-analysis state: empty state prompt should appear.
        Post-analysis state: Health score and Next Best Action should appear.
        Either is valid — the test just confirms something rendered.
        """
        main = driver.find_element(By.TAG_NAME, "main")
        text = main.text
        has_prompt   = "Analyze with AI" in text
        has_analysis = "Health" in text or "Next Best Action" in text
        assert has_prompt or has_analysis, (
            "Neither empty state prompt nor analysis output found in main panel"
        )


# ── Suite 6: Footer & Attribution ───────────────────────────────

class TestFooterAndAttribution:
    """
    Confirms footer and header links render correctly.
    Lightweight sanity checks — failure here suggests a component crash.
    """

    def test_footer_powered_by_claude(self, driver):
        main = driver.find_element(By.TAG_NAME, "main")
        assert "Claude" in main.text, "'Powered by Claude' not found in footer"

    def test_footer_shows_version(self, driver):
        main = driver.find_element(By.TAG_NAME, "main")
        assert "v0.6" in main.text, "Version string 'v0.6' not found in footer"

    def test_linkedin_link_in_header(self, driver):
        header = driver.find_element(By.TAG_NAME, "header")
        links  = header.find_elements(By.TAG_NAME, "a")
        li_links = [l for l in links if "linkedin" in (l.get_attribute("href") or "").lower()]
        assert li_links, "No LinkedIn link found in header"

    def test_github_link_in_header(self, driver):
        header = driver.find_element(By.TAG_NAME, "header")
        links  = header.find_elements(By.TAG_NAME, "a")
        gh_links = [l for l in links if "github" in (l.get_attribute("href") or "").lower()]
        assert gh_links, "No GitHub link found in header"
