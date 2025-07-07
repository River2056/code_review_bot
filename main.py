import os
import tomllib

from bots.bot import OllamaReviewBot
from fetchers.fetcher import GitDiffContentFetcher


def read_config():
    with open(os.path.join(os.getcwd(), "config.toml")) as config_file:
        return tomllib.loads(config_file.read())


def main():
    config = read_config()
    output_log_dir = config["paths"]["output-dir"]
    os.makedirs(output_log_dir)

    # fetch content (git diff)
    # fetch -> pull -> then checkout a new branch for review -> rebase to dest_branch for related diffs only
    review_branch = config["git"]["review-branch"]
    dest_branch = config["git"]["dest-branch"]
    repo_location = config["paths"]["repo-location"]
    fetcher = GitDiffContentFetcher(repo_location, dest_branch, review_branch)
    content = fetcher.fetch_content_for_review()

    # construct llm and prompt for review
    bot = OllamaReviewBot(
        model=config["ai"]["model"],
        language=config["general"]["language"],
        content=content,
        output_dir=config["paths"]["output-dir"],
        dest_branch=dest_branch,
        review_branch=review_branch,
    )
    bot.do_review()


if __name__ == "__main__":
    main()
