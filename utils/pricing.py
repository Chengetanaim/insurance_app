"""
Insurance Pricing Engine
Uses GLM-style factor tables (log-linear multiplicative model) — standard actuarial practice.
Premium = Base Rate × Product of Rating Factors × Loading adjustments
"""

import numpy as np
import json

# ─── BASE RATES (USD per annum) ───────────────────────────────────────────────
BASE_RATES = {
    "Motor":    1_200.0,
    "Life":       800.0,
    "Property": 1_500.0,
    "Health":   2_200.0,
}

# ─── MOTOR RATING FACTORS ─────────────────────────────────────────────────────
MOTOR_FACTORS = {
    "vehicle_age": {
        "0-2 years":   0.85,
        "3-5 years":   1.00,
        "6-10 years":  1.25,
        "10+ years":   1.55,
    },
    "vehicle_use": {
        "Private":     1.00,
        "Commercial":  1.45,
        "Hire":        1.80,
    },
    "driver_age": {
        "18-25": 1.60,
        "26-35": 1.10,
        "36-50": 1.00,
        "51-65": 1.05,
        "65+":   1.20,
    },
    "no_claims": {
        "0 years": 1.00,
        "1 year":  0.90,
        "2 years": 0.82,
        "3 years": 0.75,
        "4+ years":0.68,
    },
    "cover_type": {
        "Third Party Only":        0.40,
        "Third Party Fire & Theft":0.70,
        "Comprehensive":           1.00,
    },
}

# ─── LIFE RATING FACTORS ──────────────────────────────────────────────────────
LIFE_FACTORS = {
    "age_band": {
        "18-30": 0.60,
        "31-40": 0.85,
        "41-50": 1.20,
        "51-60": 1.80,
        "61-70": 2.60,
        "71+":   3.80,
    },
    "gender": {
        "Male":   1.10,
        "Female": 0.92,
        "Other":  1.00,
    },
    "smoker": {
        "Non-Smoker": 1.00,
        "Smoker":     1.65,
        "Ex-Smoker":  1.20,
    },
    "bmi_band": {
        "Underweight (<18.5)":  1.15,
        "Normal (18.5–24.9)":   1.00,
        "Overweight (25–29.9)": 1.10,
        "Obese (30+)":          1.35,
    },
    "sum_assured_band": {
        "$10k–$50k":   0.90,
        "$50k–$200k":  1.00,
        "$200k–$500k": 1.12,
        "$500k+":      1.25,
    },
}

# ─── PROPERTY RATING FACTORS ──────────────────────────────────────────────────
PROPERTY_FACTORS = {
    "property_type": {
        "Residential": 1.00,
        "Commercial":  1.40,
        "Industrial":  1.75,
        "Warehouse":   1.55,
    },
    "construction": {
        "Brick/Concrete":  1.00,
        "Mixed":           1.20,
        "Timber/Zinc":     1.50,
    },
    "security": {
        "Alarm + Guards + Electric Fence": 0.80,
        "Alarm + Electric Fence":          0.88,
        "Alarm Only":                      0.95,
        "No Security":                     1.20,
    },
    "location_risk": {
        "Low Risk Area":    0.85,
        "Medium Risk Area": 1.00,
        "High Risk Area":   1.35,
        "Flood Zone":       1.60,
    },
    "sum_insured_band": {
        "Under $50k":    0.95,
        "$50k–$200k":    1.00,
        "$200k–$500k":   1.08,
        "$500k–$1M":     1.15,
        "Over $1M":      1.25,
    },
}

# ─── HEALTH RATING FACTORS ────────────────────────────────────────────────────
HEALTH_FACTORS = {
    "age_band": {
        "0-18":  0.70,
        "19-30": 0.85,
        "31-45": 1.00,
        "46-60": 1.45,
        "61+":   2.10,
    },
    "plan_type": {
        "Basic":        0.60,
        "Standard":     1.00,
        "Premium":      1.50,
        "Executive":    2.20,
    },
    "pre_existing": {
        "None":              1.00,
        "Hypertension":      1.25,
        "Diabetes":          1.35,
        "Heart Condition":   1.60,
        "Multiple (2+)":     1.85,
    },
    "family_size": {
        "Individual":        1.00,
        "Individual + 1":    1.70,
        "Family (up to 4)":  2.40,
        "Family (5+)":       3.00,
    },
}

ALL_FACTORS = {
    "Motor":    MOTOR_FACTORS,
    "Life":     LIFE_FACTORS,
    "Property": PROPERTY_FACTORS,
    "Health":   HEALTH_FACTORS,
}

# ─── PRICING FUNCTION ─────────────────────────────────────────────────────────

def price_policy(product: str, selections: dict) -> dict:
    """
    Returns a dict with:
        premium        – final annual premium
        base_rate      – starting base rate
        factor_details – list of (factor, selection, value) tuples
        risk_score     – 0-100 normalised risk score
        breakdown      – cumulative premium at each factor step
    """
    factors = ALL_FACTORS[product]
    base = BASE_RATES[product]
    cumulative = base
    factor_details = []
    breakdown = [("Base Rate", base)]

    composite_factor = 1.0
    for factor_name, options in factors.items():
        chosen = selections.get(factor_name)
        if chosen and chosen in options:
            fv = options[chosen]
            composite_factor *= fv
            cumulative = base * composite_factor
            factor_details.append((factor_name.replace("_", " ").title(), chosen, fv))
            breakdown.append((chosen, round(cumulative, 2)))

    # Apply sum-insured / cover amount scalar for property & life
    cover_amount = selections.get("cover_amount", 0)
    if cover_amount and product in ("Property", "Life"):
        rate_on_line = cumulative / max(cover_amount, 1) * 100  # % of SI
        # GLM loading: use 0.5% of SI as floor premium guide
        floor = cover_amount * 0.005
        cumulative = max(cumulative, floor)

    # ── Risk Score: weighted average of factors relative to 1.0 ──
    if factor_details:
        factor_vals = [fv for _, _, fv in factor_details]
        avg_factor = np.mean(factor_vals)
        # Normalise: factor 0.5 = score 10, factor 1.0 = 50, factor 3.8 = 100
        raw_score = (avg_factor - 0.5) / (3.8 - 0.5) * 90 + 10
        risk_score = float(np.clip(raw_score, 5, 100))
    else:
        risk_score = 50.0

    return {
        "premium":        round(cumulative, 2),
        "base_rate":      base,
        "factor_details": factor_details,
        "risk_score":     round(risk_score, 1),
        "breakdown":      breakdown,
        "composite_factor": round(composite_factor, 4),
    }


def get_factor_options(product: str) -> dict:
    return ALL_FACTORS.get(product, {})


def sensitivity_analysis(product: str, base_selections: dict, vary_factor: str) -> list[dict]:
    """Vary one factor across all its options; return list of results."""
    options = ALL_FACTORS[product].get(vary_factor, {})
    results = []
    for option in options:
        sel = {**base_selections, vary_factor: option}
        res = price_policy(product, sel)
        results.append({"option": option, "premium": res["premium"], "risk_score": res["risk_score"]})
    return results


def get_risk_category(risk_score: float) -> tuple[str, str]:
    if risk_score < 30:
        return "Low Risk", "#22c55e"
    elif risk_score < 55:
        return "Moderate Risk", "#f59e0b"
    elif risk_score < 75:
        return "High Risk", "#f97316"
    else:
        return "Very High Risk", "#ef4444"
