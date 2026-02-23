"""Configuration from environment variables."""

from __future__ import annotations

import os

ADS_API_URL: str = os.environ.get("ADS_API_URL", "https://api.adsabs.harvard.edu")
