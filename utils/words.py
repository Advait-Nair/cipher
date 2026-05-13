import os
import sys
import json
import math
import enum
import inspect
import re
from utils.nice_object import NiceObject

WORD_SOURCE = os.path.expanduser('words_dictionary.json')
# WORD_SOURCE = os.path.expanduser('~/english_words.txt')
WORD_OMAP_SOURCE = os.path.expanduser('womap_dictionary.json')
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# NUM_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
# ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
LETTER_FREQUENCY_ORDER = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'
PLACEHOLDER_CHAR = 'Z'
IOC_ENG = 0.0667


class Matches(enum.Enum):
    NONE = 'red'
    PARTIALLY = 'yellow'
    COMPLETELY = 'green'


should_recompile_map = '-r' in sys.argv



# Get Word Source
if not os.path.exists(WORD_SOURCE):
    raise Exception('fatal: no word source')
with open(WORD_SOURCE, 'r') as f: word_dict:dict = json.loads(f.read())


# Compile Order Map And Auto-compilation

def base10_to_36(b10:int) -> str:
    if b10 > 36: return 'z'
    return ('0123456789'+ALPHABET)[abs(b10)]


def order_map_word(word:str):
    order_map = ""
    encounter_map = {}
    encounter_index = 0


    for char in word.upper():
        if not char in encounter_map:
            order_map += base10_to_36(encounter_index)
            encounter_map[char] = base10_to_36(encounter_index)
            encounter_index += 1
        else:
            order_map += encounter_map[char]
    
    return order_map


def compile_order_map_dictionary():
    compiled_dict = word_dict
    for word in compiled_dict:
        compiled_dict[word] = order_map_word(word=word)

    with open(WORD_OMAP_SOURCE, 'w') as f:
        f.write(
            json.dumps(compiled_dict)
        )


def wash(text:str, wsp=False) -> str:
    """
    This function will take input text and only return characters that are in the `ALPHABET` set.
    - Only `ALPHABET` members returned
    - Does NOT return whitespaces or any form of punctuation when `wsp=False`
    - Set `wsp=True` to allow whitespaces to filter through.

    ```python
    wash('Hello there, human!')
    >> 'HELLOTHEREHUMAN'


    wash('Hello there, human!', wsp=True)
    >> 'HELLO THERE HUMAN'

    ```

    """
    cut = text.strip().upper()
    return ''.join((x if x in ALPHABET+(' ' if wsp else '') else '') for x in cut)

if not os.path.exists(WORD_OMAP_SOURCE):
    compile_order_map_dictionary()


with open(WORD_OMAP_SOURCE, 'r') as f: word_omap:dict = json.loads(f.read())


def word_only(w:str):
    wb = ''
    for char in w.lower():
        if char in 'abcdefghijklmnopqrstuvwxyz1234567890\'': # apostrophe too
            wb += char
    return wb

def n_in_f(n:list[str], file:str) -> list[bool]:
    with open(file, 'r') as f:
        o = []
        for test in n:
            o.append(1 == word_dict.get(word_only(test), 0))
        return o

def is_word(words:str|list[str]) -> list[bool]:
    return n_in_f(words if type(words) == list else [words], WORD_SOURCE)

# def work_out_unwhitespaced_paragraphs(text: str) -> str:
    BLOCK_SIZE = 5
    SCOPE_EXPANSION_STEP = 20
    # Methodology: Work through text in blocks of BLOCK_SIZE.
    blocks = []
    for b in range(0, math.floor(len(text)/BLOCK_SIZE)):
        blocks.append(text[b*BLOCK_SIZE:b*BLOCK_SIZE+BLOCK_SIZE])
    

    global current_scope_expansion
    global possible_channels
    possible_channels = []
    current_scope_expansion = 0

    def work_possible_channels(selected_channel:int=0, lblocks:list[str]=blocks, scope=BLOCK_SIZE):
        global current_scope_expansion
        global possible_channels
        word_found = False
        
        if scope > BLOCK_SIZE:
            lb_buffer = []
            collection_buffer = ''
            for index, block in enumerate(lblocks):
                if len(collection_buffer) < scope:
                    collection_buffer += block
                else:
                    lb_buffer.append(collection_buffer)
                    collection_buffer = ''
            lblocks = lb_buffer
        
        # The code above just got the lblocks up to the scope step.
            
        for index, block in enumerate(lblocks):
            # Check block if contains a word
            for word in word_dict:
                if len(word) > scope: continue # Don't check words with length greater than scope
                if word in block:
                    print(word, block)
                    word_found = True
                    t = possible_channels[selected_channel]
                    if type(t) == list: t.append(word)
                    else: t = [word]

                    # We take the remaining characters in the channel, and continue this
                    if len(word) < BLOCK_SIZE:
                        lblocks[index] = lblocks[index][len(word):]
                        work_possible_channels(selected_channel=selected_channel, lblocks=lblocks) # Work in the same channel
                
            if not word_found:
                # We did not find a word; so, we call this with a higher scope
                current_scope_expansion += 1
                work_possible_channels(selected_channel=selected_channel, lblocks=lblocks, scope=BLOCK_SIZE+(SCOPE_EXPANSION_STEP*current_scope_expansion))

                
    work_possible_channels()
    print(possible_channels)

    return text + '\n\nunwsp!'


class WordPercentFinding(NiceObject):
    percent:int
    count:int
    ignored_count:int
    flagged_words:list[str]
    words_in_dict:int
    used_word_size:int

def no_occurences_in_word(target:str, text:str) -> int:
    # returns n occurences of target in text
    return len(re.findall(target.strip().upper(),wash(text)))


def work_out_unwhitespaced_words_percent(text: str, negation_threshold=3) -> WordPercentFinding:
    count = 0
    occurences = 0
    negated_count = 0 # words that are too short and cause high coincidence
    flagged_words = []
    for word in word_dict:
        if len(word) < negation_threshold:
            negated_count += 1
            continue
        
        word_upper = word.upper()
        text_upper = text.upper()
        if word_upper in text_upper:
            occurences += no_occurences_in_word(word_upper, text_upper)
            count += 1
            flagged_words.append(word)

    return WordPercentFinding(percent=count/(len(word_dict)-negation_threshold), count=occurences, words_found=count, ignored_count=negated_count, flagged_words=flagged_words,words_in_dict=len(word_dict),used_word_size=len(word_dict)-negated_count)
        


def percentage_words(matchlist: list[bool], dp=-1) -> float:
    if len(matchlist) == 0: return 0.0
    r = matchlist.count(True) / len(matchlist)
    if dp <= 0:
        return r
    return round(r, dp)



def work_ioc(text:str):

    iocs = []

    n = len(wash(text))
    if n == 0: return 0 # prevent ZeroDivisionError

    denominator = ( n*(n-1) )
    # print(denominator)
    for letter in ALPHABET:
        N = no_occurences_in_word(letter, text)
        iocs.append(
            ( N*(N-1) ) / denominator
        )
        # print(letter, N, iocs[-1])
    
    return sum(iocs)

def order_dict_by_ioc(dictionary):
    return {k:v for k,v in sorted(dictionary.items(), key=lambda item: work_ioc(item[1]))}


def get_omap_of_word(word:str):
    return word_omap.get(word, False)


def get_words_from_omap(omap_to_get:str):
    found_words = []
    for word, omap in word_omap.items():
        if omap == omap_to_get.strip():
            found_words.append(word)
    return found_words





if should_recompile_map: compile_order_map_dictionary()