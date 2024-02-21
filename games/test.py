import json
import Levenshtein
from tqdm import tqdm

# Charger la liste de mots anglais depuis un fichier texte
with open("static/words_alpha.txt", "r") as f:
    english_words = [word.strip() for word in f]

# Dictionnaire pour stocker les mots et leurs mots similaires
similar_words_dict = {}

# Fonction pour calculer la distance de Levenshtein entre deux mots
def levenshtein_distance(word1, word2):
    return Levenshtein.distance(word1, word2)

# Fonction pour trouver les 5 mots les plus similaires pour un mot donné
def find_similar_words(word, word_list):
    similar_words = sorted(word_list, key=lambda x: levenshtein_distance(word, x))[:5]
    return similar_words

# Parcourir tous les mots anglais et trouver les 5 mots similaires pour chacun
with tqdm(total=len(english_words), desc="Processing") as pbar:
    for word in english_words:
        similar_words_dict[word] = find_similar_words(word, english_words)
        pbar.update(1)

# Écrire le résultat dans un fichier JSON
with open("similar_words_levenshtein.json", "w") as f:
    json.dump(similar_words_dict, f, indent=4)

print("Fichier JSON créé avec succès!")
