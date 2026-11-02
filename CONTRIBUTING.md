# Contributing

Use Python 3.12 or newer, create a virtual environment, and install `requirements.txt`. Run commands from the repository root.

Before opening a pull request:

1. Run `python -m unittest discover -s tests -v`.
2. Manually check any dashboard interactions you changed.
3. Update the README or data reference when behavior changes.
4. Review `git diff` and `git status --short` for accidental health data, credentials, or local files.

Use synthetic inputs for tests and bug reports. Do not commit personal CSV/XML exports, API payloads from real users, virtual environments, or logs. Add tests when changing parsing, simulation, or API behavior. Keep experimental medical outputs clearly labeled and avoid unsupported accuracy claims.

Describe the problem, resulting behavior, and validation in your pull request. The main entry point is `app_final.py`; `app.py` is a distinct 3D demonstration, not a duplicate.
