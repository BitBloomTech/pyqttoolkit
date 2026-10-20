# Dependency and build validation — 2026-10-19

This review starts from master `4d4f4e505e6aee7fe05d2d5cabcd1249c2d63048`
(version `0.9.0+3.g4d4f4e5`). It preserves the untagged script-runner and Python
3.14 changes already merged after 0.9.0. No release version is invented here;
Versioneer continues to derive checkout and distribution versions from Git.

## Changes and compatibility choices

- Set the Jinja2 floor to 3.1.6, the fix for the public
  [attr-filter advisory](https://github.com/advisories/GHSA-cpwx-vrp4-4pq7).
  This is a dependency baseline; it does not turn ordinary templates into a sandbox.
- Declare the isolated PEP 517 backend as `setuptools>=83`, covering the public
  [macOS sdist exclusion advisory](https://github.com/advisories/GHSA-h35f-9h28-mq5c).
  The backend resolved to 84.0.0. Setuptools is now an isolated backend dependency;
  the `publish` extra supplies build 1.6.1+ and twine 7.0.0+ instead.
- Keep matplotlib, pandas and appdirs interfaces and Qt optionality. No incompatible
  package replacement or speculative upper bound was justified by these tests.
  These open ranges are not a reproducible lock; the snapshots below record the
  actual versions tested on this date.
- Use tox 4 and wheel packaging. Run tests outside the checkout so imports and
  coverage come from the installed wheel. CircleCI builds and strictly checks
  both distributions; existing tag filters, upload destination and credential
  configuration are preserved.
- Retain bundled Versioneer 0.18 and its existing Python 3.14 compatibility patches.
  The explicit source-directory insertion in setup.py is needed: removing it in
  a disposable copy reproduced `ModuleNotFoundError: versioneer` with the PEP 517
  backend. No wholesale Versioneer/API migration was needed.

## Exact resolved versions and live audit

Both clean environments used Linux x86_64 / CPython 3.14.6 and pip 26.2.1.
[Baseline snapshot](dependency-baseline.txt) and
[candidate snapshot](dependency-candidate.txt) include all installed dependencies
plus the audit/build validation tools, not just runtime requirements. The local
project entry in the candidate snapshot is the pre-commit dirty build; the PR
records the clean commit/distribution version validated for delivery.

| Component | Before | After |
| --- | --- | --- |
| matplotlib | 3.11.2 | 3.11.2 |
| Jinja2 | 3.1.6 | 3.1.6 |
| pandas / numpy | 3.0.6 / 2.5.4 | 3.0.6 / 2.5.4 |
| appdirs | 1.4.4 | 1.4.4 |
| PyQt5 / Qt runtime / sip | 5.15.11 / 5.15.19 / 12.20.0 | same |
| pytest / pytest-asyncio | 9.1.1 / 1.4.0 | same |
| pytest-qt / pytest-xvfb | 4.5.0 / 3.1.1 | same |
| pytest-cov / coverage | 7.1.0 / 7.16.2 | same |
| tox / virtualenv | 4.67.1 / 21.14.11 | same |
| build / twine | 1.6.1 / 7.0.0 | same |
| setuptools | 84.0.0 (publish environment) | 84.0.0 (isolated backend only) |
| pip-audit | 2.10.1 | 2.10.1 |

`python -m pip_audit --format json` ran live against each environment. Before:
82 entries, 81 public packages audited, zero known vulnerabilities, one skipped
local pyqttoolkit version. After: 81 entries, 80 public packages audited, zero
known vulnerabilities, one skipped local pyqttoolkit version. An additional exact
requirements audit of isolated `setuptools==84.0.0` and `pip==26.2.1` found zero
known vulnerabilities and no skips. The public advisories above were also
rechecked directly. Fresh baseline resolution already selected patched packages;
this change establishes floors/build isolation rather than claiming a decrease
in the observed finding count. `pip check` passed before and after.

The unpublished Git-derived project versions cannot be audited as PyPI releases.
The source review below complements that skip; neither it nor the scanner proves
absence of vulnerabilities. Future dependency releases require fresh validation.

## Tests and distribution checks

The original tox selection passed 72 tests. Investigating the seven excluded
task-runner tests first produced passing isolated runs, but the complete clean
wheel/tox run exposed a timeout despite an asyncio event being set by another
thread. The tests incorrectly combined cross-thread `asyncio.Event` use, busy
loops and Qt event processing. Thread-safe `threading.Event` gates, bounded waits,
Qt polling and failure cleanup now preserve the same completion/result,
cancellation, error and queue-order assertions. Production task-runner behavior
is unchanged; the blanket exclusion is removed.

Final `python -m tox -e py314` passed **79 tests**, including all seven task-runner
cases and the existing script-runner regression, followed by the license-header
checker. Installed-wheel statement coverage was **30%**, not comprehensive
behavioral coverage. Existing syntax-escape warnings remain in UI highlighting
code. There is no configured pre-commit hook set in this repository; `git diff
--check` was also run.

`python -m build` uses isolated setuptools and builds the wheel from the generated
sdist as well as producing that sdist. `python -m twine check --strict` passes for
both artifacts. Separate clean base and UI environments for **each** artifact
validate install, `pip check`, and imports from outside the checkout. Each checks
installed metadata against `pyqttoolkit.__version__`; base environments assert
PyQt5 is absent, and UI environments create an offscreen QApplication and
TaskRunner. Smoke checks also exercise pandas, metadata imports, Jinja templates
and recursive scripts, preserving the already-merged script fix. The PR records
the final clean commit, artifact version and hashes after commit.

Reproduce with the README's setup and tox commands, then install each generated
artifact in separate virtual environments, using the artifact path with `[ui]`
for the Qt variant. Run all import checks from a temporary directory rather than
the checkout; do not bypass dependencies or reuse a UI environment for base proof.

## Platform inventory and bounded source review

The configured CI image is `cimg/python:3.14.6` on Linux, installing libgl1.
Local validation covers Linux x86_64 / Python 3.14.6, headless Qt and Python
wheel/sdist packaging. Metadata declares Python >=3.14 and platforms `any`; that
is broader than this verified matrix. Windows, macOS (including APFS/HFS+), other
architectures, Python versions beyond 3.14, interactive desktop rendering and
actual CircleCI execution are unrun here. No upload or publication was performed.

Reviewed surfaces were setup/backend/Versioneer metadata paths, CircleCI/tox,
script execution/templates, JSON metadata decoding, task-runner event delivery
and the email launcher. The source review is bounded static review plus the
listed tests, not a comprehensive security assessment.

- ScriptRunner executes Python and permits broad imports while restricting a
  small set of names. Its import/builtins regression tests do not establish a
  hostile-code sandbox. Use trusted scripts or an external isolation boundary.
- ScriptTemplate uses a normal Jinja Environment to generate code, not a
  SandboxedEnvironment or an HTML sanitizer. Template source must be trusted;
  output escaping and input trust remain caller responsibilities.
- Metadata uses JSON decoding; no additional confirmed source vulnerability was
  established in this bounded review. Input-size/resource-exhaustion behavior,
  every widget/plugin, native Qt components and platform-specific email launching
  were not dynamically audited.

Residual coverage includes these unreviewed surfaces, the local-project scanner
skip and unrun platforms. This report accepts no security exception and does not
claim complete package or deployment safety.
