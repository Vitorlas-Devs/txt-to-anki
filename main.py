# the data file contains questions and answers (collectively referenced as a "card") that we want to parse and import into Anki

# The input format of a card is as follows (between triple backticks, the input file does not contain the triple backticks):

# ```
# 1.
# Az alább felsoroltak közül melyik nem jellemző a társadalmi és jogi normákra?
# a) A hipotetikus szerkezet.
# b) A szankció.
# -c) A múltra irányultság.
# d) Mindegyik jellemző.


# 2.
# Az alábbiak közül melyik nem tartozik a társadalmi normák lényeges mozzanatai közé?
# a) A magatartás leírása.
# b) A magatartás minősítése. (tilos, kötelező stb.)
# c) A következmények leírása.
# -d) Mindegyik oda tartozik.
# ```

# Notes on the input format:
# - the first line is a number followed by a period, they can also look like this: "5/A." and "5/B."
# - the second line is the question
# - the next lines are the answers, the correct answer is marked with a dash

# They are also organized into chapters, like this (indicated by triple backticks, there are no actual triple backticks in the input file):
# ```
# 01_Jogi_alapok
# --------------
# 1.
# {the content}
#
# 2.
# {the content}
# -----------------------------------------------------------------------------
# 02_Jogszabalytan
# ----------------
# 3.
# {the content}
# ```

# we need only need the cards, so we will ignore the chapter numbers and dashed lines

# The output format of a card is as follows (between triple backticks):

# ```
# Az alább felsoroltak közül melyik nem jellemző a társadalmi és jogi normákra?<br>a) A hipotetikus szerkezet.<br>b) A szankció.<br>c) A múltra irányultság.<br>d) Mindegyik jellemző.	c) A múltra irányultság.
# Az alábbiak közül melyik nem tartozik a társadalmi normák lényeges mozzanatai közé?<br>a) A magatartás leírása.<br>b) A magatartás minősítése. (tilos, kötelező stb.)<br>c) A következmények leírása.<br>d) Mindegyik oda tartozik.	d) Mindegyik oda tartozik.
# ```

# Notes on the output format:
# - it is all on one line
# - we insert a line break after the question and after each answer
# - we repeat the correct answer at the end of the line after a tab

# Let's begin!
import os
import re

input_file = "data/questions.txt"
output_file = "out/anki.txt"


# split the content into cards: remove the chapter numbers and dashed lines
def preprocess(content):
    # split the content into chapters by lines that start with more than 2 dashes
    chapters = content.split("\n---")

    # remove the first entry
    chapters.pop(0)

    # remove the remaining dashed lines from the beginning of each chapter
    for i in range(len(chapters)):
        chapters[i] = chapters[i].strip("-").strip()

    # remove the entries that start with a number followed by an underscore
    regex = r"^\d+_.+$"
    chapters = [
        chapter
        for chapter in chapters
        if not re.match(regex, chapter, flags=re.MULTILINE)
    ]

    # join the chapters back together
    content = "\n".join(chapters)

    return content


# convert the cards into the output format
def format(content):
    # split the content into cards by lines that start with a number (any number) and end with a period
    regex = r"^\d+(?:\.|\/\D\.)"

    cards = re.split(regex, content, flags=re.MULTILINE)

    cards.pop(0)

    # format each card
    for i in range(len(cards)):
        # split the content into lines
        lines = cards[i].strip().split("\n")

        # get the question (the first line) and remove it from the list
        question = lines.pop(0)

        # get the correct answer (the answer that starts with a dash)
        correct_answer = [line for line in lines if line.startswith("-")][0].strip("-")

        # concatenate the question and answers into one string according to the output format
        cards[i] = f"{question}<br>{lines}\t{correct_answer}"

    # join the cards back together
    content = "\n".join(cards)

    return content


# We open the input file and read its contents into a variable
with open(input_file, "r", encoding="utf-8") as file:
    content = file.read()

# preprocess the content
content = preprocess(content)

# format the content
content = format(content)

# create the output directory and file if they don't exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Write the cards to the output file
with open(output_file, "w", encoding="utf-8") as file:
    # anki format specifiers
    content = "separator:tab\nhtml:true\n" + content

    # write to the output
    file.write(content)
