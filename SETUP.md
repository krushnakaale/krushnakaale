# Setup: Dynamic GitHub Profile for krushnakaale

1. Create a **public** repository named `krushnakaale` under GitHub account `krushnakaale` (or use the existing same-name profile repository).
2. Upload `README.md`, `scripts/update_profile.py`, and both `.github/workflows/*.yml` files, preserving the paths. The repository default branch is assumed to be `main`.
3. In repository **Settings > Actions > General > Workflow permissions**, enable **Read and write permissions** for GITHUB_TOKEN if required, and save.
4. Open **Actions > Refresh dynamic GitHub profile > Run workflow**. The workflow fetches public repositories and updates the README. Confirm that the workflow succeeds.
5. Open **Actions > Generate contribution snake > Run workflow**. After success, the `output` branch will contain `github-contribution-grid-snake-dark.svg`.
6. View https://github.com/krushnakaale and refresh the page.

## Update timing

- The dashboard runs twice per hour, at minute 17 and 47 UTC, subject to GitHub Actions scheduling delays.
- A push to **another** repository does not immediately trigger a workflow in the profile repository. It appears after the next scheduled refresh.
- Creating, deleting, making private, or pushing a public repo is reflected at the next successful run.
- A manually started workflow updates on demand.
- The snake regenerates daily. GitHub may cache remote images temporarily.
- Only public owned non-fork repositories appear in the project table. Up to 1,000 public repos are fetched; 8 most recently pushed are displayed.
- The workflow updates README content; it cannot reorder GitHub's native pinned repository cards. Change those using GitHub's Customize your pins control.
- Scheduled GitHub Actions may be disabled after 60 days without activity on a public repository; re-enable in Actions if needed.

## Notes

- No personal access token is required: workflows use the built-in GITHUB_TOKEN.
- Verify LinkedIn, Instagram and portfolio URLs before publishing.
- Never add credentials or secrets to README or repository files.
- Dynamic section delimiters in README must remain intact.
- For the snake, GitHub Actions permissions must allow writing the output branch.
- `requirements.txt` is not needed: the Python updater uses only the standard library.
