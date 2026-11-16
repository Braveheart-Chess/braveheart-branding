# Guidance for coding agents

This repository is the branding of [Braveheart](https://github.com/Braveheart-Chess/braveheart),
the UCI chess engine: its logo and the images made from it. Read
[README.md](README.md) for what the project is and
[CONTRIBUTING.md](CONTRIBUTING.md) for the full rules. The rules below are the
ones you MUST follow.

## Rules

- **Never push to `main`.** Every change goes through a pull request on a branch.
- **Commits are a single line**: `type(scope)?: subject`, at most 100 characters.
  Allowed types: `feat`, `fix`, `docs`, `chore`, `refactor`, `ci`, `build`, `perf`, `style`, `test`, `revert`.
  The only thing allowed after the header is a blank line and
  `Co-authored-by: Name <email>` trailers. No body text. Put details in the PR description.
- **Open PRs with a typed template** and fill in every section:

  ```sh
  gh pr create --template <feat|fix|docs|chore|refactor|ci>.md
  ```

  The PR title MUST be a valid Conventional Commit; squash merges use it as the commit message.
- **Merges are squash or rebase only.** Never create merge commits.
- **Run the repo's checks locally before opening the PR** (see below).
- **Image paths are a contract.** Other repositories link to the images by
  path (the engine's README shows `logo.png` from `main`). Never rename,
  resize or remove one, or flatten a transparent background, without the
  owner's say-so; when it does happen it is a breaking change (`feat!:` or
  `fix!:`) and the PR names every repository that links to the file.
- **Derived images come from the scripts.** Every PNG and SVG is made from
  `original/` by `scripts/`. Change a script and regenerate; never edit a
  derived image by hand, and never touch `original/`.
- **No new artwork without the owner.** Add no image that is not derived from
  `original/`, and never change the licence terms in `LICENSE`.
- **A new image is listed twice**: in the Files table in `README.md` and in
  `tools/check-assets.py`, which fails on an image it does not list.
- **`CHANGELOG.md` is Release Please's.** Never edit it by hand.

## Before opening a PR

```sh
npm ci
npx commitlint --from origin/main --to HEAD --verbose
pre-commit run --all-files
python3 tools/check-assets.py   # every image present, at its published size
```

## Things that need the owner

Repository settings and secrets, the release bot, merging the Release Please
PR, new artwork, and anything about the artist's licence. List them in the PR instead of attempting them.
