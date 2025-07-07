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
        self.model = OllamaLLM(model=self.config["ai"]["model"])
        self.template = """
            You are a professional programmer with years of coding experience.
            Here's some diff, carefully sutdy it and provide code reviews and
            analysis based on good practices and conventions:
            ```
            {content}
            ```
            This code is written in {language}, please review according to this language's best practices and conventions.
            Provide any refactoring suggestions if necessary.
            Provide any refactoring code examples if you decide to give a suggestion.
            If you decide to give an advice and refactoring examples, print out the original
            code snippet you are reviewing followed by your suggestion for better comparison.
            Do not skip any line of code without reviewing, if you think the code is good enough and don't need any suggestions,
            simply print out the original code snippet with your comments.
            In your response, you should list out issues you think are most critical at the top,
            your priority should be critical > high > medium > low.
            In your response, first mention what changes are made, followed by your code review, then any refactoring examples.
            Modifications with simple key value pairs are config files, or property files, Do mention it in your change history, but
            do not attempt to review these changes, focus only on actual code.

            If the file you are reviewing is a typescript file using the Angular framework, here are some additional rules you should consider:
            1. Use OnPush change detection for components that don't need frequent updates.
            2. Avoid complex expressions in templates; move logic to the component class.
            3. Use trackBy in ngFor for efficient list rendering.
            4. Lazy load modules and components with the Angular Router.

            Respond with additional advice if asked any questions: {question}
        """
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
            for msg in self.msgs:
                log_file.write(msg)
                log_file.write("\n")
