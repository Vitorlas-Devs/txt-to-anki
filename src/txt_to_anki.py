import os
import re
import json


class TxtToAnki:
    def __init__(self, input_file, output_file, JSON=False):
        self.input_file = input_file
        self.output_file = output_file
        self.JSON = JSON
        self.content = ""
        self.chapter_titles = []
        self.chapter_counts = {}

    def preprocess(self):
        # split the content into chapters
        chapters = self.content.split("\n---")

        chapters[0] = chapters[0].strip("\ufeff")

        for i in range(len(chapters)):
            chapters[i] = chapters[i].strip("-").strip()

        re_chapter = r"^\d+_.+$"
        chapter_titles = [
            chapter for chapter in chapters if re.match(re_chapter, chapter)
        ]
        chapters = [
            chapter for chapter in chapters if not re.match(re_chapter, chapter)
        ]

        for i in range(len(chapter_titles)):
            self.chapter_counts[chapter_titles[i]] = chapters[i].count("\n\n")

        self.content = "\n".join(chapters)
        self.chapter_titles = chapter_titles

    def format(self):
        # split the content into cards
        re_question = r"^\d+(?:\.|\/\D\.)"

        cards = re.split(re_question, self.content, flags=re.MULTILINE)

        cards.pop(0)

        # format each card
        chapter_counter = 0
        for i in range(len(cards)):
            lines = cards[i].strip().split("\n")
            question = lines.pop(0)

            correct_answer = [line for line in lines if line.startswith("-")][0].strip(
                "-"
            )

            lines = "<br>".join([line.strip("-") for line in lines])

            chapter_title = list(self.chapter_counts.keys())[chapter_counter]
            cards[i] = f"{question}<br>{lines}\t{correct_answer}\t{chapter_title}"

            self.chapter_counts[chapter_title] -= 1
            if (
                self.chapter_counts[chapter_title] == 0
                and chapter_counter < len(self.chapter_counts) - 1
            ):
                chapter_counter += 1

        self.content = "\n".join(cards)

    def parseJSON(self):
        data = json.loads(self.content)

        cards = []

        for qa_set in data:
            question = qa_set["question"]

            answers = qa_set["answers"]
            correct_answer = next((a["answer"] for a in answers if a["rigth"]), None)

            answers_str = "<br>".join(
                [f"{chr(97 + i)}) {a['answer']}" for i, a in enumerate(answers)]
            )

            card = f"{question}<br>{answers_str}\t{correct_answer}"
            cards.append(card)

        self.content = "\n".join(cards)

    def run(self):
        with open(self.input_file, "r", encoding="utf-8") as f:
            self.content = f.read()

        if self.JSON:
            self.parseJSON()
        else:
            self.preprocess()
            self.format()

        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(self.content)
