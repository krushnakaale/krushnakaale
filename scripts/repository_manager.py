"""Fetch, filter and rank repositories for the public showcase."""


def fetch_repositories(api, username):
    repositories = []
    page = 1
    while True:
        batch = api.get(
            f"/users/{username}/repos?per_page=100&type=owner&sort=full_name&page={page}", list
        )
        for repo in batch:
            if not isinstance(repo, dict) or not isinstance(repo.get("name"), str):
                raise ValueError("GitHub returned a repository without a name")
            repositories.append(repo)
        if len(batch) < 100:
            return repositories
        page += 1


def select_repositories(repositories, config):
    excluded = {config["username"].casefold(), *(name.casefold() for name in config["exclude_repositories"])}
    eligible = [
        repo for repo in repositories
        if repo["name"].casefold() not in excluded
        and not repo.get("private") and not repo.get("archived")
        and (config["include_forks"] or not repo.get("fork"))
    ]
    ordered = sorted(eligible, key=lambda repo: repo["name"].casefold())
    sort_fields = {
        "recently_pushed": "pushed_at",
        "recently_created": "created_at",
        "most_starred": "stargazers_count",
    }
    field = sort_fields.get(config["sort"])
    if field:
        default = 0 if field == "stargazers_count" else ""
        ordered.sort(key=lambda repo: repo.get(field) or default, reverse=True)
    return ordered


def select_featured(repositories, names):
    by_name = {repo["name"].casefold(): repo for repo in repositories}
    return [by_name[name.casefold()] for name in names if name.casefold() in by_name]
