# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IOL Dashboard Lite is a minimalist open-source dashboard for InvertirOnline.com (Argentine broker). Read-only MVP: portfolio visualization, market quotes, and P&L tracking via the IOL Public API v2.

**Scope constraint:** No trading/write operations - read-only access only.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Run tests
pytest

# Run single test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=src

# Lint
ruff check .

# Format
black .
```

## Architecture

```
app.py              # Streamlit entry point
src/
  auth.py           # Authentication only
  api_client.py     # HTTP layer only
  portfolio.py      # Business logic only
  ui.py             # Streamlit components only
```

**Data flow:** `app.py` → `auth.py` (get tokens) → `api_client.py` (fetch data) → `portfolio.py` (process) → `ui.py` (render)

## Code Style

- Python 3.10+ with type hints
- Google-style docstrings
- Black formatting (88 char line limit)
- Import order: stdlib → third-party → local

## IOL API

- **Base URL:** `https://api.invertironline.com`
- **Auth:** Bearer token (15min TTL)
- **Rate limit:** ~120 req/min (undocumented)
- **Key endpoints:**
  - `POST /api/v2/token` - authentication
  - `GET /api/v2/portafolio/argentina` - portfolio
  - `GET /api/v2/Cotizaciones/acciones/argentina/Todos` - quotes

## Key Patterns

- Wrap API calls in try/except, show errors via `st.error()`
- Cache API responses with `st.cache_data` (always set TTL)
- Use `st.session_state` to avoid unnecessary re-renders
- Lazy load: fetch data only on user action

## Configuration

- Copy `.env.example` to `.env` and add IOL credentials
- Tokens are stored locally in `tokens_iol.json` (gitignored)

## Git

- Conventional commits: `feat:`, `fix:`, `docs:`
- Branches: `feature/*`, `fix/*`
