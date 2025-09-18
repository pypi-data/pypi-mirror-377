from .lang_list import NO_SPACE, special_characters, special_languages, ANCIENT_CIVILIZATION_NO_SPACE
import re

def count_sentence(sentence:str,
                   lang_code:str):
    """
    Count the number of words/characters in a sentence.

    Args:
        sentence: The sentence to count.
        lang_code: ISO15924 language code.

    Returns:
        The number of words/characters in the sentence.
    """

    if len(lang_code) != 4:
        raise ValueError("language code not valid")

    for special_character in special_characters:
        special_chara_length = len(re.findall(special_character, sentence, flags=re.I))
        sentence = re.sub(special_character, "", sentence)

    if lang_code in NO_SPACE or lang_code in ANCIENT_CIVILIZATION_NO_SPACE:
        sentence_length = len(sentence)
    elif lang_code in special_languages:
        sentence_length = sentence.count(special_languages[lang_code]) + 1
    else:
        sentence_length = sentence.count(" ") + 1

    return sentence_length + special_chara_length