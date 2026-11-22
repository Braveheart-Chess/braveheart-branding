# Contributing

This repository is the branding of [Braveheart](https://github.com/Braveheart-Chess/braveheart),
the UCI chess engine. Engine changes belong in the engine repository; the logo
and the images made from it belong here.

## Setup

```sh
npm ci                                                          # commitlint
pre-commit install --hook-type commit-msg --hook-type pre-commit
```

The hooks are a convenience. CI is the authoritative check.

## Checks

| CI job | What it runs | Locally |
| --- | --- | --- |
| `Commit messages` | commitlint over every commit in `base..head` | `npx commitlint --from origin/main --to HEAD --verbose`, then `npm run test:commitlint` |
| `PR title` | The title passes commitlint, scope included | |
| `Assets` | Every image is present, at its published size, with a transparent background where it should have one | `python3 tools/check-assets.py` |

## Changing the images

- Every PNG and SVG is derived from the artist's files in `original/` by the
  scripts in `scripts/`; [README.md](README.md#regenerating-the-images) has
  the commands. Change a script and regenerate. Never edit a derived image by
  hand, and never change `original/`.
- Other repositories link to the images by path, so file names, sizes and
  transparent backgrounds stay put. Changing one is a breaking change
  (`feat!:` or `fix!:`); see [Linking to the images](README.md#linking-to-the-images).
- A new image goes in the Files table in `README.md` and in
  `tools/check-assets.py`.
- Say in the pull request how the images look, in GitHub's light and dark
  themes where transparency matters.

## Commit messages

Every commit is a **single-line** [Conventional Commit](https://www.conventionalcommits.org/) with a type and a scope:

```
type(scope): subject
```

- At most 100 characters, with an imperative, lowercase subject and no trailing period.
- `type` is one of `feat`, `fix`, `perf`, `revert`, `docs`, `refactor`, `test`, `build`, `ci`, `style`, `chore`: the same set in every repository.
- `scope` is required: exactly one of the scopes below. A change that spans two is two pull requests, or takes the scope it is mostly about.
- Breaking changes are marked with `!`, for example `feat(logo)!: rename logo.png to logo-big.png`.
- The only content allowed after the header is a blank line followed by `Co-authored-by: Name <email>` trailers, in any letter case. No body text. Details belong in the PR description.
- The type drives the next version: `feat` bumps the minor version, `fix` the patch, and `!` the major (the minor while the version is below 1.0).

| Message | Valid |
| --- | --- |
| `feat(logo): add a dark-background avatar` | Yes |
| `fix(logo): keep the eyes opaque in the favicon` + blank line + `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` | Yes |
| `feat: add a dark-background avatar` | No, no scope |
| `feat(nope): add a dark-background avatar` | No, not one of this repository's scopes |
| `feat(logo): add a dark-background avatar` + blank line + `This adds…` | No, body text |

commitlint enforces this with `@commitlint/config-conventional` plus three local rules in `tools/commitlint/`: `only-coauthor-trailers` fails on any line after the header that is not blank or a `Co-authored-by` trailer, `single-scope` fails on a list such as `feat(a,b)`, and `subject-lowercase` requires a lowercase subject except in Dependabot's fixed `chore(deps): Bump ...`. The fixtures in `tests/commitlint/` show accepted and rejected messages. CI lints every commit in the PR range, so a rebase merge never lands a non-conforming commit on `main`, and lints the PR title through the same config. The standard behind it is the [repository conventions](https://github.com/jwallace145/repository-template/blob/main/repository-conventions.md).

### Scopes

Every commit names exactly one of this repository's scopes. They are `SCOPES` in `commitlint.config.mjs`; this table mirrors it, in the same order, and `npm run test:commitlint` fails if they drift. Adding, renaming or removing a scope goes through a pull request like any other change.

| Scope | Covers |
| --- | --- |
| `logo` | The logo, small logo, SVGs, avatar and favicons, and the scripts that draw them |
| `banner` | The README banners and `scripts/make_banner.py` |
| `social` | The social preview image |
| `checks` | `tools/check-assets.py` and the Assets job |
| `repo` | README, CONTRIBUTING, AGENTS, commitlint, the PR and issue templates, and repository tooling |
| `deps` | Dependency updates, mostly Dependabot's |
| `release` | Release Please's release pull requests and its config |

## Pull requests

Every change reaches `main` through a pull request. Nobody pushes to `main`.

- The title is a valid commit header, scope included: squash merges use it as the commit message. Release Please's own pull requests are titled `chore(release): release X.Y.Z`.
- Fill in every section of the one template, `.github/pull_request_template.md` (Summary, Why, Changes, Verification, Checklist). Write "n/a" rather than deleting one.
- Pull requests merge by squash or rebase only. There are no merge commits.
- Dependabot's titles are `chore(deps): bump ...` and pass as they are; squash merge them.

## Issues

Open issues from the forms: **Bug**, **Feature** or **Task**. Blank issues are off.
## Releases

[Release Please](https://github.com/googleapis/release-please) keeps a release
pull request open with the next version and the changelog. Merging it tags the
version. It owns `CHANGELOG.md`; nobody edits that file by hand.

The release pull request is authored by the `braveheart-chess-release-bot`
GitHub App, the organisation's release bot, so CI runs on it. The workflow
reads the app's credentials from the secrets `RELEASE_BOT_CLIENT_ID` and
`RELEASE_BOT_PRIVATE_KEY`.
