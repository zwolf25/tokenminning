# Case Study: Web Scraping Escalation Ladder

**Problem:** Web content extraction has wildly different requirements — some pages are static HTML, others are JS-heavy SPAs, some have Cloudflare/anti-bot protection, some need search + crawl + monitor workflows, some need authenticated interaction. No single tool handles all cases efficiently. Defaulting to one approach (e.g., "just use Playwright" or "just use Firecrawl") burns tokens, credits, or time on the wrong tool for the job.

**Solution:** A 7-level escalation ladder that starts with the cheapest, most targeted tool and escalates only when the current level fails. Each level has a specific, documented failure mode that triggers the next level — no guessing, no overkill.

---

## The Ladder

```
LEVEL 1: firecrawl search --scrape
    │  Discover + extract in one call (2 credits + scrape credits)
    │  ✅ Best for: "Find me articles about X and give me the content"
    ▼  Failure: Need specific URL, not search; or need more control

LEVEL 2: firecrawl scrape
    │  Known URL → clean markdown (JS-rendered SPAs supported)
    │  ✅ Best for: "Get content from this specific page"
    ▼  Failure: Credits exhausted; or page blocks Firecrawl

LEVEL 3: firecrawl-cached scrape
    │  Exact-match URL cache, 7-day TTL, zero credits on hit
    │  ✅ Best for: Re-fetching competitor profiles, docs, historical pages
    ▼  Failure: Cache miss (new URL); or time-sensitive content

LEVEL 4: scrapling fast path
    │  Local, free, single-URL fetch via HTTP + HTML parsing
    │  ✅ Best for: Credits exhausted; most static/JS-rendered pages
    ▼  Failure: 403, Cloudflare, anti-bot, empty/garbage content

LEVEL 5: scrapling --stealth
    │  Local, free, real browser (Patchright/Chromium), fingerprint spoofing,
    │  Cloudflare Turnstile bypass — ~3-5s per fetch
    │  ✅ Best for: Anti-bot pages, Cloudflare challenges, LinkedIn public pages
    ▼  Failure: Behavioral/session-based detection (rare)

LEVEL 6: webclaw --crawl / --map / --diff
    │  Local, free, bulk site discovery (crawl/map/diff) — static pages only
    │  ✅ Best for: Credits exhausted + need bulk discovery, not single URL
    ▼  Failure: Needs JS rendering, auth, or anti-bot bypass

LEVEL 7: playwright-browser / playwright-test
    │  Local browser automation — full control, auth, interaction, E2E tests
    │  ✅ Best for: Logged-in sessions, complex interactions, test code generation
    ▼  Failure: Scale (not for bulk crawl); maintenance overhead
```

---

## Decision Logic (Auto-Enforced by Skills)

The `firecrawl` skill **embeds this ladder as executable fallback logic**:

```bash
# Firecrawl failed? Fall back to Scrapling or webclaw
# Three distinct failure modes:

# 1. Credits exhausted, single-URL fetch → Scrapling fast path first
~/.claude/tools/scrapling/.venv/bin/python ~/.claude/tools/scrapling/scrapling_fetch.py "<url>"

# 2. Blocked by page (403, Cloudflare, bot-detection) → Scrapling STEALTH path
~/.claude/tools/scrapling/.venv/bin/python ~/.claude/tools/scrapling/scrapling_fetch.py --stealth "<url>"

# 3. Credits exhausted, crawl/map/diff need → webclaw (NOT Scrapling)
webclaw "<url>" --crawl --format markdown
webclaw "<url>" --map

# Do NOT silently fall back to WebFetch — no anti-bot handling, hits same block
```

**The skill enforces:** "Do not stop and do not silently switch to WebFetch."

---

## Tokenminning Principles Applied

