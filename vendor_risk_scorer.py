"""
Vendor Risk Scorer
==================
Automatically scores third-party vendors based on questionnaire
responses, inherent risk tier, and control coverage.

Outputs a weighted risk score and recommended review cadence.

Usage:
    python vendor_risk_scorer.py

Author: Raj Sanghvi
GitHub: https://github.com/Sang-cyber/GRC-scripts
"""

import json
from dataclasses import dataclass


@dataclass
class VendorProfile:
    name: str
    data_access: str        # "high" | "medium" | "low"
    criticality: str        # "critical" | "important" | "standard"
    controls_score: float   # 0.0 - 1.0 (1.0 = fully implemented)


WEIGHTS = {
    "data_access": {
        "high":   1.0,
        "medium": 0.6,
        "low":    0.2,
    },
    "criticality": {
        "critical":  1.0,
        "important": 0.6,
        "standard":  0.2,
    },
}

REVIEW_CADENCE = {
    "High":   "Quarterly",
    "Medium": "Bi-Annual",
    "Low":    "Annual",
}


def score_vendor(vendor: VendorProfile) -> dict:
    """
    Calculate a weighted risk score for a vendor.

    Weights:
      - Data access level : 40%
      - Business criticality : 40%
      - Control gap (1 - controls_score) : 20%
    """
    raw_score = (
        WEIGHTS["data_access"][vendor.data_access] * 0.4
        + WEIGHTS["criticality"][vendor.criticality] * 0.4
        + (1 - vendor.controls_score) * 0.2
    )

    if raw_score >= 0.7:
        risk_level = "High"
    elif raw_score >= 0.4:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "vendor":          vendor.name,
        "raw_score":       round(raw_score, 2),
        "risk_level":      risk_level,
        "review_cadence":  REVIEW_CADENCE[risk_level],
        "data_access":     vendor.data_access,
        "criticality":     vendor.criticality,
        "controls_score":  vendor.controls_score,
    }


def score_multiple_vendors(vendors: list) -> list:
    """Score a list of VendorProfile objects and return sorted results."""
    results = [score_vendor(v) for v in vendors]
    return sorted(results, key=lambda x: x["raw_score"], reverse=True)


if __name__ == "__main__":
    # Example vendors
    vendors = [
        VendorProfile("Acme SaaS",       data_access="high",   criticality="critical",  controls_score=0.65),
        VendorProfile("Beta Analytics",  data_access="medium", criticality="important", controls_score=0.80),
        VendorProfile("Gamma Tools",     data_access="low",    criticality="standard",  controls_score=0.95),
        VendorProfile("Delta Payments",  data_access="high",   criticality="critical",  controls_score=0.50),
    ]

    results = score_multiple_vendors(vendors)

    print("\n=== Vendor Risk Assessment Results ===\n")
    for r in results:
        print(f"Vendor:          {r['vendor']}")
        print(f"Risk Score:      {r['raw_score']} ({r['risk_level']})")
        print(f"Review Cadence:  {r['review_cadence']}")
        print("-" * 40)

    print("\nFull JSON output:\n")
    print(json.dumps(results, indent=2))
