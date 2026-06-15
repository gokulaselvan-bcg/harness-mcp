# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.4] - 2026-06-08

### Added

- Documentation site now publishes each minor release under a stable, immutable URL
  (`/agentic-coding/X.Y/`). `peaceiris/actions-gh-pages` (pinned to v4.1.0 SHA)
  replaces `actions/deploy-pages`; `keep_files: true` preserves older minor
  directories on every deploy (GH-97).
- `VersionSelector` component injected into the Starlight header lets readers switch
  between published minor versions. `update-versions.mjs` maintains the
  `versions.json` manifest (semver-sorted, `latest` always semver-max) (GH-97).

### Changed

- refactor: remove `/templates/` directory; templates now live inside owning skills (GH-90).
- Workflow docs for `spec`, `plan`, and `implement` moved from
  `docs/src/content/docs/workflows/` into `workflows/developer/` to match the
  sidebar taxonomy. All inbound links and sidebar slug entries updated. No content
  changed (GH-98).

### Fixed

- Pre-existing `ruff` D205 and E501 violations in `tests/test_install_sh.py` resolved:
  six docstrings reformatted to PEP 257 summary + body structure; one long shell
  line inside an f-string broken with a `\` continuation.

## [1.0.3] - 2026-06-02

### Fixed

- PRD skill (`.claude/skills/prd/`) referenced a template at
  `templates/prd_template.md` that does not exist in the release
  tarball, so the skill failed at runtime as soon as it tried to
  read it (GH-89). The canonical template is now bundled inside the
  skill directory as `PRD-TEMPLATE.md` and referenced via relative
  markdown links, making the skill self-contained.

### Changed

- Release workflow `verify-tag` job now accepts tags whose commit is
  reachable from `origin/main` **or** any `origin/release/*`
  stabilisation branch. Previously only `origin/main` was accepted,
  which blocked shipping patches from a release branch (e.g.
  `release/1.0`) without first merging back to `main`. The job probes
  for `release/*` branches with `git ls-remote --exit-code` before
  fetching so a benign "no release branches yet" state (exit 2) is
  distinguished from a real network or auth failure. Release-process
  documentation updated to match.

## [1.0.2] - 2026-05-11

### Fixed

- `install.sh` now downloads release assets via `gh release download`
  when the GitHub CLI is installed and authenticated. GitHub's
  browser-style `/releases/.../download/<asset>` URL does not honor
  `Authorization: Bearer <token>` headers — for private repos it
  returns 404 regardless of any token — which made the install
  one-liner unusable for private installs. The gh path uses the API
  endpoint, which respects token auth. The previous curl/wget path is
  retained as a fallback for environments without `gh` (works for
  public repos).

### Changed

- `verify_tarball_checksum` accepts an optional local sidecar path; the
  gh path passes the `.sha256` file it downloaded alongside the tarball,
  so no second network fetch happens and the `latest`-vs-tag race for
  sidecar resolution is gone for the gh path.
- `--help` text reorganized to make the gh-preferred / curl-fallback
  relationship explicit.

## [1.0.1] - 2026-05-11

### Fixed

- Release workflow tag-push glob `[0-9]*[0-9].[0-9]*[0-9].[0-9]*[0-9]`
  required ≥2 characters per segment in minimatch, so single-digit tags
  like `1.0.0` silently failed to trigger the workflow and no release
  asset was published. Replaced with `[0-9]*.[0-9]*.[0-9]*` (plus a
  pre-release variant) and rely on the existing `verify-tag` regex for
  canonical SemVer enforcement.

## [1.0.0] - 2026-05-11

### Added

- `build.sh` script that produces pre-filtered, BOM-bearing distribution tarballs
  (`dist/agentic-coding.tar.gz`) for both local development (`--local`) and tagged
  releases (`--tag X.Y.Z`).
- `install.sh --version X.Y.Z` flag to install a specific tagged release.
- `install.sh --local <path>` flag to install from a local tarball produced by `build.sh`.
- `install.sh` (no flags) now resolves and installs the latest GitHub Release.
- Resolved version is printed during install (e.g. `Installing agentic-coding 1.0.0...`).
- `CHANGELOG.md` following the Keep a Changelog format.
- GitHub Actions release workflow that triggers on tag push, validates the changelog
  entry, builds the release tarball, and publishes a GitHub Release with the tarball
  attached as an asset.
- Documentation site changelog page rendered from `CHANGELOG.md`.

### Changed

- `install.sh` now consumes pre-built release artifacts instead of filtering the
  source tree at install time. Filtering and BOM generation moved to `build.sh`.
- Production documentation deployment now triggers on release publication rather
  than every push to `main`.

### Removed

- `install.sh --ref` flag has been removed. Use `--version <version>` for tagged
  releases or `--local <path>` for locally built tarballs. Passing `--ref` now exits
  with an explanatory error.

[Unreleased]: https://github.com/bcgx-pi-genx-training/agentic-coding/compare/1.0.4...HEAD
[1.0.4]: https://github.com/bcgx-pi-genx-training/agentic-coding/compare/1.0.3...1.0.4
[1.0.3]: https://github.com/bcgx-pi-genx-training/agentic-coding/compare/1.0.2...1.0.3
[1.0.2]: https://github.com/bcgx-pi-genx-training/agentic-coding/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/bcgx-pi-genx-training/agentic-coding/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/bcgx-pi-genx-training/agentic-coding/releases/tag/1.0.0
