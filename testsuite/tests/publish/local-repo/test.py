"""
Tests for proper publishing using a local repo as reference
"""

from drivers.alr import init_local_crate, run_alr
from drivers.asserts import assert_match
from drivers.helpers import init_git_repo
from glob import glob
from shutil import rmtree
from subprocess import run

import os


def verify_manifest():
    target = os.path.join("alire", "releases", "xxx-0.0.0.toml")
    assert os.path.isfile(target), \
        "Index manifest not found at expected location"
    # Clean up for next test
    rmtree(os.path.join("alire", "releases"))


# Prepare our "remote" repo
init_local_crate("xxx", enter=False)
head_commit = init_git_repo("xxx")

# Clone to a "local" repo and set minimal config
assert run(["git", "clone", "xxx", "xxx_local"]).returncode == 0
os.chdir("xxx_local")
assert run(["git", "config", "user.email", "alr@testing.com"]).returncode == 0
assert run(["git", "config", "user.name", "Alire Testsuite"]).returncode == 0

# Tests with different default arguments that must all succeed
run_alr("--force", "publish")
verify_manifest()

run_alr("--force", "publish", ".")
verify_manifest()

run_alr("--force", "publish", ".", "master")
verify_manifest()

run_alr("--force", "publish", ".", "HEAD")
verify_manifest()

# Verify that a dirty repo precludes publishing
with open("lasagna", "wt") as file:
    file.write("wanted\n")

p = run_alr("--force", "publish", complain_on_error=False)
assert_match(".*git status reports working tree not clean.*", p.out)

# Even if changes are committed but not pushed
assert run(["git", "add", "."]).returncode == 0
assert run(["git", "commit", "-a", "-m", "please"]).returncode == 0
p = run_alr("--force", "publish", complain_on_error=False)
assert_match(".*Repository has commits yet to be pushed.*", p.out)

print('SUCCESS')
