# 🐍 pliskin_framework

[![Tests](https://github.com/icekingoz/pliskin_framework/actions/workflows/tests.yml/badge.svg)](https://github.com/icekingoz/pliskin_framework/actions/workflows/tests.yml)
[![Allure Report](https://img.shields.io/badge/report-Allure-brightgreen)](https://icekingoz.github.io/pliskin_framework/)
[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/playwright-1.50-2EAD33)](https://playwright.dev/python/)

**A Playwright + pytest test framework that tests two things and doesn't lie about either.**

📊 **[Live test report →](https://icekingoz.github.io/pliskin_framework/)** — published on every push, with trend history.

<p align="center">
  <img src="docs/snake.jpg" alt="Snake Plissken, unimpressed" width="520">
  <br>
  <em>"I heard you were dead."</em><br>
  <sub>Every stakeholder, about the test suite, the moment one badge goes red.<br>
  Kurt Russell as Snake Plissken — <em>Escape from New York</em> (1981), dir. John Carpenter.</sub>
</p>

> 🐍 **Why "pliskin"?** Because the job is the same: go into a hostile environment nobody else wants to enter, retrieve the thing, get out before the timer hits zero. Also because `test_framework_final_v2` was taken.

---

## 🎯 What's in the box

| Suite | Target | What it does |
| :--- | :--- | :--- |
| **UI** | [SauceDemo](https://www.saucedemo.com) | Login, inventory, cart — driven through Page Objects |
| **API** | [restful-booker](https://restful-booker.herokuapp.com/apidoc/index.html) | Auth, health check, full booking CRUD — driven through Service Clients |

Two suites, one repo, **zero shared state**. The API suite doesn't import Playwright, so it runs without a browser anywhere on the machine. That's not an accident — it's the reason CI gives you an API signal in seconds instead of waiting two minutes for Chromium to install.

---

## ⚡ Quick start

```bash
git clone https://github.com/icekingoz/pliskin_framework.git
cd pliskin_framework

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium          # UI only — skip it if you're just running API

pytest                                # everything
```

No `.env` needed. Every value has a working default, because a framework that requires a twelve-step setup ritual before the first green test is a framework nobody runs. Copy `.env.example` → `.env` only when you want to point it somewhere else.

```bash
pytest -m api                  # API only — no browser required
pytest -m ui                   # UI only
pytest -m smoke                # the "is anything on fire" subset
pytest --headed --slowmo 500   # watch the browser actually do the thing
```

---

## 🏗️ Architecture

```
pliskin_framework/
├── pages/          # HOW to talk to a browser      (Page Objects)
├── api/            # HOW to talk to HTTP           (Service Clients + request builders)
├── support/        # HOW to attach failure evidence
├── scripts/        # CI glue that deserved to be testable
├── conftest.py     # fixtures BOTH suites need
└── tests/
    ├── ui/         # WHAT should be true in the browser  (+ ui-only fixtures)
    └── api/        # WHAT should be true over HTTP       (+ api-only fixtures)
```

Three rules hold the whole thing together:

1. **`pages/` and `api/` describe capability. `tests/` describes truth.** One says *how to click the button* or *how to POST the booking*. The other says *what should have happened*. Mixing them is how you end up with a 400-line test you can't read.
2. **Nothing in `pages/` or `api/` ever asserts.** More on this below, because it's the one people fight me on.
3. **Conftests are layered, not stacked.** Root holds what both suites need. `tests/ui/conftest.py` holds the Playwright stuff. `tests/api/conftest.py` holds the HTTP stuff. Neither can see the other's — which is *structurally* why the API suite can't accidentally grow a browser dependency.

---

## 🧠 Design decisions, and why

### Service Clients, not Page Objects, for the API

restful-booker has no UI. It's an API. A "Page Object" for a REST endpoint is cargo cult. The equivalent pattern is a **Service Client**: one class per resource, wrapping its endpoints.

```python
booking_client.create(payload)      # POST /booking
booking_client.update(id, p, token) # PUT  /booking/:id
booking_client.delete(id, token)    # DELETE /booking/:id
```

### Clients return responses. They never raise.

```python
def create(self, payload):
    return self._post(self.PATH, json=payload)   # that's it. no raise_for_status()
```

A client that calls `raise_for_status()` is a client that **can never test a 404**. The moment you want to assert on an error case, you're fighting your own abstraction. The client's job is to make the call. Judgement lives in the test, where you can read it.

### Page Objects are stateless

They hold one thing: the `page` handle. No cached element handles, no test data, no assertions. Locators are lazy properties that re-resolve on every access, which is why this survives `pytest-xdist` instead of exploding in six different ways at once.

### Test data is built, not typed

```python
build_booking()  # → {"firstname": "Ozzy", "lastname": "Pliskin-1d420701", ...}
```

Two things earn their keep here:

**Dates are relative.** Every tutorial on the internet hardcodes `2018-01-01`. Those bookings are now years in the past, and any date-filter assertion built on them stopped meaning anything a long time ago. Here, check-in is tomorrow. Always.

**Surnames are unique per call.** restful-booker is a *public* sandbox. Hardcode `"Jim Brown"` and you're sharing a namespace with every other person following the same tutorial today. Your name-filter test will fail for reasons that have nothing to do with your code, and you'll spend an afternoon on it.

### Fixtures clean up after themselves

```python
@pytest.fixture
def created_booking(...):
    booking_id = booking_client.create(payload).json()["bookingid"]
    yield booking_id, payload
    booking_client.delete(booking_id, auth_token)   # ← the entire point
```

**If your suite can't run twice in a row and give the same answer, it isn't a test suite. It's a one-shot script with ambitions.** This teardown is the difference.

Corollary: **no test asserts on data it didn't create.** No `GET /booking/1`. No asserting on total counts. Strangers are creating and deleting bookings while your suite runs — assert on membership, never on totals.

---

## 🐛 restful-booker's greatest hits

Documented behaviour that looks exactly like bugs. Asserted as-is, with comments explaining why, because "fixing" these gives you a red suite against a healthy service:

| Endpoint | Does | Should probably |
| :--- | :--- | :--- |
| `DELETE /booking/:id` | returns **201 Created** | 204, or literally anything else |
| `GET /ping` | returns **201 Created** | 200 |
| `POST /auth` with garbage | returns **200 OK** + `{"reason": "Bad credentials"}` | 401 |

That last one is the genuinely dangerous one. Assert `status_code == 200` on auth and your test passes with *no token at all*. The suite checks for the token, not the status code.

---

## 🔍 When things fail

Green tests are easy. This is the part that actually matters.

> *"You going to kill me, Snake?"*
> *"Not now. I'm too tired."*
>
> Same energy as debugging a failing suite at 5pm. Which is exactly why the failure output has to do the work for you.

**UI failure** → screenshot, final URL, and full DOM snapshot attached to the report. Plus Playwright's own trace, video, and screenshot on the failing test only, so passing runs cost nothing.

**API failure** → every HTTP request and response from that test, attached to the report. Method, URL, headers, bodies, timing.

```
--> PUT https://restful-booker.herokuapp.com/booking/42
    headers: {'Content-Type': 'application/json', 'Cookie': '<redacted>'}
    body:    {"firstname": "Updated", ...}
<-- 403 (0.184s)
```

Auth headers are redacted before anything reaches a published report, because the report is on the public internet and shipping your token to GitHub Pages would be a memorable way to learn that lesson.

`assert 200 == 201` tells you a test broke. This tells you *why*, without re-running anything locally.

---

## 🤖 CI

Three jobs on every push:

**`api`** — no browser install. Seconds, not minutes.
**`ui`** — Chromium, traces retained on failure.
**`report`** — merges both suites, generates Allure, publishes to GitHub Pages with history carried forward so the trend graph actually trends.

The report job runs with `if: always()`. A report that only publishes when everything passed is useless, because the run you most want to look at is the one that failed.

Every run also writes a pass/fail table straight onto the Actions summary page — no clicking, no downloading, no unzipping.

> 💡 There's no Docker action in this pipeline. The popular Allure action builds a container on every run, which is slow and dies whenever Docker Hub feels like rate-limiting you. Downloading the Allure CLI and running it is four lines of shell and it doesn't have moods.

---

## 🚧 Not done yet

Because a README that pretends a project is finished is the least trustworthy document in the repo:

- [ ] **Negative tests** — `403` on unauthenticated PUT, `404` on missing booking, bad-credentials handling. Highest-value gap on this list.
- [ ] **Parallel execution** — `pytest-xdist`. The Page Objects are built for it; that claim deserves proof.
- [ ] **Broader UI coverage** — full checkout, plus SauceDemo's `locked_out_user` and `problem_user`.
- [ ] **`ruff` + `pre-commit`**, enforced in CI.
- [ ] **Response schema validation** — catches contract drift that field-by-field asserts miss.

---

## 🛠️ Stack

`pytest` · `playwright` · `requests` · `allure-pytest` · `pytest-html` · `python-dotenv` · GitHub Actions

---

<sub>Built against two public sandboxes that owe me nothing and are occasionally down. If a run is red, check the target's pulse before checking mine. 🫡</sub>

<sub>*The name's Plissken.* 🐍</sub>
