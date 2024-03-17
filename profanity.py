import re
import Levenshtein
import logging

def profanity_detector(text):
    """
    Detects the presence of profanity in a text.

    Args:
        text (str): The text to analyze.

    Returns:
        bool: True if the text contains profanity, False otherwise.
    """

    try:
        # Load the profanity file
        with open("static/censored_words.txt", "r") as f:
            profanity_words = f.read().splitlines()

        # Convert the text to lowercase and remove accents
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)

        # Search for profanity in the text
        for word in profanity_words:
            if re.search(r"\b"+word+r"\b", text):
                return True

        profanity_coef = []
        for word in text.split(" "):
            if len(word) > 4:
                for profanity_word in profanity_words:
                    profanity_coef.append([profanity_word, Levenshtein.ratio(profanity_word, word)])
        
        profanity_coef = sorted(profanity_coef, key=lambda x: x[1], reverse=True)
        if profanity_coef:
            return True if profanity_coef[0][1] > 0.7 else False
        else:
            return False
    except Exception as e:
        logging.error(f"An error occurred while detecting profanity: {e}")
        return False