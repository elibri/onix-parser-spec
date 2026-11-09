#!/usr/bin/env python3
"""Runs an ONIX parser or differ over the fixtures and compares its output.

The implementation can be written in any language; it is called as a command:

  tools/check.py parser [--only TEXT] -- COMMAND...
      COMMAND onix_parser_fixtures/cases/<id>/onix.xml
      must print the parsed message (JSON object) on stdout.

  tools/check.py diff [--only TEXT] -- COMMAND...
      COMMAND onix_diff_fixtures/cases/<id>/before.xml onix_diff_fixtures/cases/<id>/after.xml
      must print the changes (JSON array) on stdout.

Examples:
  tools/check.py parser -- php bin/onix-parse
  tools/check.py diff --only price -- node dist/diff.js

Comparison follows the fixture READMEs: object keys as sets, arrays in order,
numbers by value (39.9 == 39.90), booleans are not numbers. Diff changes are a
multiset: each expected change must match one reported change.
Exit status 0 when every case passes.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return type(a) is type(b) and a == b


def differences(expected, actual, path="$", found=None, limit=5):
    """Up to `limit` (path, expected, actual) triples where the JSON values differ."""
    found = [] if found is None else found
    if len(found) >= limit:
        return found
    if isinstance(expected, dict) and isinstance(actual, dict):
        for key in expected:
            if key not in actual:
                found.append((f"{path}.{key}", expected[key], "<missing>"))
            else:
                differences(expected[key], actual[key], f"{path}.{key}", found, limit)
        found.extend((f"{path}.{key}", "<not expected>", actual[key]) for key in actual if key not in expected)
    elif isinstance(expected, list) and isinstance(actual, list):
        for i, (x, y) in enumerate(zip(expected, actual)):
            differences(x, y, f"{path}[{i}]", found, limit)
        if len(expected) != len(actual):
            found.append((f"{path} (length)", len(expected), len(actual)))
    elif not same(expected, actual):
        found.append((path, expected, actual))
    return found[:limit]


def short(value, limit=160):
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else text[:limit] + "…"


def run(command, args):
    try:
        proc = subprocess.run(command + [str(a) for a in args], capture_output=True, text=True)
    except OSError as e:
        raise RuntimeError(f"cannot run {command[0]}: {e}")
    if proc.returncode != 0:
        raise RuntimeError(f"exit {proc.returncode}: {proc.stderr.strip()[:500]}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"stdout is not JSON ({e}): {proc.stdout[:200]!r}")


def check_parser(case, command):
    expected = json.loads((case / "expected.json").read_text(encoding="utf-8"))["message"]
    actual = run(command, [case / "onix.xml"])
    return [f"{path}: expected {short(e)}, got {short(a)}" for path, e, a in differences(expected, actual)]


def check_diff(case, command):
    expected = json.loads((case / "expected.json").read_text(encoding="utf-8"))["changes"]
    actual = run(command, [case / "before.xml", case / "after.xml"])
    if not isinstance(actual, list):
        return [f"expected a JSON array, got {short(actual)}"]
    unmatched = list(actual)
    missing = []
    for change in expected:
        match = next((i for i, c in enumerate(unmatched) if same(change, c)), None)
        if match is None:
            missing.append(change)
        else:
            unmatched.pop(match)
    return [f"missing {short(c)}" for c in missing] + [f"unexpected {short(c)}" for c in unmatched]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kind", choices=["parser", "diff"])
    parser.add_argument("--only", help="run only cases whose id contains this text")
    parser.add_argument("--details", type=int, default=20, help="how many failing cases to describe (default 20)")
    argv = sys.argv[1:]
    split = argv.index("--") if "--" in argv else len(argv)
    args = parser.parse_args(argv[:split])
    command = argv[split + 1:]
    if not command:
        parser.error("give the command after --")

    cases_dir = ROOT / ("onix_parser_fixtures" if args.kind == "parser" else "onix_diff_fixtures") / "cases"
    check = check_parser if args.kind == "parser" else check_diff
    cases = sorted(p for p in cases_dir.iterdir() if p.is_dir() and (not args.only or args.only in p.name))

    failed = []
    for case in cases:
        try:
            problems = check(case, command)
        except RuntimeError as e:
            problems = [str(e)]
        if problems:
            failed.append((case.name, problems))

    for name, problems in failed[: args.details]:
        print(f"FAIL {name}")
        for problem in problems[:5]:
            print(f"     {problem}")
    if len(failed) > args.details:
        print(f"... and {len(failed) - args.details} more failing cases: {' '.join(n for n, _ in failed[args.details:])}")
    print(f"{args.kind}: {len(cases) - len(failed)}/{len(cases)} cases pass")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