| Principle | How the Ladder Embodies It |
|-----------|----------------------------|
| **Retrieve don't preload** | Start with targeted fetch (`scrape`), not bulk crawl. `search --scrape` combines discover + extract. `map` finds URLs before scraping — never crawl blindly. |
| **Optimize context not complexity** | Every level returns **clean markdown** (not raw HTML, not DOM, not screenshots). `scrape --only-main-content` strips nav/footer. `scrapling` outputs markdown via `html2text`. Context stays dense. |
| **Compress don't repeat** | `firecrawl-cached` eliminates repeated fetches for stable content (7-day TTL). `monitor` replaces repeated manual scrapes with scheduled diffs. |
| **Eliminate context debt continuously** | Hard rule in skill: "Never `Read` raw HTML into context." Every tool outputs markdown to file → model operates on file path (stub). |
| **Escalation ladder** | 7 levels, each with a *specific, documented failure mode* that triggers the next. No "try everything and see what works." |
| **Design systems not prompts** | The ladder is encoded in the `firecrawl` skill's fallback section — executable, versioned, not a prompt convention. |
| **Stub Pattern** | All tools: `-o .firecrawl/page.md` → model sees `WROTE .firecrawl/page.md (12K chars)`, not the content. |

---

## Measured Impact

| Scenario | Naive Approach | Ladder Approach | Savings |
|----------|----------------|-----------------|---------|
| **Competitor profile (re-fetch weekly)** | `firecrawl scrape` every time | `firecrawl-cached` → 0 credits after first | **100% credit savings on repeat** |
| **Pricing page monitor** | Manual scrape daily | `firecrawl monitor` → diff only on change | **~95% fewer fetches** |
| **Credits exhausted mid-research** | Stop / wait / pay more | Auto-fallback to Scrapling (free, local) | **Unblocked, $0** |
| **Cloudflare-protected docs** | Playwright (slow, heavy) | `scrapling --stealth` (3-5s, free) | **~10x faster, free** |
| **Bulk docs section (50 pages)** | 50x `scrape` calls | `crawl` or `webclaw --crawl` (1 call) | **~98% fewer API calls** |
| **Search + extract top 10 results** | `search` → 10x `scrape` | `search --scrape --limit 10` (1 call) | **90% fewer calls** |

---

## Tool Capability Matrix

| Capability | Firecrawl | Scrapling Fast | Scrapling Stealth | Webclaw | Playwright |
|------------|-----------|----------------|-------------------|---------|------------|
| Single URL → markdown | ✅ | ✅ | ✅ | ✅ (static) | ✅ |
| JS rendering | ✅ | ✅ (limited) | ✅ | ❌ | ✅ |
| Cloudflare/anti-bot bypass | Partial | ❌ | ✅ | ❌ | ✅ (with stealth) |
| Web search | ✅ | ❌ | ❌ | ❌ | ❌ |
| Map (URL discovery) | ✅ | ❌ | ❌ | ✅ | ❌ |
| Crawl (bulk extract) | ✅ | ❌ | ❌ | ✅ (static) | ❌ |
| Monitor (change detection) | ✅ | ❌ | ❌ | ✅ (diff) | ❌ |
| Interact (clicks, forms) | ✅ | ❌ | ❌ | ❌ | ✅ |
| Authenticated sessions | ✅ (interact) | ❌ | ❌ | ❌ | ✅ |
| E2E test code generation | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Cost** | Credits | **Free** | **Free** | **Free** | **Free (local)** |
| **Speed** | ~1-3s | ~0.5-1s | ~3-5s | ~1-10s | ~5-30s |

---

## Workflow Patterns

### Pattern 1: Research a Topic (Most Common)
```bash
# 1. Search + scrape top results in one call
firecrawl search "ServiceChannel competitor pricing" --scrape --limit 5 -o .firecrawl/search.json

# 2. If need deeper: map a specific site for more URLs
firecrawl map https://competitor.com --search "pricing" -o .firecrawl/map.json

# 3. Scrape specific URLs from map
firecrawl scrape "https://competitor.com/pricing" -o .firecrawl/pricing.md

# 4. Set monitor if ongoing tracking needed
firecrawl monitor create --name "Competitor Pricing" \
  --goal "Alert when pricing tiers or features change" \
  --page https://competitor.com/pricing --schedule "daily"
```

### Pattern 2: Credits Exhausted → Local Fallback
```bash
# Firecrawl returns insufficient-credits error
# Auto-fallback (encoded in firecrawl skill):

# Try fast path first
~/.claude/tools/scrapling/.venv/bin/python ~/.claude/tools/scrapling/scrapling_fetch.py "https://target.com/page"

# If 403/Cloudflare → stealth
~/.claude/tools/scrapling/.venv/bin/python ~/.claude/tools/scrapling/scrapling_fetch.py --stealth "https://target.com/page"

# If need bulk discovery → webclaw
webclaw "https://target.com" --crawl --format markdown
```

