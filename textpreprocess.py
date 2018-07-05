import re

def cleanText(text):
    text = re.sub("[^a-zA-Z]"," ",text)
    text = re.sub("/\r?\n|\r/"," ",text).lower()
    return text
