# Troubleshooting

- **Workflow or Run workflow button missing**. Confirm the YAML is on the default branch, Actions are enabled and you have write access.
- **YAML error**. Run python -m scripts.validators locally and use the workflow log for the schema or indentation error.
- **Permission denied or rejected push**. Confirm the workflow's contents write permission and review branch rules. A concurrent push can reject a refresh. Rerun the job on the latest commit.
- **API rate limit, timeout or server error**. Check the job log for the HTTP status, wait for the rate window and rerun. The last successful README and stats remain available.
- **README not updating**. Check the config and marker pairs, run the updater locally, and review the diff. An unchanged run creates no commit.
- **Stats image broken**. Run the updater and validator. Check that assets/github-stats.svg was committed and that the filename matches case.
- **Snake output missing**. Run Generate contribution snake from the default branch, inspect both action steps and check the SVG filenames on output. Use the contribution activity link until the first publish.
- **Snake or banner animation appears static**. Open the SVG directly, check your browser’s reduced-motion settings and allow for GitHub image caching. The static banner is available at assets/banner.png.
- **Schedule delayed**. GitHub schedules run on the default branch and may be delayed or disabled on an inactive public repo. Check Actions and use manual dispatch when needed.
