#!/usr/bin/env python3
"""
setup.py — One-shot setup for rentalincostarica.com home repo.

Run this from inside the `luiskarlos.github.io` folder on your Mac:

    cd ~/path/to/luiskarlos.github.io
    python3 setup.py

What it does (in order):
  1. If this folder is nested inside `jaco-live-local/`, move it up so it
     becomes a sibling — repos shouldn't be nested.
  2. Wipe and re-init git history (clean slate, single commit on `main`).
  3. Verify `gh` is installed and authenticated.
  4. Create the public GitHub repo `luiskarlos.github.io` and push.
  5. Enable GitHub Pages: Source = main branch, /docs folder.
  6. Confirm the CNAME (rentalincostarica.com) is in place.
  7. Print DNS records to add in GoDaddy.

Re-running is safe: if the repo already exists, the script force-pushes
and re-applies the Pages config.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = "luiskarlos.github.io"
DOMAIN = "rentalincostarica.com"
BRANCH = "main"
DOCS = "/docs"


# -----------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------
def run(cmd, *, capture=False, check=True, cwd=None, env=None, quiet=False):
    if not quiet:
        printable = cmd if isinstance(cmd, str) else " ".join(cmd)
        print(f"  $ {printable}")
    res = subprocess.run(
        cmd,
        shell=isinstance(cmd, str),
        capture_output=capture,
        text=True,
        cwd=cwd,
        env=env,
    )
    if check and res.returncode != 0:
        if capture:
            sys.stderr.write(res.stdout or "")
            sys.stderr.write(res.stderr or "")
        sys.exit(f"ERROR: command failed (exit {res.returncode})")
    return res


def step(msg):
    print(f"\n\033[1;36m== {msg} ==\033[0m")


def need(cmd, hint):
    if shutil.which(cmd) is None:
        sys.exit(f"ERROR: `{cmd}` not found. {hint}")


# -----------------------------------------------------------------
# Main
# -----------------------------------------------------------------
def main():
    here = Path(__file__).parent.resolve()

    # ---------- 0. Sanity checks ----------
    need("gh", "Install GitHub CLI: https://cli.github.com (brew install gh)")
    need("git", "Install Git first.")

    if not (here / "docs").is_dir():
        sys.exit(f"ERROR: expected `docs/` next to setup.py at {here}")

    # ---------- 1. Move out of jaco-live-local if nested ----------
    repo_path = here
    if repo_path.parent.name == "jaco-live-local":
        target = repo_path.parent.parent / REPO
        step(f"Moving repo out of jaco-live-local → {target}")
        if target.exists():
            print(f"  {target} already exists. Skipping move.")
        else:
            shutil.move(str(repo_path), str(target))
            repo_path = target
            print(f"  Moved. New location: {repo_path}")
            print(f"  Re-running from new path...")
            os.chdir(repo_path)
            os.execv(sys.executable, [sys.executable, str(repo_path / "setup.py")])
    os.chdir(repo_path)

    # ---------- 2. gh auth check ----------
    step("Checking gh auth")
    res = run(["gh", "auth", "status"], capture=True, check=False, quiet=True)
    if res.returncode != 0:
        sys.exit("ERROR: not logged in. Run: gh auth login")
    print((res.stderr or res.stdout).strip().splitlines()[0])

    # ---------- 3. Get GitHub username ----------
    user = run(["gh", "api", "user", "--jq", ".login"], capture=True).stdout.strip()
    print(f"  Logged in as: {user}")
    expected_repo = REPO  # luiskarlos.github.io literally — must match user login for user-site behavior
    if user.lower() != "luiskarlos":
        print(
            f"\n  WARNING: gh is logged in as `{user}` but the repo name is `{REPO}`."
        )
        print(
            "  GitHub Pages user-site only works if repo name = `<your-username>.github.io`."
        )
        print(
            f"  For your account it should be `{user}.github.io`. The script will continue,"
        )
        print("  but you may want to rename the repo.")
        expected_repo = f"{user}.github.io"

    # ---------- 4. Verify CNAME ----------
    step("Verifying docs/CNAME")
    cname = repo_path / "docs" / "CNAME"
    if not cname.exists() or cname.read_text().strip() != DOMAIN:
        cname.write_text(f"{DOMAIN}\n")
        print(f"  wrote {cname}")
    else:
        print(f"  OK ({DOMAIN})")

    # ---------- 5. Reset git history ----------
    step("Resetting git history (clean single commit)")
    git_dir = repo_path / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir)
    run(["git", "init", "-q", "-b", BRANCH])
    run(["git", "config", "user.email", f"{user}@users.noreply.github.com"])
    run(["git", "config", "user.name", user])
    run(["git", "add", "-A"])
    run(["git", "commit", "-q", "-m", f"Initial commit: {DOMAIN} home (bilingual ES/EN)"])

    # ---------- 6. Create or update GitHub repo ----------
    step(f"Creating/syncing {user}/{expected_repo} on GitHub")
    res = run(["gh", "repo", "view", f"{user}/{expected_repo}"], capture=True, check=False, quiet=True)
    if res.returncode == 0:
        print(f"  Repo already exists. Force-pushing.")
        run(["git", "remote", "remove", "origin"], capture=True, check=False, quiet=True)
        run(["git", "remote", "add", "origin", f"https://github.com/{user}/{expected_repo}.git"])
        run(["git", "push", "-f", "-q", "-u", "origin", BRANCH])
    else:
        print(f"  Creating new public repo and pushing initial commit.")
        run([
            "gh", "repo", "create", f"{user}/{expected_repo}",
            "--public",
            "--source", ".",
            "--remote", "origin",
            "--push",
            "--description", f"Home portfolio for {DOMAIN}",
        ])

    # ---------- 7. Enable Pages from /docs on main ----------
    step("Enabling GitHub Pages (source: /docs on main)")
    api_repo = f"repos/{user}/{expected_repo}/pages"
    # Try POST first (creates the Pages site)
    res = run([
        "gh", "api", "-X", "POST", api_repo,
        "-H", "Accept: application/vnd.github+json",
        "-f", f"source[branch]={BRANCH}",
        "-f", "source[path]=/docs",
    ], capture=True, check=False, quiet=True)
    if res.returncode == 0:
        print("  Pages enabled.")
    else:
        # If it already exists, update with PUT
        res2 = run([
            "gh", "api", "-X", "PUT", api_repo,
            "-H", "Accept: application/vnd.github+json",
            "-f", f"source[branch]={BRANCH}",
            "-f", "source[path]=/docs",
        ], capture=True, check=False, quiet=True)
        if res2.returncode == 0:
            print("  Pages already existed; source updated.")
        else:
            print("  Couldn't auto-configure Pages. Set it manually:")
            print(f"    Settings -> Pages -> Source: Branch=main, Folder=/docs")
            print(f"  API errors: POST={res.stderr.strip()} | PUT={res2.stderr.strip()}")

    # ---------- 8. Print summary ----------
    print()
    print("\033[1;32m" + "=" * 64 + "\033[0m")
    print("\033[1;32m  DONE — repo created, pushed, Pages configured\033[0m")
    print("\033[1;32m" + "=" * 64 + "\033[0m")
    print(f"  Repo:        https://github.com/{user}/{expected_repo}")
    print(f"  Pages URL:   https://{user}.github.io  (also serves {DOMAIN} once DNS resolves)")
    print(f"  Local path:  {repo_path}")
    print()
    print("\033[1mNEXT STEP — DNS in GoDaddy\033[0m")
    print("  Replace any default `A @` and `CNAME @` parking records with these:")
    print("    A     @     185.199.108.153")
    print("    A     @     185.199.109.153")
    print("    A     @     185.199.110.153")
    print("    A     @     185.199.111.153")
    print(f"    CNAME www   {user}.github.io")
    print()
    print("  Then wait for DNS (10 min - 24 h). Verify with:")
    print(f"    dig {DOMAIN} +short    # should return the four 185.199.108-111.153 IPs")
    print()
    print("  Once GitHub validates the domain (green check in Settings -> Pages),")
    print("  turn on 'Enforce HTTPS'.")
    print()


if __name__ == "__main__":
    main()
