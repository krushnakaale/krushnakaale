"""Read public data from GitHub REST with bounded retries."""
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GitHubError(RuntimeError):
    pass


class GitHubAPI:
    def __init__(self, token=""):
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "dynamic-profile-readme",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def get(self, path, expected_type):
        for attempt in range(3):
            delay = 2 ** attempt
            request = Request("https://api.github.com" + path, headers=self.headers)
            try:
                with urlopen(request, timeout=15) as response:
                    data = json.load(response)
                if not isinstance(data, expected_type):
                    raise GitHubError("GitHub returned an unexpected response shape")
                return data
            except HTTPError as error:
                headers = error.headers or {}
                limited = error.code == 429 or (
                    error.code == 403 and
                    (headers.get("X-RateLimit-Remaining") == "0" or headers.get("Retry-After"))
                )
                message = f"GitHub API returned HTTP {error.code}"
                if limited:
                    message += " (rate limit)"
                    try:
                        retry_after = int(headers.get("Retry-After", "0"))
                        reset = int(headers.get("X-RateLimit-Reset", "0"))
                        delay = max(delay, retry_after, reset - int(time.time()))
                    except ValueError:
                        pass
                if attempt == 2 or delay > 30 or not (limited or 500 <= error.code < 600):
                    raise GitHubError(message) from error
            except (URLError, TimeoutError) as error:
                if attempt == 2:
                    raise GitHubError("Could not connect to GitHub API") from error
            time.sleep(delay)
