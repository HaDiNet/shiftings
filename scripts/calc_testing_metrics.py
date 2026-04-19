#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


TIER1_COVERAGE_MODULES = (
    'shiftings/accounts/views/auth.py',
    'shiftings/accounts/views/user.py',
    'shiftings/shifts/forms/permission.py',
    'shiftings/shifts/views/permission.py',
    'shiftings/utils/views/base.py',
)

TIER1_SCENARIO_DOMAINS = {'Auth', 'Permissions'}


@dataclass
class CoverageRow:
    stmts: int
    miss: int
    cover_pct: float

    @property
    def covered(self) -> int:
        return self.stmts - self.miss


def parse_coverage_report(report_text: str) -> dict[str, CoverageRow]:
    rows: dict[str, CoverageRow] = {}
    line_re = re.compile(r'^(\S+)\s+(\d+)\s+(\d+)\s+(\d+)%\s*$')

    for line in report_text.splitlines():
        match = line_re.match(line.strip())
        if not match:
            continue
        path, stmts, miss, cover_pct = match.groups()
        rows[path] = CoverageRow(stmts=int(stmts), miss=int(miss), cover_pct=float(cover_pct))

    return rows


def run_coverage_report(repo_root: Path) -> str:
    result = subprocess.run(
        ['python', '-m', 'coverage', 'report'],
        cwd=repo_root / 'src',
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def parse_scenario_coverage(doc_text: str) -> tuple[int, int, int, int]:
    covered = 0
    partial = 0
    missing = 0
    total = 0

    for line in doc_text.splitlines():
        if not line.startswith('|'):
            continue
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(cells) < 4:
            continue
        domain = cells[0]
        status = cells[2]
        if domain not in TIER1_SCENARIO_DOMAINS:
            continue
        total += 1
        if status == 'Covered':
            covered += 1
        elif status == 'Partial':
            partial += 1
        elif status == 'Missing':
            missing += 1

    return covered, partial, missing, total


def load_mutation_score(repo_root: Path) -> tuple[float | None, dict[str, int] | None]:
    stats_path = repo_root / 'mutants' / 'mutmut-cicd-stats.json'
    if not stats_path.exists():
        return None, None

    data = json.loads(stats_path.read_text(encoding='utf-8'))
    killed = int(data.get('killed', 0))
    survived = int(data.get('survived', 0))

    denominator = killed + survived
    if denominator == 0:
        return None, data
    return (100.0 * killed / denominator), data


def load_regression_index(repo_root: Path, tracker_path: Path) -> tuple[float | None, int, int]:
    path = tracker_path if tracker_path.is_absolute() else (repo_root / tracker_path)
    if not path.exists():
        return None, 0, 0

    data = json.loads(path.read_text(encoding='utf-8'))
    items = data.get('tier1_fixes', [])
    total = len(items)
    if total == 0:
        return None, 0, 0

    with_test = sum(1 for item in items if bool(item.get('has_regression_test')))
    return (100.0 * with_test / total), with_test, total


def maybe_run_mutmut(repo_root: Path) -> None:
    (repo_root / 'mutants').mkdir(parents=True, exist_ok=True)
    env = dict(**os.environ)
    env['PYTHONPATH'] = 'src'
    try:
        subprocess.run(['python', '-m', 'mutmut', 'run'], cwd=repo_root, check=True, env=env)
        subprocess.run(['python', '-m', 'mutmut', 'export-cicd-stats'], cwd=repo_root, check=True, env=env)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            'mutmut execution failed. If you are running on Python 3.14, run mutmut in a 3.12/3.13 '
            'environment and then rerun this script without --run-mutmut.'
        ) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description='Calculate testing quality scorecard metrics.')
    parser.add_argument('--repo-root', default='.', help='Path to repository root.')
    parser.add_argument('--doc', default='docs/testing_quality.md', help='Path to testing quality markdown file.')
    parser.add_argument(
        '--regression-tracker',
        default='docs/regression_protection_tracker.json',
        help='JSON file tracking Tier 1 bug fixes and regression tests.',
    )
    parser.add_argument('--coverage-report-file', help='Use an existing coverage report text file instead of running coverage.')
    parser.add_argument('--run-mutmut', action='store_true', help='Run mutmut before reading mutation score.')
    parser.add_argument('--json', action='store_true', help='Print output as JSON instead of markdown-friendly text.')
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    doc_path = Path(args.doc) if Path(args.doc).is_absolute() else (repo_root / args.doc)

    if args.run_mutmut:
        maybe_run_mutmut(repo_root)

    if args.coverage_report_file:
        report_path = Path(args.coverage_report_file)
        if not report_path.is_absolute():
            report_path = repo_root / report_path
        coverage_report = report_path.read_text(encoding='utf-8')
    else:
        coverage_report = run_coverage_report(repo_root)

    coverage_rows = parse_coverage_report(coverage_report)

    tier1_rows = [coverage_rows[module] for module in TIER1_COVERAGE_MODULES if module in coverage_rows]
    if not tier1_rows:
        raise SystemExit('No Tier 1 module coverage rows found. Run coverage first.')

    tier1_total_stmts = sum(row.stmts for row in tier1_rows)
    tier1_total_covered = sum(row.covered for row in tier1_rows)
    tier1_weighted_pct = 100.0 * tier1_total_covered / tier1_total_stmts

    total_coverage = coverage_rows.get('TOTAL')
    if total_coverage is None:
        raise SystemExit('TOTAL row missing from coverage report.')

    doc_text = doc_path.read_text(encoding='utf-8')
    covered, partial, missing, total = parse_scenario_coverage(doc_text)
    scenario_strict_pct = (100.0 * covered / total) if total else None
    scenario_partial_weighted_pct = (100.0 * (covered + 0.5 * partial) / total) if total else None

    mutation_score_pct, mutation_raw = load_mutation_score(repo_root)
    regression_pct, regression_with_test, regression_total = load_regression_index(
        repo_root, Path(args.regression_tracker)
    )

    result = {
        'full_suite_coverage_pct': round(total_coverage.cover_pct, 1),
        'tier1_weighted_coverage_pct': round(tier1_weighted_pct, 1),
        'tier1_scenario_covered': covered,
        'tier1_scenario_total': total,
        'tier1_scenario_strict_pct': None if scenario_strict_pct is None else round(scenario_strict_pct, 1),
        'tier1_scenario_partial_weighted_pct': None
        if scenario_partial_weighted_pct is None
        else round(scenario_partial_weighted_pct, 1),
        'tier1_mutation_score_pct': None if mutation_score_pct is None else round(mutation_score_pct, 1),
        'tier1_regression_protection_pct': None if regression_pct is None else round(regression_pct, 1),
        'tier1_regression_with_test': regression_with_test,
        'tier1_regression_total': regression_total,
        'tier1_modules': {
            module: {
                'stmts': coverage_rows[module].stmts,
                'miss': coverage_rows[module].miss,
                'cover_pct': coverage_rows[module].cover_pct,
            }
            for module in TIER1_COVERAGE_MODULES
            if module in coverage_rows
        },
        'mutation_raw': mutation_raw,
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    print(f"Full-suite line coverage: {result['full_suite_coverage_pct']}%")
    print(f"Tier 1 weighted coverage: {result['tier1_weighted_coverage_pct']}%")
    print(
        'Tier 1 scenario coverage: '
        f"{result['tier1_scenario_covered']}/{result['tier1_scenario_total']} "
        f"({result['tier1_scenario_strict_pct']}%)"
    )
    print(f"Tier 1 scenario partial-weighted: {result['tier1_scenario_partial_weighted_pct']}%")
    mutation_value = 'n/a' if result['tier1_mutation_score_pct'] is None else f"{result['tier1_mutation_score_pct']}%"
    print(f'Tier 1 mutation score: {mutation_value}')
    if result['tier1_regression_protection_pct'] is None:
        print('Tier 1 regression protection index: n/a')
    else:
        print(
            'Tier 1 regression protection index: '
            f"{result['tier1_regression_protection_pct']}% "
            f"({result['tier1_regression_with_test']}/{result['tier1_regression_total']})"
        )

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
