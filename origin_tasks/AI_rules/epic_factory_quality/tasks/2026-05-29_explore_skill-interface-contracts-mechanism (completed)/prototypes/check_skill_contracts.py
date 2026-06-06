"""Lint skill interface contracts: derived_from vs produces cross-ref + may_invoke existence."""
# tier: B

import argparse, sys
from pathlib import Path
import yaml

EXTERNAL = ("doc/", "requirements_user_needs/", "lib/", "test/", ".claude/schemas/")

def _norm(p):
    return p.rstrip("/").replace("iteration_{n}", "v{n}")

def _folder(p):
    n = _norm(p)
    return n.rsplit("/", 1)[0] if "." in n.split("/")[-1] else n

def _flat(block, *sects):
    return [i.get("path", "") for s in sects for i in block.get(s, [])]

def load_contracts(d):
    out = {}
    for f in sorted(d.glob("contract_*.yaml")):
        out[f.stem.removeprefix("contract_")] = {"file": f, "data": yaml.safe_load(f.read_text())}
    return out

def check_derived_from(contracts, violations):
    pp = [p for info in contracts.values()
          for p in _flat(info["data"].get("produces", {}), "required", "conditional")]
    all_produced = {_norm(p) for p in pp} | {_folder(p) for p in pp}
    for info in contracts.values():
        for sec in ("required", "optional"):
            for item in info["data"].get("derived_from", {}).get(sec, []):
                path = item.get("path", "")
                src = item.get("source", "")
                # "external" = developer-owned; "skill:X" = declared cross-ref — skip both
                if src == "external" or src.startswith("skill:"):
                    continue
                if any(path.startswith(e) for e in EXTERNAL):
                    continue
                if _norm(path) not in all_produced:
                    violations.append(
                        f"{info['file'].name} derived_from[{sec}] '{path}' — "
                        f"no producer declares this path and it is not a known external source. "
                        f"Add it to a producing skill's produces: block."
                    )

def check_may_invoke(contracts, skills_root, violations):
    for info in contracts.values():
        for ref in info["data"].get("may_invoke", []):
            if not (skills_root / ref / "SKILL.md").exists():
                violations.append(
                    f"{info['file'].name} may_invoke '{ref}' — "
                    f".claude/skills/{ref}/SKILL.md not found. "
                    f"Misspelled skill name or skill not yet created."
                )

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prototypes-dir", required=True, type=Path)
    ap.add_argument("--skills-root", type=Path, default=Path(".claude/skills"))
    args = ap.parse_args()
    contracts = load_contracts(args.prototypes_dir)
    if not contracts:
        print("No contract_*.yaml files found.")
        return 0
    violations = []
    check_derived_from(contracts, violations)
    check_may_invoke(contracts, args.skills_root, violations)
    if violations:
        print(f"FAIL — {len(violations)} contract violation(s):")
        for v in violations:
            print(f"  - {v}")
        return 1
    print(f"PASS — {len(contracts)} contract(s) checked, 0 violations.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
