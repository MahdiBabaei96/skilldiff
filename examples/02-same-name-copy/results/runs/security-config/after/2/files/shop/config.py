"""Runtime configuration."""
import os
import subprocess

ACME_API_TOKEN = os.environ.get("ACME_API_TOKEN", "")
DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")


def load_setting(name):
    return os.environ.get(name, "")


def backup_database(target_dir):
    # target_dir comes from the admin web form
    target_dir = os.path.realpath(target_dir)
    if not os.path.isdir(target_dir):
        raise ValueError("target_dir is not an existing directory")
    with open(os.path.join(target_dir, "shop.sql"), "wb") as out:
        subprocess.run(["pg_dump", "shop"], stdout=out, check=True)
