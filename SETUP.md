# GitHub profile setup

This repository powers the [Krushna Kale GitHub profile](https://github.com/krushnakaale). GitHub displays the root README from the public repository named `krushnakaale` on that profile.

1. Add the profile files to the default branch of [krushnakaale/krushnakaale](https://github.com/krushnakaale/krushnakaale).
2. In the repository's **Actions** tab, run **Refresh dynamic GitHub profile** and **Generate contribution snake** on the default branch.
3. Confirm the project table appears in `README.md` and both contribution SVGs appear on the `output` branch.

The workflows request `contents: write` and use the built-in GitHub Actions token. If a push fails, check repository or organization Actions policies and branch rules.

## Refresh schedule

- The dashboard runs at minutes 17 and 47 of each hour (UTC). It also runs when the README, updater, or dashboard workflow changes on the default branch.
- Repository activity elsewhere appears on the next successful refresh. The dashboard lists up to eight recently pushed public repositories, excluding forks and this profile repository. Totals cover up to 1,000 public repositories before those exclusions.
- The contribution workflow runs daily at 03:23 UTC and publishes a light and dark SVG to the `output` branch.
- GitHub may delay scheduled runs. Both workflows also support manual runs.

## Run locally

With Python 3.12 and network access, run:

```sh
python scripts/update_profile.py
```

The script runs with the Python standard library and can use an optional `GH_TOKEN` environment variable for authenticated API requests. Keep both `DYNAMIC` comment markers in `README.md` so the updater can find the dashboard.
