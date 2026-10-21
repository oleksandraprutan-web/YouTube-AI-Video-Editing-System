"""Word normalisation shared by the assembler and QA: contractions, numbers, punctuation."""
import re

CONTR = {"don't": "do not", "doesn't": "does not", "didn't": "did not", "isn't": "is not", "aren't": "are not",
         "wasn't": "was not", "can't": "can not", "cannot": "can not", "won't": "will not", "wouldn't": "would not",
         "it's": "it is", "that's": "that is", "there's": "there is", "here's": "here is", "what's": "what is",
         "let's": "let us", "he's": "he is", "she's": "she is", "i'm": "i am", "you're": "you are", "we're": "we are",
         "they're": "they are", "i'll": "i will", "you'll": "you will", "we'll": "we will", "it'll": "it will",
         "i've": "i have", "you've": "you have", "we've": "we have", "i'd": "i would", "everything's": "everything is",
         "one's": "one is", "link's": "link is", "gonna": "going to", "wanna": "want to"}
NUMS = {"zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7",
        "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
        "fifteen": "15", "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50", "hundred": "100", "thousand": "000"}
DROP = {"dollars", "dollar"}


def norm(w):
    w = w.lower().replace("’", "'").replace("%", " percent").replace("-", " ")
    w = re.sub(r"[^a-z0-9' ]", " ", w)
    out = []
    for t in w.split():
        t = t.strip("'")
        if not t:
            continue
        for u in CONTR.get(t, t).split():
            u = NUMS.get(u, u)
            if u not in DROP:
                out.append(u)
    return out
