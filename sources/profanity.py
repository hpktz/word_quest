"""
This module contains the profanity detector function.

The profanity detector function is used to detect the presence of profanity in a text.

Imports: 
    - re: For handling regular expressions
    - Levenshtein: For handling the Levenshtein distance
    - logging: For logging errors
    
Functions:
    - profanity_detector: Detects the presence of profanity in a text
"""
import re
import Levenshtein
import logging
from root import *


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
        with open(str(os.getenv("DIRECTORY_PATH")) + "static/censored_words.txt", "r") as f:
            profanity_words = f.read().splitlines()

        # Convert the text to lowercase and remove accents
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)

        # Search for profanity in the text
        for word in profanity_words:
            if re.search(r"\b"+word+r"\b", text):
                return True

        # If no profanity is found, compare the words with the profanity words
        profanity_coef = []
        for word in text.split(" "): # For each word in the text
            if len(word) > 6:
                for profanity_word in profanity_words: # For each profanity word
                    # Calculate the Levenshtein distance between the word and the profanity word
                    profanity_coef.append([profanity_word, Levenshtein.ratio(profanity_word, word)])
        
        # Sort the profanity words by the Levenshtein distance
        profanity_coef = sorted(profanity_coef, key=lambda x: x[1], reverse=True)
        if profanity_coef:
            # If the Levenshtein distance is greater than 0.7, the word is considered as profanity
            return True if profanity_coef[0][1] > 0.85 else False
        else:
            return False
    except Exception as e:
        logging.error(f"An error occurred while detecting profanity: {e}")
        return False