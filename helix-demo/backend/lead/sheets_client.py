"""
Persists qualified leads to Google Sheets (via gspread) when credentials are
configured, otherwise falls back to appending to data/leads.csv — so this
demoes with zero Google Cloud setup and swaps to a real CRM-like sheet with
just two env vars.
"""
import csv
import os
import time
from backend.lead.config import settings
from backend.lead.models import LeadProfile

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "leads.csv")
CSV_HEADERS = [
    "timestamp", "name", "company", "email", "phone",
    "budget_range", "is_decision_maker", "need_clarity", "timeline",
    "score", "category", "summary",
]


def _ensure_csv():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            csv.writer(f).writerow(CSV_HEADERS)


def _row_from_lead(lead: LeadProfile, score: int, category: str):
    return [
        time.strftime("%Y-%m-%d %H:%M:%S"),
        lead.name or "", lead.company or "", lead.email or "", lead.phone or "",
        lead.budget_range or "", lead.is_decision_maker, lead.need_clarity or "",
        lead.timeline or "", score, category, lead.summary,
    ]


def save_lead(lead: LeadProfile, score: int, category: str):
    row = _row_from_lead(lead, score, category)

    if settings.SHEETS_ENABLED:
        _save_to_google_sheets(row)
    else:
        _ensure_csv()
        with open(CSV_PATH, "a", newline="") as f:
            csv.writer(f).writerow(row)


def _save_to_google_sheets(row: list):
    import gspread
    from google.oauth2.service_account import Credentials

    creds = Credentials.from_service_account_file(
        settings.GOOGLE_CREDENTIALS_JSON,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(settings.GOOGLE_SHEET_ID).sheet1
    sheet.append_row([str(x) for x in row])
