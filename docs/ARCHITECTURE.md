# Architecture

The refresh workflow installs PyYAML and runs the Python updater with its scoped GitHub Actions token. The API client requests the public account, every repository page and a page of public activity. It verifies response shapes and retries transient HTTP and network failures with bounded backoff. API failure leaves the existing published outputs available.

The repository manager filters ineligible data, applies a deterministic sort and validates featured selections against the public repository list. The updater renders the six README regions and generates a local statistics SVG. Content outside the markers remains editable. Files change only when the rendered data changes, and the workflow commits only when Git detects a difference.

Public activity uses a limited and delayed GitHub feed. Language counts cover eligible repositories and represent primary languages, rather than code volume. Account-wide commit and streak totals depend on the contribution rules and visibility of the source, so the profile uses GitHub’s native contribution view for that context.

The separate snake workflow publishes to output. The read-only validation workflow uses mocked tests, checks YAML, markers, linked local assets and SVG structure, and audits the single runtime dependency. README.template.md is the starter layout. The generated README is the committed preview and live artifact. The repository uses unittest and requires no package build configuration or duplicate preview file.
