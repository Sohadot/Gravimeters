#!/usr/bin/env python3
"""Offline, fail-closed release gates for the public Gravimeters reference.

These are engineering controls, NOT a substitute for scientific source review,
GitHub branch rules, production access controls, independent vulnerability scans,
or an external website/DOI/mail check. No network access or project writes.
"""
from __future__ import annotations

import ipaddress
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
ID = re.compile(r"^[a-z][a-z0-9-]{1,49}$")
PIN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}$")
FORBIDDEN_FILE = re.compile(r"(?:decisions[_-]?log|internal[_-]?master[_-]?plan|buyer[_-]?pipeline|lead[_-]?pipeline|\.env(?:\.|$)|\.pem$|\.p12$|\.pfx$|id_rsa$|\.key$)", re.I)
TOKENS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{32,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{50,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
]
PUBLIC_ROUTES = ["index.html", "instruments/index.html", "navigation/index.html", "acquisition/index.html"]


def json_file(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"Cannot parse {path.name}: {exc}")
        return None


def valid_https(value: object) -> bool:
    if not isinstance(value, str) or len(value) > 2048:
        return False
    try:
        p = urlsplit(value)
        host = p.hostname
        if p.scheme != "https" or not host or p.username or p.password or p.fragment:
            return False
        if p.port not in (None, 443):
            return False
        if host in {"localhost", "example.com", "example.org", "example.net"} or host.endswith(".local"):
            return False
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            return "." in host and all(k for k in host.split("."))
        return False  # disallow IP-literal sources, including private and loopback
    except ValueError:
        return False


def valid_date(value: object, *, not_future: bool = True) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = date.fromisoformat(value)
        return (parsed <= date.today()) if not_future else True
    except ValueError:
        return False


def audit_data(root: Path) -> list[str]:
    errors: list[str] = []
    data = root / "data"
    inst = json_file(data / "instruments.json", errors)
    evid = json_file(data / "evidence.json", errors)
    apps = json_file(data / "applications.json", errors)
    tax = json_file(data / "taxonomy.json", errors)
    schema = json_file(data / "schema/instrument.schema.json", errors)
    links = json_file(data / "links.json", errors)
    if any(x is None for x in (inst, evid, apps, tax, schema, links)):
        return errors
    if not isinstance(inst, list) or not inst or not isinstance(evid, list) or not evid or not isinstance(apps, list) or not apps:
        return ["Instrument and evidence records must be nonempty lists"]
    if not isinstance(tax, dict) or not isinstance(schema, dict) or not isinstance(links, dict):
        return ["Taxonomy, schema and link manifest must be JSON objects"]

    facets = tax.get("facets", {})
    measurement = facets.get("measurement_type") if isinstance(facets, dict) else None
    sensing = facets.get("sensing_family") if isinstance(facets, dict) else None
    if not isinstance(measurement, dict) or not isinstance(sensing, dict) or not measurement or not sensing:
        errors.append("Taxonomy must define nonempty measurement/sensor vocabularies")
        measurement, sensing = {}, {}
    version = tax.get("taxonomy_version", "")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        errors.append("Taxonomy version must be semver")
    if not any(x.get("class") == "gravity_gradiometer" and x.get("included_in_atlas") is False
               for x in tax.get("distinctions", []) if isinstance(x, dict)):
        errors.append("Gradiometer distinction must remain explicit and excluded")
    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
    except Exception as exc:
        errors.append(f"Invalid instrument JSON Schema: {exc}")
        validator = None
    props = schema.get("properties", {})
    if (set(props.get("measurement_type", {}).get("enum", [])) != set(measurement)
            or set(props.get("sensing_family", {}).get("enum", [])) != set(sensing)):
        errors.append("Schema allowed values must match taxonomy exactly")
    if schema.get("additionalProperties") is not False:
        errors.append("Instrument schema must reject undocumented extra fields")

    ids = set()
    for item in inst:
        if not isinstance(item, dict):
            errors.append("Instrument record must be an object")
            continue
        key = item.get("id", "<missing>")
        if key in ids:
            errors.append(f"Duplicate instrument ID: {key}")
        ids.add(key)
        if not isinstance(key, str) or not ID.fullmatch(key):
            errors.append(f"Invalid instrument ID: {key}")
        if validator:
            for err in validator.iter_errors(item):
                errors.append(f"Instrument {key}: {err.message}")
        if item.get("measurement_type") not in measurement or item.get("sensing_family") not in sensing:
            errors.append(f"Instrument {key}: unknown taxonomy value")
        if str(item.get("measurement", "")).lower() != item.get("measurement_type"):
            errors.append(f"Instrument {key}: contradictory measurement modes")
        if not valid_https(item.get("source_url")):
            errors.append(f"Instrument {key}: invalid/untrusted source URL")
        if not valid_date(item.get("reviewed_at")):
            errors.append(f"Instrument {key}: missing, invalid or future review date")

    application_ids = set()
    for app in apps:
        if not isinstance(app, dict):
            errors.append("Application record must be an object")
            continue
        key = app.get("id")
        if not isinstance(key, str) or not ID.fullmatch(key) or key in application_ids:
            errors.append(f"Invalid or duplicate application ID: {key}")
        application_ids.add(key)
        if any(not isinstance(app.get(field), str) or len(app[field].strip()) < 20
               for field in ("title", "summary", "boundary")):
            errors.append(f"Application {key}: missing or insufficient context and limitation")

    evidence_ids = set()
    required = ("id", "title", "source_type", "claim", "boundary", "published_at", "reviewed_at", "source_url")
    for item in evid:
        if not isinstance(item, dict):
            errors.append("Evidence record must be an object")
            continue
        key = item.get("id", "<missing>")
        if key in evidence_ids:
            errors.append(f"Duplicate evidence ID: {key}")
        evidence_ids.add(key)
        if not isinstance(key, str) or not ID.fullmatch(key):
            errors.append(f"Invalid evidence ID: {key}")
        if any(not isinstance(item.get(x), str) or len(item[x].strip()) < 3 for x in required):
            errors.append(f"Evidence {key}: missing/empty required provenance and limitations")
            continue
        if len(item["claim"]) < 35 or len(item["boundary"]) < 45:
            errors.append(f"Evidence {key}: insufficient claim/limitation summary")
        if not valid_https(item["source_url"]):
            errors.append(f"Evidence {key}: invalid/untrusted original source URL")
        if not valid_date(item["published_at"]) or not valid_date(item["reviewed_at"]):
            errors.append(f"Evidence {key}: invalid/future publication or review date")
        if item["source_url"].startswith("https://arxiv.org/") and "preprint" not in item["source_type"].lower():
            errors.append(f"Evidence {key}: arXiv source must be explicitly labelled preprint")
        if "guaranteed" in item["claim"].lower() or "universal replacement" in item["claim"].lower():
            errors.append(f"Evidence {key}: unqualified absolute performance claim")
        status = item.get("evidence_status")
        if status not in {"preprint", "peer_reviewed_article"}:
            errors.append(f"Evidence {key}: invalid explicit evidence status")
        original_doi = item.get("source_doi")
        if status == "preprint":
            if "preprint" not in item["source_type"].lower() or original_doi is not None:
                errors.append(f"Evidence {key}: preprint must be labelled and cannot claim journal source DOI")
        if status == "peer_reviewed_article":
            if "peer-reviewed" not in item["source_type"].lower():
                errors.append(f"Evidence {key}: journal status requires peer-reviewed source label")
            if not isinstance(original_doi, str) or not re.fullmatch(r"10\.\d{4,9}/[A-Za-z0-9._;()/:-]+", original_doi):
                errors.append(f"Evidence {key}: journal status requires plausible original article DOI")
            elif item["source_url"].startswith("https://www.nature.com/articles/") and item["source_url"].rstrip('/').split('/')[-1] != original_doi.split('/')[-1]:
                errors.append(f"Evidence {key}: journal DOI does not match cited Nature article")
        if not isinstance(item.get("application_ids"), list) or not item["application_ids"] or len(item["application_ids"]) != len(set(map(str, item["application_ids"]))):
            errors.append(f"Evidence {key}: application links must be unique and nonempty")
        elif any(app_id not in application_ids for app_id in item["application_ids"]):
            errors.append(f"Evidence {key}: unknown application ID")
        if not isinstance(item.get("sensing_families"), list) or not item["sensing_families"] or len(item["sensing_families"]) != len(set(map(str, item["sensing_families"]))):
            errors.append(f"Evidence {key}: sensing links must be unique and nonempty")
        elif any(family not in sensing for family in item["sensing_families"]):
            errors.append(f"Evidence {key}: unknown sensing-family link")
        links_to_models = item.get("linked_instruments")
        if not isinstance(links_to_models, list):
            errors.append(f"Evidence {key}: model relationships must be an explicit list (may be empty)")
            continue
        seen_models = set()
        for link in links_to_models:
            if not isinstance(link, dict) or set(link) != {"instrument_id", "relation", "source_section"}:
                errors.append(f"Evidence {key}: model link needs instrument, relation and source location")
                continue
            model_id = link["instrument_id"]
            if model_id not in ids or model_id in seen_models:
                errors.append(f"Evidence {key}: unknown or duplicate explicitly identified instrument")
            seen_models.add(model_id)
            if link["relation"] != "model_explicitly_named_in_source" or not isinstance(link["source_section"], str) or len(link["source_section"].strip()) < 20:
                errors.append(f"Evidence {key}: insufficient source evidence for model identification")

    expected = "https://github.com/Sohadot/Gravimeters"
    if links.get("github_repository_url") != expected:
        errors.append("GitHub source-of-truth link was modified")
    if links.get("zenodo_record_url") is not None:
        errors.append("Zenodo DOI link requires a separate documented publication/verification gate")
    if links.get("escrow_process_url") != "https://www.escrow.com/domains/how-it-works":
        errors.append("Escrow informational link changed; requires explicit review")
    try:
        build = (root / "scripts/build.py").read_text(encoding="utf-8")
        match = re.search(r"['\"]dataset_version['\"]\s*:\s*['\"](\d+\.\d+\.\d+)['\"]", build)
        if not match or match.group(1) != version:
            errors.append("Public dataset and taxonomy versions disagree")
    except OSError:
        errors.append("Missing site build script")
    return errors


def audit_workflows(root: Path) -> list[str]:
    errors: list[str] = []
    folder = root / ".github/workflows"
    workflows = list(folder.glob("*.yml"))
    if not workflows:
        return ["No GitHub Actions workflows exist"]
    for path in workflows:
        try:
            doc = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        except (OSError, yaml.YAMLError) as exc:
            errors.append(f"Invalid Actions YAML in {path.name}: {exc}")
            continue
        if not isinstance(doc, dict):
            errors.append(f"Workflow {path.name} must be YAML object")
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if re.search(r"^\s*(?:-\s*)?uses:\s*", line):
                value = line.split("uses:", 1)[1].strip().split(" #", 1)[0]
                if value.startswith("./"):
                    continue
                if not PIN.fullmatch(value):
                    errors.append(f"{path.name}: action must use immutable full SHA: {value}")
        if "pull_request_target" in doc.get("on", {}):
            errors.append(f"{path.name}: privileged pull_request_target is prohibited")
        if path.name == "deploy-pages.yml":
            trigger = doc.get("on", {})
            if not isinstance(trigger, dict) or set(trigger) != {"workflow_dispatch"}:
                errors.append("Production publication must be exclusively manual workflow_dispatch")
            jobs = doc.get("jobs", {})
            build = jobs.get("build", {})
            deploy = jobs.get("deploy", {})
            if "refs/heads/main" not in build.get("if", ""):
                errors.append("Production build must be limited to main")
            if build.get("permissions", {}).get("contents") != "read":
                errors.append("Production build must have only read content permission")
            if set(deploy.get("permissions", {})) != {"pages", "id-token"} or deploy.get("permissions", {}).get("pages") != "write" or deploy.get("permissions", {}).get("id-token") != "write":
                errors.append("Production deploy must be limited to pages/OIDC permissions")
            if deploy.get("environment", {}).get("name") != "github-pages":
                errors.append("Production deploy must use github-pages environment")
            runs = "\n".join(str(x.get("run", "")) for x in build.get("steps", []))
            if any(command not in runs for command in ("scripts/governance_gate.py", "scripts/smoke_test.py", "unittest")):
                errors.append("Production build must repeat the governance and smoke-test gates")
        if path.name == "check.yml":
            jobs = doc.get("jobs", {})
            check = jobs.get("check", {})
            if check.get("permissions", {}).get("contents") != "read":
                errors.append("PR check must have read-only GitHub permissions")
            trigger = doc.get("on", {})
            if not isinstance(trigger, dict) or "pull_request" not in trigger:
                errors.append("PR quality workflow must run on pull_request")
            runs = "\n".join(str(x.get("run", "")) for x in check.get("steps", []))
            for command in ("scripts/governance_gate.py", "scripts/smoke_test.py", "unittest"):
                if command not in runs:
                    errors.append(f"PR gate does not invoke {command}")
    return errors


def audit_files(root: Path) -> list[str]:
    errors: list[str] = []
    public = root / "dist"
    if not public.exists():
        return ["No generated dist/ exists. Build first."]
    for name in PUBLIC_ROUTES:
        if not (public / name).is_file():
            errors.append(f"Missing public route: {name}")
    for item in public.rglob("*"):
        if not item.is_file():
            continue
        rel = str(item.relative_to(public))
        if FORBIDDEN_FILE.search(rel):
            errors.append(f"Private or sensitive-looking artifact in site: {rel}")
        if item.suffix.lower() not in {".html", ".css", ".js", ".json", ".txt", ".svg", ".jpg", ".jpeg", ".png", ".webp", ".xml", ".ico"}:
            errors.append(f"Unexpected public artifact type: {rel}")
        if item.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".ico"}:
            try:
                body = item.read_text(encoding="utf-8")
            except UnicodeError:
                errors.append(f"Non-UTF8 public text artifact: {rel}")
                continue
            if any(token.search(body) for token in TOKENS):
                errors.append(f"Possible credential leaked to public artifact: {rel}")
            if "GRAVIMETERS_INTERNAL_MASTER_PLAN" in body or "GRAVIMETERS_DECISIONS_LOG" in body:
                errors.append(f"Internal document name/content leaked to public artifact: {rel}")
    return errors



