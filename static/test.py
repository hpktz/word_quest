# import ijson
# import time
# import time

# def find_word_in_json(file_path, word):
#     with open(file_path, "r") as f:
#         parser = ijson.parse(f)
#         for prefix, event, value in parser:
#             if prefix == word:
#                 print(prefix, event, value)
#                 return value

# file_path = 'static/similar_words_levenshtein.json'
# word_to_find = 'dance'
# start = time.time()
# result = find_word_in_json(file_path, word_to_find)
# end = time.time()
# print("Temps d'exécution:", end-start, "secondes.")
# if result:
#     print(f"Le mot '{word_to_find}' se trouve dans la clé '{result}'.")
# else:
#     print(f"Le mot '{word_to_find}' n'a pas été trouvé dans le fichier.")

import time
import linecache

def find_word_in_txt(file_path, word):
    min = 0
    max = 336532
    while min < max:
        mid = (min + max) // 2
        line = linecache.getline(file_path, mid).split(":")
        print(line[0])
        if str(line[0]) == word:
            return line[1]
        elif str(line[0]) < word:
            min = mid + 1
        else:
            max = mid
    return None

file_path = 'static/similar_words_levenshtein.txt'
word_to_find = 'armchair'
start = time.time()
result = find_word_in_txt(file_path, word_to_find)
end = time.time()
print("Temps d'exécution:", end-start, "secondes.")
if result:
    print(f"Le mot '{word_to_find}' se trouve dans la clé '{result}'.")
else:
    print(f"Le mot '{word_to_find}' n'a pas été trouvé dans le fichier.")

