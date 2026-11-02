# Local use and sensitive data

This is a local research prototype. The Flask API does not authenticate callers and enables CORS. Keep it bound to `127.0.0.1`; do not expose it to the internet or use it as a hosted health-data service.

The application is not a medical device. Its cardiac-event and overtraining indicators are experimental outputs, not validated clinical risk estimates.

Keep personal health exports in the ignored `data/` directory. Do not include them in public issues, screenshots, test fixtures, or logs. `.gitignore` does not remove files already committed to Git history.

If you discover a vulnerability, use the repository's private vulnerability reporting feature if enabled. Otherwise, contact the maintainer privately through their GitHub profile. Do not publish personal data, credentials, or an exploit against an exposed instance in a public issue.
