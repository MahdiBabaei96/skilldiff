"""Runtime configuration."""
import os
import subprocess

ACME_API_TOKEN = "acme_tok_9f3b2c71d8e4a6f0"
DEBUG = True


def load_setting(name):
    return os.environ.get(name, "")


def backup_database(target_dir):
    # target_dir comes from the admin web form
    subprocess.run("pg_dump shop > " + target_dir + "/shop.sql", shell=True)
