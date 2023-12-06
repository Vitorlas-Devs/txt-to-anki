from src.txt_to_anki import TxtToAnki

txt_to_anki = TxtToAnki("data/questions.txt", "out/anki.tsv")
txt_to_anki.run()