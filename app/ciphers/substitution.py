from utils.words import ALPHABET
from utils.bindutils import *
from utils.expose import *
from copy import deepcopy

@expose_args({
    'keysub_CSV': Hold(''),
    'tgt_kw': Hold(0),
    'substitution_map': Hold(dict(zip(
        list(ALPHABET),
        list(ALPHABET),
    ))),
})
def substitution_cipher(ciphertext:str, substitution_map:dict|str, keysub_CSV:str='', tgt_kw:int=0, ui_row=None):
    tgt_kw = int(tgt_kw or 0)
    keysub_CSV = keysub_CSV.strip().upper()
    tsfrd_submap = deepcopy(ALPHABET)
    if type(substitution_map) == dict:
        for mapping in substitution_map:
            if not mapping in tsfrd_submap: continue
            tsfrd_submap = tsfrd_submap.replace(mapping, substitution_map[mapping].upper())
            # tsfrd_submap[mapping] = substitution_map[mapping]
    
    new_substitution_map = substitution_map if type(substitution_map) == str else ''.join(list(substitution_map.values()))
    # new_substitution_map = substitution_map if type(substitution_map) == str else tsfrd_submap

    if len(keysub_CSV) > 0:
        kw = keysub_CSV.split(',')[tgt_kw].strip()
        tmp_kw = ''
        for char in kw:
            if char in tmp_kw: continue
            tmp_kw += char
        kw = tmp_kw
        rest_alphabet = ''
        for letter in ALPHABET:
            if not letter in kw:
                rest_alphabet += letter

        new_substitution_map = kw + rest_alphabet
        print(new_substitution_map)

    print(new_substitution_map)
    new_buffer = ''
    for char in ciphertext.upper():
        print(char)
        # new_buffer += substitution_map.get(char) if char in ALPHABET else char
        try: new_buffer += new_substitution_map[ALPHABET.find(char)] if char in ALPHABET else char
        except Exception as e: print(e)
        # new_buffer += ALPHABET[new_substitution_map.find(char)] if char in new_substitution_map else char
    return new_buffer
