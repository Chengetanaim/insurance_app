# 🛡️ InsureIQ — Actuarial Insurance Pricing Platform

A full-featured **Streamlit** web app for GLM-based insurance premium pricing,
built as a data science school project inspired by Claxon Actuaries (Zimbabwe).

---

## Features

| Feature | Description |
|---|---|
| 🔐 Authentication | Register / Login with hashed passwords (SHA-256) |
| 💰 Policy Pricer | Motor, Life, Property & Health — GLM multiplicative model |
| 📁 My Quotes | Save, filter, sort and export quotes to CSV |
| 🔍 Risk Explorer | Sensitivity analysis, factor heatmaps, portfolio simulator |
| 🧠 Model Insights | GLM methodology explanation + full rate tables |
| 👤 Account | Profile management, password change, activity log |

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Open your browser
Streamlit will print a URL like `http://localhost:8501` — open it.

---

## Project Structure

```
insurance_app/
├── app.py                  # Entry point + routing
├── requirements.txt
├── insureiq.db             # SQLite database (auto-created on first run)
├── pages/
│   ├── auth_page.py        # Login / Register UI
│   ├── sidebar.py          # Navigation sidebar
│   ├── dashboard.py        # KPI dashboard
│   ├── pricer.py           # Policy pricing form
│   ├── quotes.py           # Saved quotes manager
│   ├── risk_explorer.py    # Sensitivity & simulation
│   ├── model_insights.py   # GLM methodology
│   └── account.py          # Profile & password
└── utils/
    ├── auth.py             # DB, auth, CRUD helpers
    ├── pricing.py          # GLM pricing engine
    └── styles.py           # Global CSS theme
```

---

## Actuarial Methodology

Premium uses the standard multiplicative GLM formula:

```
Premium = Base Rate × F₁ × F₂ × ... × Fₙ
```

Each factor Fᵢ is derived from rating tables representing risk relativities.
This mirrors real-world actuarial pricing used by insurers in Zimbabwe and globally
(IFRS 17, ZICARP, Solvency II compliant approaches).

---

## Tech Stack
- **Frontend**: Streamlit + Plotly
- **Database**: SQLite (via Python `sqlite3`)
- **Pricing Engine**: Pure Python (NumPy)
- **Auth**: SHA-256 password hashing

---

*Built for academic use. Inspired by Claxon Actuaries, Harare, Zimbabwe.*
