"""Runtime configuration."""
import os
import subprocess

ACME_API_TOKEN = os.environ.get("ACME_API_TOKEN", "")
DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")


def load_setting(name):
    return os.environ.get(name, "")


def backup_database(target_dir):
    # target_dir comes from the admin web form
    target = os.path.join(os.path.realpath(target_dir), "shop.sql")
    subprocess.run(["pg_dump", "--file", target, "shop"], check=True)
