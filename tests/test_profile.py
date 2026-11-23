import io
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
from urllib.error import HTTPError
from xml.etree import ElementTree

from scripts.github_api import GitHubAPI, GitHubError
from scripts.markdown_renderer import project_cards, render_regions
from scripts.profile_config import load_config
from scripts.repository_manager import fetch_repositories, select_featured, select_repositories
from scripts.update_profile import ROOT, update


class GitHubTests(unittest.TestCase):
    @patch("scripts.github_api.urlopen")
    def test_success_with_token(self, open_url):
        open_url.return_value = io.BytesIO(b'{"followers": 1}')
        self.assertEqual(GitHubAPI("example-token").get("/users/test", dict), {"followers": 1})
        self.assertEqual(open_url.call_args.args[0].get_header("Authorization"), "Bearer example-token")

    @patch("scripts.github_api.time.sleep")
    @patch("scripts.github_api.urlopen")
    def test_http_and_timeout_handling(self, open_url, sleep):
        for code, headers, count in [(401, {}, 1), (404, {}, 1), (429, {"Retry-After": "1"}, 3),
                                     (403, {"X-RateLimit-Remaining": "0"}, 3), (503, {}, 3)]:
            with self.subTest(code=code):
                open_url.reset_mock()
                open_url.side_effect = HTTPError("https://api.github.com", code, "", headers, None)
                with self.assertRaisesRegex(GitHubError, str(code)):
                    GitHubAPI().get("/users/test", dict)
                self.assertEqual(open_url.call_count, count)
        open_url.side_effect = TimeoutError()
        with self.assertRaisesRegex(GitHubError, "Could not connect"):
            GitHubAPI().get("/users/test", dict)
        self.assertTrue(sleep.called)

    def test_pagination_and_empty_result(self):
        api = Mock()
        api.get.side_effect = [[{"name": f"repo-{i}"} for i in range(100)], [{"name": "last"}]]
        self.assertEqual(len(fetch_repositories(api, "test")), 101)
        self.assertTrue(api.get.call_args.args[0].endswith("page=2"))
        api.get.side_effect = None
        api.get.return_value = []
        self.assertEqual(fetch_repositories(api, "test"), [])


class RepositoryTests(unittest.TestCase):
    def test_sort_filter_and_featured(self):
        config = load_config(ROOT / "config/profile.yml")
        config.update(sort="most_starred", exclude_repositories=["skip"])
        repos = [{"name": "weak"}, {"name": "top", "stargazers_count": 2},
                 {"name": "skip"}, {"name": config["username"]}, {"name": "fork", "fork": True},
                 {"name": "old", "archived": True}, {"name": "private", "private": True}]
        public = select_repositories(repos, config)
        self.assertEqual([repo["name"] for repo in public], ["top", "weak"])
        self.assertEqual(select_featured(public, ["WEAK", "missing"]), [repos[0]])

    def test_markdown_escaping_and_missing_description(self):
        cards = project_cards("example", [{"name": "sample", "description": "[image] | <script>"},
                                          {"name": "blank"}])
        self.assertIn("&#91;image&#93; &#124; &lt;script&gt;", cards)
        self.assertIn("https://github.com/example/blank", cards)
        self.assertNotIn("None", cards)


class UpdateTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "assets").mkdir()
        # The live dashboard renders project cards over checked-in background photos.
        # Give the isolated test workspace the same required source assets.
        for background in ("developer-background.png", "hacker-background.png.png"):
            shutil.copy2(ROOT / "assets" / background, self.root / "assets" / background)
        shutil.copytree(ROOT / "config", self.root / "config")
        self.readme = self.root / "README.md"
        self.template = (ROOT / "README.template.md").read_text(encoding="utf-8")
        self.readme.write_text(self.template + "\nManual note.\n", encoding="utf-8")
        self.api = Mock()
        self.repos = [{"name": "Python-Projects", "language": "Python"}, {"name": "first"}]
        self.api.get.side_effect = self.response

    def response(self, path, expected):
        if "/repos?" in path:
            return self.repos
        if "/events/" in path:
            return [{"type": "PushEvent", "repo": {"name": "krushnakaale/Python-Projects"},
                     "created_at": "2026-11-23T10:00:00Z", "public": True}]
        return {"followers": 3}

    def test_update_changes_and_idempotence(self):
        self.assertTrue(update(self.root, self.api))
        before = self.readme.read_bytes()
        ElementTree.parse(self.root / "assets/github-stats.svg")
        ElementTree.parse(self.root / "assets/language-breakdown.svg")
        self.assertIn(b"Python", (self.root / "assets/language-breakdown.svg").read_bytes())
        self.assertTrue((self.root / "assets/featured-projects-developer.png").is_file())
        self.assertTrue((self.root / "assets/latest-repositories-hacker.png").is_file())
        self.assertIn(b"Pushed to", before)
        self.assertIn(b"Manual note.", before)
        self.assertFalse(update(self.root, self.api))
        self.assertEqual(self.readme.read_bytes(), before)
        self.repos = [{"name": "renamed"}, {"name": "added"}]
        self.assertTrue(update(self.root, self.api))
        current = self.readme.read_text(encoding="utf-8")
        self.assertIn("https://github.com/krushnakaale/renamed", current)
        self.assertIn("https://github.com/krushnakaale/added", current)
        self.assertNotIn("https://github.com/krushnakaale/first", current)

    def test_failed_api_preserves_existing_outputs(self):
        update(self.root, self.api)
        before = self.readme.read_bytes()
        stats = self.root / "assets/github-stats.svg"
        svg = stats.read_bytes()
        self.api.get.side_effect = GitHubError("unavailable")
        with self.assertRaises(GitHubError):
            update(self.root, self.api)
        self.assertEqual(self.readme.read_bytes(), before)
        self.assertEqual(stats.read_bytes(), svg)

    def test_invalid_markers_and_configuration(self):
        invalid = self.template.replace("<!-- STATS:END -->", "")
        with self.assertRaisesRegex(ValueError, "STATS"):
            render_regions(invalid)
        (self.root / "config/profile.yml").write_text("repository_limit: 0\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            update(self.root, self.api)
        self.api.get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
