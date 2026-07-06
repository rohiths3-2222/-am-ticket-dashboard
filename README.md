# AM Ticket Performance Dashboard

A static, org-wide live dashboard built to run for free on GitHub Pages.
It reads everything from `data.json` — no backend server needed.

Tracks seller tickets assigned to Account Managers against these SLAs:
- First response within **24 hours** of raise
- A response at least every **72 hours** while the ticket stays open
- Tickets open **7+ days** are flagged critical/aging

## Data shape (`data.json`)

```json
{
  "last_updated": "2026-07-05T09:00:00+05:30",
  "ams": ["Rahul Singh", "Priya Nair", "..."],
  "issue_types": ["Payment Delay", "Return/Refund Dispute", "..."],
  "tickets": [
    {
      "ticket_id": "TCK-1000",
      "am": "Rahul Singh",
      "seller_id": "SEL-2000",
      "issue_type": "Payment Delay",
      "raised_date": "2026-06-28T10:00:00",
      "status": "Open",              // or "Closed"
      "closed_date": null,           // ISO datetime once closed, else null
      "first_response_hours": 18.5,  // hours from raise to first AM reply, null if none yet
      "last_response_date": "2026-07-01T14:00:00", // most recent AM reply, null if none yet
      "escalated": false,
      "escalation_id": null          // e.g. "ESC-0001" when escalated
    }
  ]
}
```

Everything else — aging days, breach flags, averages, percentages — is
calculated in the browser from these raw fields, so `data.json` only ever
needs to hold the source-of-truth ticket records.

**Note on duplicates:** raw exports from the escalation tool have one row
per shipment item, so the same Escalation ID can repeat several times.
`convert_data.py` deduplicates by Escalation ID before writing `data.json`
(earliest first-response time and latest comment time are kept across the
duplicate rows for that ticket).

**Date filter:** the dashboard has a "Raised between" date range filter
that combines with the AM dropdown — both the AM ticket-count chart and
all breach/aging percentages respect whichever range is selected.

## 0. Create the GitHub repo and push this code

1. Go to your GitHub organization → **New repository** (e.g.
   `github.com/orgs/<your-org>/repositories/new`).
   - Name: `am-ticket-dashboard` (or whatever you prefer)
   - Visibility: **Public** — this is required for free GitHub Pages
     hosting to be reachable by your team at all (private-repo Pages
     needs a paid GitHub plan). Public means anyone on the internet
     *could* find the URL, which is exactly why step 5 below (Cloudflare
     Access) matters if this data shouldn't be open to the public.
   - Don't initialize with a README (you already have one).
2. On your own machine, unzip this folder, then from inside it:
   ```bash
   git init
   git add .
   git commit -m "Initial dashboard"
   git branch -M main
   git remote add origin https://github.com/<your-org>/am-ticket-dashboard.git
   git push -u origin main
   ```

## 1. Publish it (5 minutes)

1. Repo must be **Public** — free GitHub Pages hosting doesn't serve
   private repos (see step 0).
2. Push these files to the repo's `main` branch.
3. Go to **Settings → Pages** → set source to `main` branch, `/ (root)`.
4. GitHub gives you a URL like `https://yourorg.github.io/repo-name/`.
   That URL loads `index.html` — a single file containing both the email
   gate and the dashboard. Entering a `@flipkart.com` address reveals the
   dashboard in place, no page navigation. Share that root link with the
   organization; anyone with it can view the
   dashboard, no login needed (unless you restrict the repo further).

That alone gives you a shareable dashboard. Right now it's showing
**sample data** in `data.json` so you can see the layout working.

## 2. Make the data live

`app.elite.ekartlogistics.in` is a login-gated portal, so nothing can pull
from it automatically without one of these two paths:

### Path A — Official API/webhook (recommended)
Ask your Ekart account manager or integrations contact whether the Elite
portal offers API or webhook access for partners. If yes:
1. Add the token as a repo secret: **Settings → Secrets and variables →
   Actions → New repository secret** → name it `EKART_API_TOKEN`.
2. Edit `scripts/fetch_data.py` to call the real endpoint and reshape the
   response into the fields `index.html` expects (see comments in that
   file).
3. The included workflow (`.github/workflows/refresh-data.yml`) already
   runs that script every 30 minutes and commits the refreshed
   `data.json` — the dashboard picks it up automatically since the page
   re-fetches `data.json` every 5 minutes.

### Path B — No API, portal login only
Don't script a login with a stored password against the portal — that's
both a security risk and likely against Ekart's terms. Instead:
- Check if the portal can email/export a scheduled report (many
  logistics dashboards support this).
- Point that export at a place this repo can read safely (e.g. a shared
  Google Sheet you convert to CSV, or a folder your team controls), and
  adjust `scripts/fetch_data.py` to read from there instead of an API.
- Or, simplest for now: someone manually exports the numbers weekly/daily
  and updates `data.json` (even by hand, or by pasting into the JSON
  file) — the dashboard will render whatever is in there.

## 4. Upload a new export from the dashboard

There's an "Upload new ticket export" card at the top of the dashboard.
Choosing a `.xlsx` file there re-parses it in the browser (same column
mapping and dedup logic as `scripts/convert_excel_export.py`) and
refreshes every number, chart, and table immediately — no page reload
needed.

**Important:** this update only happens in the browser of the person who
uploaded the file. It does not change `data.json` in the repo, so it
won't automatically appear for other people viewing the GitHub Pages
link. Once you're happy with the uploaded data, click **Download
data.json** (appears after a successful upload) and commit that file to
the repo — that's what makes it visible to everyone. A true one-click
org-wide update without that manual commit step needs a small backend or
a triggered GitHub Action — ask if you want that built out.

## 3. Customize
- `index.html` — single file containing everything: the email gate
  (`#gateOverlay`), the dashboard (`#dashboardRoot`), all styles, and all
  logic (uses Chart.js + SheetJS from a CDN). The gate hides/shows the
  dashboard div directly — there's no second page or navigation.
- `data.json` — the ticket records. Add/edit tickets here; the dashboard
  recalculates every metric automatically.

## 5. Email gate (light, not a real security boundary)

`index.html` shows an email-gate overlay first. Entering a work email
ending in `@flipkart.com` hides the overlay and reveals the dashboard in
the same page (no navigation to a second file). Access is remembered in
that browser (`localStorage`) so people aren't asked again next visit,
with a "Switch account" link in the dashboard header to reset it.

**Be clear-eyed about what this is:** the check runs entirely in the
visitor's browser. It stops casual/accidental access and mistyped links,
but anyone who opens dev tools, edits local storage, or just reads the
page source can bypass it — there's no real identity verification behind
it. Since this repo needs to be **public** for free GitHub Pages hosting,
that also means the raw content is technically reachable by anyone who
has or guesses the URL, gate or not.

If this dashboard ever holds data you don't want reachable by a
determined outsider, upgrade to **Cloudflare Access** in front of it —
it verifies the person actually controls a `@flipkart.com` inbox via a
one-time emailed code before serving any content at all, works with the
exact same static files, and is free for teams under 50 people. Say the
word and I'll walk through that setup instead/in addition.


## Files
```
index.html                      everything: email gate + dashboard, single file
data.json                       ticket records it renders (sample data for now)
scripts/fetch_data.py           template script to populate data.json from a real source
scripts/convert_excel_export.py converts a raw ticket-tool Excel export into data.json
.github/workflows/refresh-data.yml   scheduled job that runs fetch_data.py and commits the result
```

