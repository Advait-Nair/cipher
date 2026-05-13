import matplotlib
from utils.bindutils import *
from nicegui import ui
from time import sleep
from utils.words import *
from utils.expose import *
from utils.generic import *
alphabet_hold = Hold(ALPHABET)


def offset_alphabet_by_n(offset: int, alphabet_map=ALPHABET) -> str:

    # Based on the offset, rotate alphabet
    # alphabet_reversed = alphabet[::-1]
    return alphabet_map[len(alphabet_hold.value)-offset:] + alphabet_map[0:len(alphabet_hold.value)-offset]

def work_alphabet_offset(ctext_letter: int, ptext_letter, charset:str=ALPHABET) -> int:
    ctext_letter = wash(ctext_letter)
    ptext_letter = wash(ptext_letter)


    ctext_i = charset.find(ctext_letter)
    ptext_i = charset.find(ptext_letter)
    return max(0, abs(ctext_i - ptext_i))


@expose_args({
    'offset': Hold(0, {
        'range_min': 0,
        'range_max': 25
    }),
})
def caesar_cipher(offset: int, ciphertext:str, alphabet_map=ALPHABET, ui_row=None) -> str:
    # Based on the offset, rotate alphabet
    offset_alphabet = offset_alphabet_by_n(offset, alphabet_map=alphabet_map)

    # Map the ciphertext to plaintext
    plaintext = ''
    for char in ciphertext:
        target_map_index = alphabet_map.find(char.upper())
        if target_map_index == -1:
            plaintext += char # What it it is a symbol, like ?
            continue
        plaintext += offset_alphabet[target_map_index]
    
    return plaintext