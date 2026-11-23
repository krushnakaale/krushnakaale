# Set up the GitHub profile

Create a public repository whose name matches your GitHub username. For this profile, use [krushnakaale/krushnakaale](https://github.com/krushnakaale/krushnakaale). Keep README.md and the assets, config, scripts, tests and .github directories at the repository root. Git includes the hidden .github directory when you clone or push.

Install Git and Python 3.12 or newer. In an existing checkout, start with the environment commands. To create a new checkout, first run:

    git clone https://github.com/krushnakaale/krushnakaale.git
    cd krushnakaale

## Windows PowerShell

    py -3.12 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe -m unittest discover -s tests -v
    .\.venv\Scripts\python.exe -m scripts.validators
    .\.venv\Scripts\python.exe -m scripts.update_profile

## Kali Linux and Ubuntu

    sudo apt install git python3 python3-venv
    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    .venv/bin/python -m unittest discover -s tests -v
    .venv/bin/python -m scripts.validators
    .venv/bin/python -m scripts.update_profile

In Git Bash on Windows, invoke .venv/Scripts/python.exe instead. The updater can make unauthenticated public API requests locally. Set GH_TOKEN in your process environment if authenticated rate limits are needed.

## Deploy

Review git status and git diff. Stage the profile files and commit:

    git add README.md README.template.md SETUP.md requirements.txt .gitignore assets config scripts tests docs .github
    git commit -m "Upgrade dynamic GitHub profile"
    git push origin main

In **Settings → Actions → General**, enable Actions and allow the workflow dependencies under the repository or organization policy. The refresh and snake workflows request write access for their own jobs. Default token permissions can stay restricted. The default branch and output branch must permit the applicable bot pushes.

Open **Actions**, select **Validate profile**, **Refresh dynamic GitHub profile** and **Generate contribution snake**, and run each on the default branch. Verify the updated README and both snake SVGs on the output branch. On a new account, use README.template.md to start with the contribution activity link. Add the README picture block with that account's asset URLs after the first snake publish.

See the [configuration](docs/CONFIGURATION.md), [architecture](docs/ARCHITECTURE.md), [customization](docs/CUSTOMIZATION.md), and [troubleshooting](docs/TROUBLESHOOTING.md) guides.
