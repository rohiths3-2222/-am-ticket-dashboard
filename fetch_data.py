"""
Fetch the latest logistics data and overwrite data.json.

This file is a TEMPLATE. Fill in ONE of the two paths below depending on
what access your organization actually has to app.elite.ekartlogistics.in.

PATH A — You have an official Ekart API / webhook (ask your Ekart account
manager or integrations contact whether one exists for the Elite portal).
    1. Store the API token as a GitHub Actions secret named EKART_API_TOKEN.
    2. Replace the placeholder request below with the real endpoint.

PATH B — You only have portal login access, no API.
    Do NOT try to script a login to app.elite.ekartlogistics.in with a
    stored password — that risks violating Ekart's terms of service and
    is a poor place to keep credentials. Instead:
    1. Check whether the portal has a "scheduled report" or "export to
       email" feature.
    2. Have that export land somewhere this script CAN read safely, e.g.
       a shared Google Sheet or an emailed CSV saved to a folder your
       org controls, then parse that here instead of calling Ekart directly.
    3. Ask Ekart support whether Elite offers a data feed for partners —
       many logistics platforms do, even if it's not self-serve.
"""

import json
import os
import sys

import requests

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data.json")


def fetch_from_api():
    token = os.environ.get("EKART_API_TOKEN")
    if not token:
        print("EKART_API_TOKEN not set — skipping fetch, keeping existing data.json")
        sys.exit(0)

    # TODO: replace with the real Ekart Elite API endpoint once you have one
    resp = requests.get(
        "https://api.example-placeholder.ekartlogistics.in/v1/dashboard-summary",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    raw = fetch_from_api()

    # TODO: reshape `raw` into the structure index.html expects:
    # { "last_updated", "kpis", "shipment_status", "order_trend_7d",
    #   "sla_by_hub", "cod_reconciliation" }
    data = raw

    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
