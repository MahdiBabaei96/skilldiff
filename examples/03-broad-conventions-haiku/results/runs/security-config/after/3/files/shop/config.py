"""Runtime configuration."""
import os
import subprocess

ACME_API_TOKEN = os.environ.get("ACME_API_TOKEN", "")
DEBUG = os.environ.get("SHOP_DEBUG", "").lower() in ("1", "true", "yes")


def load_setting(name):
    return os.environ.get(name, "")


def backup_database(target_dir):
    # target_dir comes from the admin web form; no shell, so it cannot inject commands
    subprocess.run(
        ["pg_dump", "shop", "-f", os.path.join(target_dir, "shop.sql")],
        check=True,
    )
