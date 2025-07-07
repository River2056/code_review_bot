from abc import abstractmethod
import os
import subprocess
import sys


class ContentFetcher:

    @abstractmethod
    def fetch_content_for_review(self) -> str:
        pass


class GitDiffContentFetcher(ContentFetcher):

    def __init__(self, repo_location, dest_branch, review_branch):
        self.repo_location = repo_location
        self.dest_branch = dest_branch
        self.review_branch = review_branch

    def _run(self, *args):
        subprocess.run([*args])

    def fetch_content_for_review(self) -> str:
        original_location = os.getcwd()
        os.chdir(self.repo_location)
        self._run("git", "reset", "--hard", "HEAD")
        self._run("git", "fetch", "--all")
        self._run("git", "checkout", self.dest_branch)
        self._run("git", "pull", "origin", self.dest_branch)
        self._run("git", "checkout", self.review_branch)
        clone_branch_for_review = f"{self.review_branch}_review"

        # check if clone_branch_for_review already exists, delete if exists
        self._run("git", "branch", "-D", clone_branch_for_review)

        self._run("git", "checkout", "-b", clone_branch_for_review)
        rebase_result = subprocess.run(["git", "rebase", self.dest_branch])
        try:
            rebase_result.check_returncode()
        except Exception as e:
            print("error occurred while rebase operation for review branch! abort...")
            print(e)
            sys.exit(1)
        git_diff = subprocess.run(
            ["git", "diff", f"{self.dest_branch}..{clone_branch_for_review}"],
            capture_output=True,
            text=True,
        )
        content = git_diff.stdout

        # delete clone_branch_for_review after getting diff
        self._run("git", "checkout", self.review_branch)
        self._run("git", "branch", "-D", clone_branch_for_review)
        os.chdir(original_location)

        return content
