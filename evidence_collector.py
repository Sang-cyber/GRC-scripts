"""
Evidence Collection Workflow
=============================
Automates the collection of audit evidence from REST APIs
(AWS Config, Okta, GitHub). Packages results into a timestamped
ZIP with a manifest — ready for auditor handoff.

Usage:
    python evidence_collector.py --token YOUR_API_TOKEN

Author: Raj Sanghvi
GitHub: https://github.com/Sang-cyber/GRC-scripts
"""

import json
import zipfile
import argparse
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    raise ImportError("Please install requests: pip install requests")


# ── Source configuration ──────────────────────────────────────────────────────
# Replace these URLs with your actual API endpoints

SOURCES = {
    "aws_config_rules": {
        "url":         "https://api.example.com/aws/config-rules",
        "description": "AWS Config compliance rules and evaluation results",
    },
    "okta_groups": {
        "url":         "https://api.example.com/okta/groups",
        "description": "Okta group memberships and access assignments",
    },
    "github_merged_prs": {
        "url":         "https://api.example.com/github/merged-prs",
        "description": "GitHub merged pull requests (change management evidence)",
    },
    "aws_iam_policies": {
        "url":         "https://api.example.com/aws/iam-policies",
        "description": "AWS IAM policies and attached roles",
    },
}


# ── Core functions ────────────────────────────────────────────────────────────

def fetch_evidence(token: str, dry_run: bool = False) -> dict:
    """
    Fetch evidence from all configured sources.

    Args:
        token:   Bearer token for API authentication
        dry_run: If True, skip real HTTP calls and return mock data

    Returns:
        dict mapping source name → response payload
    """
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    results = {}

    for name, config in SOURCES.items():
        print(f"  Fetching {name}...")

        if dry_run:
            results[name] = {
                "mock": True,
                "source": name,
                "description": config["description"],
                "records": [{"id": f"mock-{i}", "status": "compliant"} for i in range(3)],
            }
            continue

        try:
            resp = requests.get(config["url"], headers=headers, timeout=15)
            if resp.ok:
                results[name] = resp.json()
                print(f"    ✓ {resp.status_code} — {len(str(resp.content))} bytes")
            else:
                results[name] = {"error": resp.status_code, "message": resp.text[:200]}
                print(f"    ✗ {resp.status_code} error")
        except requests.exceptions.RequestException as e:
            results[name] = {"error": "connection_failed", "message": str(e)}
            print(f"    ✗ Connection failed: {e}")

    return results


def build_manifest(sources: list, output_zip: str, collected_at: str) -> dict:
    """Build a manifest describing the evidence package."""
    return {
        "package_version":  "1.0",
        "collected_at":     collected_at,
        "output_file":      output_zip,
        "sources_collected": sources,
        "total_sources":    len(sources),
        "instructions":     (
            "Each JSON file in this package contains raw API evidence from "
            "the named source. Review individual files for compliance verification."
        ),
    }


def package_evidence(data: dict, output_dir: str = ".") -> str:
    """
    Package collected evidence into a timestamped ZIP file.

    Args:
        data:       Evidence dict from fetch_evidence()
        output_dir: Directory to write the ZIP file

    Returns:
        Path to the created ZIP file
    """
    ts       = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    zip_name = f"audit_evidence_{ts}.zip"
    zip_path = Path(output_dir) / zip_name

    manifest = build_manifest(
        sources=list(data.keys()),
        output_zip=zip_name,
        collected_at=ts,
    )

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Write each evidence source as its own JSON file
        for name, payload in data.items():
            zf.writestr(f"evidence/{name}.json", json.dumps(payload, indent=2))

        # Write the manifest
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    return str(zip_path)


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect audit evidence from REST APIs")
    parser.add_argument("--token",      default="demo-token", help="API bearer token")
    parser.add_argument("--output-dir", default=".",          help="Output directory for ZIP")
    parser.add_argument("--dry-run",    action="store_true",  help="Use mock data instead of real API calls")
    args = parser.parse_args()

    print("\n=== Evidence Collection Workflow ===\n")
    print(f"Mode:       {'DRY RUN (mock data)' if args.dry_run else 'LIVE'}")
    print(f"Sources:    {len(SOURCES)}")
    print(f"Output dir: {args.output_dir}\n")
    print("Collecting evidence...")

    evidence = fetch_evidence(token=args.token, dry_run=args.dry_run)

    print("\nPackaging evidence...")
    zip_path = package_evidence(evidence, output_dir=args.output_dir)

    print(f"\n✓ Evidence package created: {zip_path}")
    print("\nContents:")
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            info = zf.getinfo(name)
            print(f"  {name:45} {info.file_size:>8} bytes")

    print("\nDone. Share the ZIP file with your auditor.")
