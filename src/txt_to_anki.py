import os
import re


class TxtToAnki:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.content = ""
        self.chapter_titles = []
        self.chapter_counts = {}

    def preprocess(self):
        # split the content into chapters
        chapters = self.content.split("\n---")

        chapters[0] = chapters[0].strip("\ufeff")

        for i in range(len(chapters)):
            chapters[i] = chapters[i].strip("-").strip()

        regex = r"^\d+_.+$"

        chapter_titles = [chapter for chapter in chapters if re.match(regex, chapter)]

        for i in range(len(chapter_titles)):
            chapter_titles[i] = (
                chapter_titles[i][:2] + "." + chapter_titles[i][2:]
            ).replace("_", " ")

        chapters = [chapter for chapter in chapters if not re.match(regex, chapter)]

        for i in range(len(chapter_titles)):
            self.chapter_counts[chapter_titles[i]] = chapters[i].count("\n\n") + 1

        self.content = "\n".join(chapters)
        self.chapter_titles = chapter_titles

    def format(self):
        # split the content into cards
        regex = r"^\d+(?:\.|\/\D\.)"

        cards = re.split(regex, self.content, flags=re.MULTILINE)

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
            if self.chapter_counts[chapter_title] == 0:
                chapter_counter += 1

        self.content = "\n".join(cards)

    def run(self):
        with open(self.input_file, "r", encoding="utf-8") as f:
            self.content = f.read()

        self.preprocess()
        self.format()

        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(self.content)
