from datetime import datetime
import os
import subprocess
import sys
import tomllib

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM


def read_config():
    with open(os.path.join(os.getcwd(), "config.toml")) as config_file:
        return tomllib.loads(config_file.read())


def run(*args):
    subprocess.run([*args])


def main():
    config = read_config()
    original_location = os.getcwd()

    # fetch content (git diff)
    # fetch -> pull -> then checkout a new branch for review -> rebase to dest_branch for related diffs only
    review_branch = config["git"]["review-branch"]
    dest_branch = config["git"]["dest-branch"]
    repo_location = config["paths"]["repo-location"]
    os.chdir(repo_location)
    run("git", "reset", "--hard", "HEAD")
    run("git", "fetch", "--all")
    run("git", "checkout", dest_branch)
    run("git", "pull", "origin", dest_branch)
    run("git", "checkout", review_branch)
    new_branch_for_review = f"{review_branch}_review"
    run("git", "checkout", "-b", new_branch_for_review)
    rebase_result = subprocess.run(["git", "rebase", dest_branch])
    try:
        rebase_result.check_returncode()
    except Exception as e:
        print("error occurred while rebase operation for review branch! abort...")
        print(e)
        sys.exit(1)

    git_diff = subprocess.run(
        ["git", "diff", f"{dest_branch}..{new_branch_for_review}"],
        capture_output=True,
        text=True,
    )
    content = git_diff.stdout

    # delete new_branch_for_review after getting diff
    run("git", "checkout", review_branch)
    run("git", "branch", "-D", new_branch_for_review)
    os.chdir(original_location)

    # construct llm and prompt for review
    model = OllamaLLM(model=config["ai"]["model"])
    template = """
        You are a professional programmer with years of coding experience.
        Here's some diff, carefully sutdy it and provide code reviews and
        analysis based on good practices and conventions:
        ```
        {content}
        ```
        Optionally, provide any refactoring suggestions if necessary,
        provide any refactoring code examples if you decide to give a suggestion.
        If you decide to give an advice and refactoring examples, print out the original
        code snippet you are reviewing followed by your suggestion for better comparison.
        Do not skip any line of code without reviewing, if you think the code is good enough and don't need any suggestions,
        simply print out the original code snippet with your comments.
        Respond with additional advice if asked any questions: {question}
    """
    msgs = []
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    result = chain.invoke({"content": content, "question": ""})
    print(result)
    msgs.append("")
    msgs.append(result)

    # while loop for asking questions
    while True:
        question = input("questions to ask (type q to quit): ")
        if "q" == question:
            break

        result = chain.invoke({"content": content, "question": question})

        print(result)
        msgs.append(question)
        msgs.append(result)

    # output messages for future reviewing
    with open(
        os.path.join(
            os.getcwd(),
            config["paths"]["output-dir"],
            f"{datetime.now().strftime("%Y%m%d_%H%M%S")}_{dest_branch}..{review_branch}.log",
        ),
        "wt",
        encoding="utf8",
    ) as log_file:
        for msg in msgs:
            log_file.write(msg)
            log_file.write("\n")


if __name__ == "__main__":
    main()
