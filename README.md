# VersusHub

A Django comparison site — compare cars, phones, foods, companies, telecoms,
construction firms, electronics, footballers, universities, or clothing
brands head-to-head, with a shareable "A vs B" URL for every matchup.

## What's inside

- **Category** — a group of things you compare (Cars, Phones, Foods…)
- **Spec** — an attribute you compare within a category (Price, RAM, Horsepower…)
- **Item** — one specific thing, with a brand tag, a 0-100 score badge,
  pros/cons, a real logo (see below), and a price
- **SpecValue** — the value of one Spec for one Item
- **Comparison** — a saved A-vs-B matchup with its own permanent URL, a view
  counter, and community vote counts
- **Review** — star ratings + comments on each item

Every comparison lives at a clean, memorable URL like:
`/vs/cars/honda-accord-2025-vs-toyota-camry-2025/`

## Run it locally

```bash
cd versushub
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations compare   # generates the database schema
python manage.py migrate                  # creates the actual tables
python manage.py createsuperuser          # create your admin login
python manage.py seed_demo                # loads ~74 sample items across 10 categories
python manage.py runserver
```

> **Already ran this before?** The models picked up new fields (`logo_url`,
> `photo_credit`, plus everything from earlier updates). Delete `db.sqlite3`
> and any files under `compare/migrations/` except `__init__.py`, then
> repeat the four commands above for a clean slate.

Then open `http://127.0.0.1:8000/` for the site and `/admin/` to manage content.

## The 10 seeded categories

Cars (16 across 15 brands) · Smartphones (6) · Foods (6, Nigerian) ·
Companies (6) · **Telecom Companies** (8, global) · **Construction
Companies** (6) · **Electronics** (8, spanning TVs/laptops/appliances/audio/
wearables) · **Footballers** (6, by achievements) · **Universities** (6,
QS 2026 top ranks) · **Clothing Brands** (6)

## Real brand logos — how they work, and the limits

Every item across 8 of the 10 categories gets a real logo via
[Hunter's free Logo API](https://hunter.io/api/logo) — a no-key, no-signup
service that returns a company's logo from its domain
(`https://logos.hunter.io/nike.com` → Nike's actual logo). It's the
maintained replacement for Clearbit's logo API, which Google/HubSpot shut
down in December 2025.

**Three things to know:**
1. **These are real trademarks.** Hunter's own terms say it plainly: *"The
   logos served through this API are trademarks of their respective owners.
   You are responsible for ensuring your use complies with each trademark
   holder's policies."* Showing a brand's logo purely to identify the real
   product you're comparing (nominative use) is the standard, widely-used
   pattern for comparison sites — but I'm not a lawyer, and this isn't legal
   advice.
2. **Some logos may not resolve.** The templates hide any that fail to load.
   Spot-check the categories that matter most to you.
3. **Footballers deliberately have no photo or logo** — just an initials
   badge. Real people's photos raise likeness/publicity-rights issues beyond
   simple brand-logo nominative use, and a player's "current club" changes
   every transfer window, so rather than guess wrong, we skip both.

## Real subject photos — what changed and what's left

**Companies, Telecom Companies, Construction Companies, and Clothing
Brands (26 items)** now show their real logo full-size on the card instead
of a stock photo. A generic "office building" placeholder wasn't any more
authentic than the picsum photo it replaced — the logo already does the
identification job honestly, the way most B2B/corporate comparison content
actually works.

**Cars, Smartphones, Foods, Electronics, and Universities (42 items)** are
where a real subject photo genuinely adds something, and those still use
picsum placeholders for now. I can't safely auto-source real photos for
these myself — most product photography on the web is copyrighted marketing
material, and I don't have a tool that can both verify a Wikimedia Commons
license *and* extract the actual direct image URL (Commons pages aren't
fetchable by my tools, and Wikipedia strips image URLs on extraction).

**→ See `PHOTO_CHECKLIST.md`** for all 42, each with a direct, pre-built
Wikimedia Commons search link plus notes on which ones are likely to have
good coverage vs. which need extra care. It's about a 30-60 second job per
item once you get into the rhythm — click, check the match, copy the
license-holder's name, paste both the image URL and the credit into
`/admin/`. [Claude for Chrome](https://claude.com/chrome) can also drive
this end-to-end if you'd rather automate the browsing/copying step.

Other legitimate photo sources worth knowing about:
- **Manufacturer press kits** — most car/phone/electronics makers offer
  downloadable press photos for reviewers; check each brand's media page.
- **Your own photography** — especially strong for the Foods category.
  Real, homemade photos of jollof rice or suya would look more authentic
  than *any* stock photo, and it's a nice differentiator.
- **Amazon Product Advertising API** — if you become an approved Amazon
  affiliate, this grants explicit image-usage rights for exactly this kind
  of use case.



## Data accuracy — what's real, what's a placeholder

- **Cars, Smartphones, Foods, Electronics specs** — plausible, representative
  numbers, in the same spirit as the original demo.
- **Companies, Telecom, Construction, Clothing Brands** (revenue, headcount,
  ratings) — illustrative placeholders, **not verified financial data**.
  Replace with sourced figures before publishing these categories live.
- **Footballers** — Ballon d'Or counts are stable, real facts. Goal tallies
  were checked against live sources in early July 2026 (mid-World-Cup) but
  will already be out of date by the time you read this — they move almost
  daily during an active tournament. Double-check before publishing.
- **Universities** — world rankings reflect the QS World University Rankings
  2026 (MIT #1, Imperial College London #2, Stanford #3, Oxford #4, Harvard
  #5 — yes, that order surprised me too, Imperial jumped up this year).
  Acceptance rates, tuition, and Nobel counts are approximate.

## Adding your own content

Everything is managed from `/admin/`, no code needed:
1. Add a **Category**.
2. Add a few **Specs** for it (lower/higher-is-better matters — e.g. price
   should be "lower is better", horsepower "higher is better").
3. Add **Items** — brand, price, score, pros/cons, and set each Spec value
   on the item's edit page. Add a `logo_url` manually if you want a specific
   logo, or leave blank. If you add a real photo, fill in `photo_credit` too
   (most Commons licenses require it) — see `PHOTO_CHECKLIST.md`.
4. Visit the category page and either use the dropdown picker or tick two
   cards in the floating tray.

## Turning on AdSense

1. Get your site approved on Google AdSense first — you need real, live
   content for that.
2. In `versushub/settings.py`, set:
   ```python
   ADSENSE_CLIENT_ID = "ca-pub-your-real-id"
   ADSENSE_ENABLED = True
   ```
3. Every page already has an `.ad-slot` div wired to render AdSense once enabled.

## Before deploying live

- Set `DEBUG = False`, set `ALLOWED_HOSTS` to your real domain, change `SECRET_KEY`.
- Swap SQLite for Postgres if you expect real traffic.
- Run `python manage.py collectstatic` and serve `/static/` via your host or a CDN.
- Common free/cheap hosts that work well with Django: Railway, Render, PythonAnywhere.
- Re-check every placeholder called out above (logos, financials, football
  stats, rankings) before it's public.

## Ideas to grow traffic

- Aim for 15-20+ items per category before launch — thin categories don't rank.
- Write an honest one-line "why it wins" for your most popular duels.
- Submit `/sitemap.xml` to Google Search Console.
- Let visitors vote and review — fresh content on autopilot.
# versushub