### Pattern 3: Authenticated / Complex Interaction
```bash
# Firecrawl interact for simple post-login
firecrawl scrape "https://app.service.com" --interact '{"actions":[{"type":"click","selector":"#login"}]}'

# Complex: Playwright codegen → test → reuse
npx playwright codegen https://app.service.com
# Record login + navigation → generates .spec.ts
# Refine locators (getByRole > CSS) → add assertions
npx playwright test --headed  # verify
```

### Pattern 4: Competitive Intelligence (Production)
```bash
# 1. Discover competitors
firecrawl search "facility management software competitors 2024" --scrape --limit 10

# 2. Deep extract each competitor (parallel)
firecrawl scrape "https://competitor1.com" -o .firecrawl/c1.md &
firecrawl scrape "https://competitor2.com" -o .firecrawl/c2.md &
# ... wait for all

# 3. Structured extraction for battlecards
firecrawl agent "https://competitor1.com" \
  --prompt "Extract pricing, features, target market, integrations" \
  --schema battlecard.schema.json

# 4. Monitor key pages
firecrawl monitor create --name "Competitor Watch" \
  --goal "Alert on pricing, product, or leadership changes" \
  --scrape-urls "https://c1.com/pricing,https://c2.com/pricing" --schedule "weekly"
```

---

## Anti-Patterns This Ladder Replaces

| Anti-Pattern | Problem | Ladder Fix |
|--------------|---------|------------|
| Default to Playwright for everything | Slow, heavy, overkill for static pages | Start at Level 1-2; escalate only when needed |
| WebFetch for all fetching | No anti-bot, no JS render, no markdown cleanup | Ladder has anti-bot (L5), JS (L2, L5), clean MD (all) |
| Firecrawl for everything | Credits burn fast; blocked by Cloudflare | Auto-fallback to free local tools (L4-L6) |
| Manual re-scraping for monitoring | Wasteful, misses changes between checks | `monitor` (L2) or `webclaw --diff` (L6) |
| Crawl entire site "just in case" | 1000s of pages, most irrelevant | `map --search` → targeted `scrape` |
| No cache for reference content | Re-fetch same competitor profile weekly | `firecrawl-cached` (L3) = free after first |

---

## Environment-Specific Notes (This Machine)

- **Zscaler TLS interception**: Handled automatically — system Python/curl trust the Zscaler root CA. No extra config.
- **Claude Code Bash sandbox**: Network calls from Bash need `dangerouslyDisableSandbox: true` or they fail with TLS errors that *look* like cert problems but aren't. Normal terminal usage unaffected.
- **`example.com` blocked by Zscaler**: Don't use as smoke test. Use `news.ycombinator.com` or real sites.
- **Scrapling venv**: Isolated at `~/.claude/tools/scrapling/.venv/` (Python 3.14, Homebrew). Doesn't touch system Python.
- **Firecrawl cache**: `~/.claude/tools/firecrawl-cache/firecrawl-cached` — exact-match URL, 7-day TTL.

---

## Related Examples

- [`document-processing.md`](document-processing.md) — Local document pipeline (doc-convert, vtt-normalizer, doc-ingest)
- [`skill-tooling-pattern.md`](skill-tooling-pattern.md) — How the skill system encodes this ladder as executable fallback logic

---

## Source Code

- **Firecrawl CLI skills**: `~/.claude/skills/firecrawl*` (40+ sub-skills: search, scrape, map, crawl, monitor, interact, agent, parse, download, QA, research, lead-gen, company-directories, SEO, dashboard, market-research, website-design-clone, workflows)
- **Scrapling**: `~/.claude/tools/scrapling/` (README.md, scrapling_fetch.py, venv)
- **Webclaw**: Local binary (installed via cargo/homebrew)
- **Playwright**: `~/.claude/skills/playwright-browser/`, `~/.claude/skills/playwright-test/`

Each skill: `SKILL.md` contract + Bash CLI → deterministic, composable, versioned.
