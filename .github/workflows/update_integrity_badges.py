import json
import os
import sys
from pathlib import Path

readme = Path('README.md')
start_marker = '<!-- Start Integrity Badges -->'
end_marker = '<!-- End Integrity Badges -->'

content = readme.read_text(encoding='utf-8')
if start_marker not in content or end_marker not in content:
    print('README markers were not found.', file=sys.stderr)
    sys.exit(1)

raw_versions = os.environ.get('PYTHON_VERSIONS', '')

try:
    parsed_versions = json.loads(raw_versions)
except json.JSONDecodeError as exc:
    print(f'PYTHON_VERSIONS must be a JSON array of strings: {exc}', file=sys.stderr)
    sys.exit(1)

if not isinstance(parsed_versions, list) or not all(
    isinstance(version, str) for version in parsed_versions
):
    print('PYTHON_VERSIONS must be a JSON array of strings.', file=sys.stderr)
    sys.exit(1)

versions = [version.strip() for version in parsed_versions if version.strip()]
if not versions:
    print('PYTHON_VERSIONS JSON array is empty.', file=sys.stderr)
    sys.exit(1)

repository = os.environ['GITHUB_REPOSITORY']
workflow = 'check_integrity.yml'

badges = [
    f'[![Python {version}]'
    f'(https://img.shields.io/badge/Python-{version}-3776AB?logo=python&logoColor=white)]'
    f'(https://github.com/{repository}/actions/workflows/{workflow})'
    for version in versions
]

start_index = content.index(start_marker) + len(start_marker)
end_index = content.index(end_marker)
replacement = '\n' + '\n'.join(badges) + '\n'
updated = content[:start_index] + replacement + content[end_index:]
readme.write_text(updated, encoding='utf-8')
