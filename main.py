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
    try:
        os.makedirs(output_log_dir)
    except:
        print("output dir already exists, skip creating...")

    # fetch content (git diff)
    # fetch -> pull -> then checkout a new branch for review -> rebase to dest_branch for related diffs only
    fetcher = GitDiffContentFetcher(config)
    content = fetcher.fetch_content_for_review()

    # construct llm and prompt for review
    bot = OllamaReviewBot(config=config, content=content)
    bot.do_review()


if __name__ == "__main__":
    main()
