from utils.bindutils import *
from nicegui import ui
from time import sleep
from utils.words import *
from app.ciphers.substitution import substitution_cipher
from utils.words import ALPHABET
alphabet_hold = Hold(ALPHABET)


def SubstitutionCipher():
    ciphertext = Hold('')
    plaintext = Hold('')
    pcalc = Hold(100*percentage_words(is_word(plaintext.value.split(' '))))
    

    def run(n):
        # SET ciphertext AND SUBMAP HERE
        plaintext.set(substitution_cipher(ciphertext=ciphertext.value, substitution_map=alphabet_hold.value))
        pcalc.set(100*percentage_words(is_word(plaintext.value.split(' ')), dp=3))
    
    with ui.element('div').classes('w-full grid grid-cols-2 gap-4 max-md:grid-cols-1'):
        ui.textarea('Ciphertext', on_change=run).classes('w-full').bind_value(ciphertext)
        ui.textarea('Decoded plaintext').classes('w-full').bind_value_from(plaintext)
        

    with ui.row():
        ui.button('Remove whitespaces', color='bg-gray-700', on_click=lambda _: ciphertext.set((ciphertext.value or '').replace(' ','')))



    with ui.row().classes('w-full'):
        ui.input('Alphabet Map', on_change=run).classes('w-full').bind_value(alphabet_hold, alphabet_hold.t())
        ui.label(ALPHABET)
    
    with ui.row():
        ui.label('Percentage of recognised words:')
        ui.label().bind_text(pcalc, pcalc.t())
        ui.label('%')