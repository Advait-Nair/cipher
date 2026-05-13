from utils.words import ALPHABET
from utils.bindutils import *
from utils.expose import *
from copy import deepcopy
from app.ciphers.frequency_analysis import frequency_analysis
from app.ciphers.substitution import substitution_cipher
from nicegui import ui
from utils.words import *

multiplier_hold = Hold(3)
shift_hold = Hold(5)
@expose_args({
    'multiplier': multiplier_hold,
    'shift': shift_hold
})

def affine_cipher(ciphertext:str, multiplier:int=1, shift:int=0, ui_row=None):
    # f_analysis = frequency_analysis(ciphertext)

    substitution_map = ''
    # multiplier (index) + shift => new index
    for i, char in enumerate(ALPHABET):
        substitution_map += ALPHABET[int((multiplier*i + shift) % len(ALPHABET))]

    if ui_row:
        with ui_row:
            ui.label(substitution_map)

    return substitution_cipher(
        ciphertext=ciphertext,
        substitution_map=substitution_map
    )



max_magnitude = Hold(50)
goes_negative = Hold(False)
def brute_force_affine(ciphertext_hold:Hold, plaintext_hold:Hold, util_space:ui.row, function_holds:dict) -> None:
    def work():
        # plaintext_pword_values = []
        highest_recorded_value = {
            'plaintext': plaintext_hold.value,
            'percentage': 0,
            's': 0,
            'm': 0

        }
        for m in range((-max_magnitude.value) if goes_negative.value else 0, max_magnitude.value):
            for s in range((-max_magnitude.value) if goes_negative.value else 0, max_magnitude.value):
                decoded = affine_cipher(ciphertext=ciphertext_hold.value, multiplier=m, shift=s)

                percent = 100*percentage_words(is_word(decoded.split(' ')))

                if percent > highest_recorded_value.get('percentage'):
                    highest_recorded_value['plaintext'] = decoded
                    highest_recorded_value['percentage'] = percent
                    highest_recorded_value['m'] = m
                    highest_recorded_value['s'] = s


        multiplier_hold.set(highest_recorded_value.get('m'))
        shift_hold.set(highest_recorded_value.get('s'))
        plaintext_hold.set(
            highest_recorded_value.get('plaintext')
        )
    
        with util_space.classes('flex items-center justify-start w-full'):
            ui.number(label='Max Magnitude', on_change=work).bind_value(max_magnitude, max_magnitude.t())
            ui.checkbox(text='Goes negative', on_change=work).bind_value(goes_negative, goes_negative.t())

    work()