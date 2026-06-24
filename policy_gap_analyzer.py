"""
Policy Gap Analyzer
====================
Compares your implemented controls against a compliance framework
(SOC 2, ISO 27001, or NIST CSF) and outputs a gap report with
missing controls and remediation priority.

Usage:
    python policy_gap_analyzer.py

Author: Raj Sanghvi
GitHub: https://github.com/Sang-cyber/GRC-scripts
"""

import json
from datetime import datetime, timezone


FRAMEWORK_CONTROLS = {
    "SOC2": {
        "CC6.1":  "Logical and physical access controls",
        "CC6.2":  "Authentication and access provisioning",
        "CC6.3":  "Access removal and role changes",
        "CC7.1":  "System monitoring and anomaly detection",
        "CC8.1":  "Change management process",
        "CC9.1":  "Risk mitigation and vendor management",
        "CC1.1":  "COSO principle — demonstrates commitment to integrity",
        "CC2.1":  "Board oversight of internal controls",
        "CC3.1":  "Risk assessment process",
        "CC4.1":  "Monitoring activities and controls evaluation",
    },
    "ISO27001": {
        "A.5.1":  "Information security policies",
        "A.6.1":  "Internal organization and roles",
        "A.8.1":  "Asset inventory and ownership",
        "A.9.1":  "Access control policy",
        "A.10.1": "Cryptographic controls",
        "A.12.1": "Operational procedures and responsibilities",
        "A.13.1": "Network security management",
        "A.14.1": "Security in development and support processes",
        "A.16.1": "Management of security incidents",
        "A.18.1": "Compliance with legal requirements",
    },
    "NIST_CSF": {
        "ID.AM":  "Asset management",
        "ID.RA":  "Risk assessment",
        "PR.AC":  "Identity management and access control",
        "PR.DS":  "Data security",
        "PR.IP":  "Information protection processes",
        "DE.CM":  "Security continuous monitoring",
        "DE.AE":  "Anomalies and events detection",
        "RS.RP":  "Response planning",
        "RS.CO":  "Communications during response",
        "RC.RP":  "Recovery planning",
    },
}

PRIORITY_LABELS = {
    "High":   "Immediate remediation required (< 30 days)",
    "Medium": "Remediation recommended (30–90 days)",
    "Low":    "Monitor and plan remediation (90+ days)",
}


def analyze_gaps(implemented: list, framework: str) -> dict:
    """
    Compare implemented controls against a framework and return a gap report.

    Args:
        implemented: List of control IDs already in place (e.g. ["CC6.1", "CC7.1"])
        framework:   One of "SOC2", "ISO27001", "NIST_CSF"

    Returns:
        dict with coverage percentage, gaps, and priority.
    """
    controls = FRAMEWORK_CONTROLS.get(framework)
    if not controls:
        raise ValueError(f"Unknown framework: {framework}. Choose from {list(FRAMEWORK_CONTROLS.keys())}")

    required  = set(controls.keys())
    covered   = set(implemented) & required
    gaps      = required - covered
    coverage  = round(len(covered) / len(required) * 100, 1)

    if coverage < 60:
        priority = "High"
    elif coverage < 85:
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "framework":        framework,
        "assessed_at":      datetime.now(timezone.utc).isoformat(),
        "total_controls":   len(required),
        "implemented":      len(covered),
        "gaps_count":       len(gaps),
        "coverage_pct":     coverage,
        "priority":         priority,
        "priority_guidance": PRIORITY_LABELS[priority],
        "gaps": [
            {"control_id": cid, "description": controls[cid]}
            for cid in sorted(gaps)
        ],
        "covered": sorted(covered),
    }


if __name__ == "__main__":
    # Example: SOC 2 assessment
    implemented_controls = ["CC6.1", "CC6.2", "CC7.1", "CC8.1", "CC1.1", "CC3.1"]

    for framework in ["SOC2", "ISO27001", "NIST_CSF"]:
        print(f"\n{'='*50}")
        print(f"Framework: {framework}")
        print(f"{'='*50}")

        # Use matching control IDs per framework for demo
        if framework == "SOC2":
            impl = implemented_controls
        elif framework == "ISO27001":
            impl = ["A.5.1", "A.6.1", "A.9.1", "A.12.1"]
        else:
            impl = ["ID.AM", "PR.AC", "DE.CM", "RS.RP"]

        result = analyze_gaps(impl, framework)

        print(f"Coverage:   {result['coverage_pct']}%  ({result['implemented']}/{result['total_controls']} controls)")
        print(f"Priority:   {result['priority']} — {result['priority_guidance']}")
        print(f"\nGaps ({result['gaps_count']}):")
        for gap in result["gaps"]:
            print(f"  ✗ {gap['control_id']:10}  {gap['description']}")
        print(f"\nCovered:")
        for ctrl in result["covered"]:
            print(f"  ✓ {ctrl}")

    print("\n\nFull JSON (SOC2):\n")
    print(json.dumps(analyze_gaps(implemented_controls, "SOC2"), indent=2))
