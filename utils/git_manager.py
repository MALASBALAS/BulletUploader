# utils/git_manager.py

import subprocess

class GitManager:
    def create_branch(self, branch_name):
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)

    def add_all_changes(self):
        subprocess.run(["git", "add", "-A"], check=True)

    def commit(self, message):
        subprocess.run(["git", "commit", "-m", message], check=True)

    def push(self, branch_name):
        subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)
