from abc import abstractmethod
from datetime import datetime
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM


class ReviewBot:

    @abstractmethod
    def do_review(self):
        pass


class OllamaReviewBot(ReviewBot):

    def __init__(self, config, content):
        self.config = config
        self.output_dir = self.config["paths"]["output-dir"]
        self.dest_branch = self.config["git"]["dest-branch"]
        self.review_branch = self.config["git"]["review-branch"]
        self.language = self.config["general"]["language"]
        self.model = OllamaLLM(
            model=self.config["ai"]["model"], num_ctx=self.config["ai"]["num-ctx"]
        )
        with open(os.path.join(os.getcwd(), "prompt.md")) as prompt_file:
            self.template = prompt_file.read()
        self.content = content
        self.msgs = []
        self.prompt = ChatPromptTemplate.from_template(self.template)
        self.chain = self.prompt | self.model

    def do_review(self):
        result = self.chain.invoke(
            {"content": self.content, "language": self.language, "question": ""}
        )
        print(result)
        self.msgs.append("\n")
        self.msgs.append(result)

        while True:
            question = input("questions to ask (type q to quit): ")
            if "q" == question:
                break

            result = self.chain.invoke(
                {
                    "content": self.content,
                    "language": self.language,
                    "question": question,
                }
            )
            print(result)
            self.msgs.append(question)
            self.msgs.append("\n")
            self.msgs.append(result)

        log_file_name = f"{datetime.now().strftime("%Y%m%d_%H%M%S")}_{self.dest_branch.replace("/", "_")}..{self.review_branch.replace("/", "_")}.log"
        with open(
            os.path.join(
                os.getcwd(),
                self.output_dir,
                log_file_name,
            ),
            "wt",
            encoding="utf8",
        ) as log_file:
            # msgs
            for msg in self.msgs:
                log_file.write(msg)
                log_file.write("\n")

            # git diff content
            log_file.write(self.content)
            log_file.write("\n")
