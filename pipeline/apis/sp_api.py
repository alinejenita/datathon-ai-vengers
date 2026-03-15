"""
pipeline/apis/sp_api.py
────────────────────────
Amazon Selling Partner API client.
SP-API access is not available in this environment — all methods are stubbed
and return empty/mock data so the rest of the pipeline doesn't break.
"""

import requests
from pipeline.config import (
    SP_API_CLIENT_ID, SP_API_CLIENT_SECRET,
    SP_API_REFRESH_TOKEN, SP_API_MARKETPLACE,
)

TOKEN_URL = "https://api.amazon.com/auth/o2/token"
BASE_URL  = "https://sellingpartnerapi-fe.amazon.com"

SP_API_AVAILABLE = bool(SP_API_CLIENT_ID and SP_API_CLIENT_SECRET and SP_API_REFRESH_TOKEN)


def get_access_token() -> str:
    """Exchange refresh token for a short-lived access token."""
    if not SP_API_AVAILABLE:
        raise RuntimeError("SP-API credentials not configured")

    response = requests.post(TOKEN_URL, data={
        "grant_type":    "refresh_token",
        "refresh_token": SP_API_REFRESH_TOKEN,
        "client_id":     SP_API_CLIENT_ID,
        "client_secret": SP_API_CLIENT_SECRET,
    })
    response.raise_for_status()
    return response.json()["access_token"]


def _headers(token: str) -> dict:
    return {
        "x-amz-access-token": token,
        "Content-Type":       "application/json",
    }


def get_sales_metrics(asin: str, start_date: str, end_date: str) -> dict:
    """
    Returns units sold and revenue for a date range.
    start_date / end_date format: "2024-01-01"

    STUBBED: returns empty dict when SP-API is unavailable.
    """
    if not SP_API_AVAILABLE:
        return {}

    token    = get_access_token()
    url      = f"{BASE_URL}/sales/v1/orderMetrics"
    params   = {
        "marketplaceIds": SP_API_MARKETPLACE,
        "interval":       f"{start_date}T00:00:00Z--{end_date}T23:59:59Z",
        "granularity":    "Day",
        "asin":           asin,
    }
    response = requests.get(url, headers=_headers(token), params=params)
    response.raise_for_status()
    return response.json()


def get_inventory(asin: str) -> dict:
    """STUBBED: returns empty dict when SP-API is unavailable."""
    if not SP_API_AVAILABLE:
        return {}

    token    = get_access_token()
    url      = f"{BASE_URL}/fba/inventory/v1/summaries"
    params   = {
        "marketplaceIds": SP_API_MARKETPLACE,
        "details":        True,
        "sellerSkus":     asin,
    }
    response = requests.get(url, headers=_headers(token), params=params)
    response.raise_for_status()
    return response.json()


def get_listing_metrics(asin: str) -> dict:
    """
    Traffic data: sessions, page views, buy box %.
    STUBBED: returns zeroed mock data.
    """
    if not SP_API_AVAILABLE:
        return {"sessions": 0, "pageViews": 0, "buyBoxPercentage": 0.0}

    token = get_access_token()
    # Real implementation would use the Reports API
    url   = f"{BASE_URL}/reporting/2021-06-30/reports"
    return {"sessions": 0, "pageViews": 0, "buyBoxPercentage": 0.0}