from texts import correct_para_texts as _texts, MUTILATED, PRACTICE
from makescn import cm

text_dict = {}
title_dict = {}

for text in _texts:
    if text.type in (MUTILATED, PRACTICE):
        continue
    paragraphs = []
    paragraph = []
    iterator = text.indexed_and_numbered_display_sentences()
    for sentence_i, numbers, display_words in iterator:
        if sentence_i in text.sentence_idxs:
            for number, display_word in zip(numbers, display_words):
                last_in_sentence = (number == numbers[-1])
                last_in_paragraph = (last_in_sentence
                                     and sentence_i + 1 in text.paragraph_idxs)
                code = cm.code("text-word", text=text.textid, word=number)
                paragraph.append((code, display_word))
                if last_in_paragraph:
                    paragraphs.append(paragraph)
                    paragraph = []
    if paragraph:
        paragraphs.append(paragraph)
    text_dict[text.textid] = paragraphs
    title_dict[text.textid] = text.title