def audit_source_paths(root: Path) -> list[str]:
    """Prevent obvious private assets and credential signatures entering public git."""
    errors: list[str] = []
    if (root / ".git").exists():
        result = subprocess.run(["git", "ls-files", "-z", "--cached"], cwd=root,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode:
            return ["Cannot inspect Git index for sensitive source paths"]
        candidates = [root / name.decode("utf-8", "replace")
                      for name in result.stdout.split(b"\x00") if name]
    else:
        candidates = [x for x in root.rglob("*") if x.is_file() and not any(
            part in {"dist", ".git", "__pycache__", ".pytest_cache"}
            for part in x.relative_to(root).parts)]
    for path in candidates:
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        if FORBIDDEN_FILE.search(rel):
            errors.append(f"Private/sensitive filename committed to public repository: {rel}")
        if path.is_symlink():
            errors.append(f"Symlink in public repository requires separate review: {rel}")
            continue
        if path.suffix.lower() not in {".md", ".py", ".json", ".yml", ".yaml", ".js", ".css", ".html", ".txt", ".xml", ".sh"}:
            continue
        try:
            if path.stat().st_size > 2_000_000:
                errors.append(f"Oversized text source file requires explicit review: {rel}")
                continue
            body = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            errors.append(f"Cannot inspect public text source: {rel}")
            continue
        if any(token.search(body) for token in TOKENS):
            errors.append(f"Possible credential in public source: {rel}")
    return errors

def audit_repository(root: Path) -> list[str]:
    return audit_data(root) + audit_workflows(root) + audit_files(root) + audit_source_paths(root)


if __name__ == "__main__":
    problems = audit_repository(ROOT)
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        records = json_file(ROOT / "data/instruments.json", []) or []
        evidence = json_file(ROOT / "data/evidence.json", []) or []
        tax = json_file(ROOT / "data/taxonomy.json", []) or {}
        report = (
            "## Gravimeters — automated governance gate\n\n"
            f"**Status:** {'FAILED' if problems else 'PASSED'}  \n"
            f"**Instrument entries:** {len(records)}  \n"
            f"**Evidence entries:** {len(evidence)}  \n"
            f"**Taxonomy version:** {tax.get('taxonomy_version', 'unknown')}  \n"
            f"**Automated policy violations:** {len(problems)}\n\n"
            "Offline checks test structure, provenance metadata, and release workflow controls. "
            "They do **not** prove scientific truth, website security, source ownership, or live link availability.\n"
        )
        with Path(summary).open("a", encoding="utf-8") as out:
            out.write(report)
    if problems:
        print("GOVERNANCE GATE: FAILED", file=sys.stderr)
        for issue in problems:
            print(f" - {issue}", file=sys.stderr)
        sys.exit(1)
    print("GOVERNANCE GATE: PASSED — provenance, taxonomy, workflow security, export hygiene")
