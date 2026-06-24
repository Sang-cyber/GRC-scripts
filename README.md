# GRC Automation Scripts

Python scripts for automating GRC (Governance, Risk, and Compliance) workflows — built by [Raj Sanghvi](https://github.com/Sang-cyber).

## Scripts

### 1. `vendor_risk_scorer.py`
Automatically scores third-party vendors based on data access level, business criticality, and control coverage. Outputs a weighted risk score and recommended review cadence.

```bash
python vendor_risk_scorer.py
```

### 2. `policy_gap_analyzer.py`
Compares implemented controls against SOC 2, ISO 27001, or NIST CSF and outputs a gap report with missing controls and remediation priority.

```bash
python policy_gap_analyzer.py
```

### 3. `evidence_collector.py`
Automates collection of audit evidence from REST APIs (AWS Config, Okta, GitHub). Packages results into a timestamped ZIP ready for auditor handoff.

```bash
# Dry run (mock data)
python evidence_collector.py --dry-run

# Live run
python evidence_collector.py --token YOUR_API_TOKEN --output-dir ./output
```

## Requirements

```bash
pip install requests
```

