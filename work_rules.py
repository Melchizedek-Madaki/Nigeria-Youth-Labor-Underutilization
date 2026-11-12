"""Descriptive pay/work explorer and transparent rule-based examples."""
from pathlib import Path
import re
import numpy as np
import pandas as pd

OCCUPATIONS = {0: "Armed forces", 1: "Managers", 2: "Professionals",
    3: "Technicians and associate professionals", 4: "Clerical support",
    5: "Service and sales workers", 6: "Skilled agricultural, forestry and fishery workers",
    7: "Craft and related trades", 8: "Plant/machine operators and assemblers", 9: "Elementary occupations"}
INDUSTRIES = dict(zip("ABCDEFGHIJKLMNOPQRSTU", ["Agriculture, forestry and fishing", "Mining and quarrying",
    "Manufacturing", "Electricity and gas", "Water, sewerage and waste", "Construction",
    "Wholesale/retail trade and vehicle repair", "Transport and storage", "Accommodation and food services",
    "Information and communication", "Finance and insurance", "Real estate", "Professional and technical activities",
    "Administrative/support services", "Public administration and defence", "Education", "Health and social work",
    "Arts, entertainment and recreation", "Other services", "Household employment/own-use production",
    "Extraterritorial organisations"]))

def occupation(value):
    if pd.isna(value):
        return "Not recorded"
    try:
        number = float(value)
        if number.is_integer():
            return OCCUPATIONS.get(int(number), f"Unmapped occupation code {int(number)}")
    except (ValueError, TypeError):
        pass
    return re.sub(r"^\d+\s+", "", str(value))

def industry(value):
    if pd.isna(value):
        return "Not recorded"
    text = str(value).strip()
    return INDUSTRIES.get(text.upper(), re.sub(r"^\d+\s+", "", text))

def weighted_median(values, weights):
    valid = values.notna() & weights.notna() & weights.gt(0)
    v, w = values[valid], weights[valid]
    if v.empty:
        return np.nan
    if w.eq(1).all():
        return float(v.median())
    order = np.argsort(v.to_numpy(), kind="stable")
    return float(v.iloc[order].to_numpy()[np.searchsorted(w.iloc[order].cumsum().to_numpy(), w.sum() / 2)])

def money(value):
    return "Not available" if pd.isna(value) else f"₦{value:,.0f}"

def share(frame, mask):
    return 100 * frame.loc[mask, "weight"].sum() / frame.weight.sum() if frame.weight.sum() else np.nan

def evaluate_work(employed, searching, available, paid_status, pay, hours, wants_more, can_more, threshold):
    """Explain the existing project rules; this does not call or retrain the model."""
    if not employed:
        return ("Unemployed", ["No job, actively searching and available to start."]) if searching and available else (
            "Outside this three-class assessment", ["No job, but the search and availability conditions are not both met."])
    reasons = []
    if hours is not None and hours < 40 and wants_more and can_more:
        reasons.append("Hours shortfall: under 40 hours, wants more hours and is available.")
    if paid_status == "Unpaid":
        reasons.append("Unpaid work: explicitly receives no payment.")
    known_pay = paid_status == "Paid" and pay is not None and 1000 <= pay <= 5_000_000
    if known_pay and pay < threshold:
        reasons.append(f"Low pay: {money(pay)} per month is below the quarter's {money(threshold)} threshold.")
    if reasons:
        return "Underemployed (project definition)", reasons
    if not known_pay:
        return "Unresolved", ["Pay is unknown or outside the notebook's reviewed range of ₦1,000–₦5,000,000. "
                              "Without another confirmed condition, the project leaves this case unresolved."]
    return "Adequately employed (project definition)", ["None of the project's confirmed hours, unpaid-work or low-pay conditions applies."]

