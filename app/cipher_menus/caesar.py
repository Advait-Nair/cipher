import matplotlib
from utils.bindutils import *
from nicegui import ui
from time import sleep
from utils.words import *
from app.ciphers.caesar import offset_alphabet_by_n, caesar_cipher, alphabet_hold

def ConductCaesarCipher():
    current_offset = Hold()
    ciphertext = Hold('')
    rotation_map = Hold(offset_alphabet_by_n(current_offset.value, alphabet_map=alphabet_hold.value))
    plaintext = Hold('')
    pcalc = Hold(100*percentage_words(is_word(plaintext.value.split(' '))))
    

    def run(n):
        plaintext.set(caesar_cipher(offset=current_offset.value, ciphertext=ciphertext.value, alphabet_map=alphabet_hold.value))
        rotation_map.set(offset_alphabet_by_n(current_offset.value, alphabet_map=alphabet_hold.value))
        pcalc.set(100*percentage_words(is_word(plaintext.value.split(' ')), dp=3))
    
    with ui.element('div').classes('w-full grid grid-cols-2 gap-4 max-md:grid-cols-1'):
        ui.textarea('Ciphertext', on_change=run).classes('w-full').bind_value(ciphertext)
        ui.textarea('Decoded plaintext').classes('w-full').bind_value_from(plaintext)
        

    with ui.row():


        def onadd(n):
            if current_offset.value >= len(alphabet_hold.value)-1:
                current_offset.set(0)
            else: current_offset.incr(1)
            run(n)
        
        def onsub(n):
            if current_offset.value == 0: current_offset.set(len(alphabet_hold.value)-1)
            else: current_offset.decr(1)
            run(n)

        def cycle_all(n):
            largest_pw = 0
            largest_pw_i = 0
            for i in range(0, len(alphabet_hold.value)):
                ptext = caesar_cipher(i, ciphertext=ciphertext.value, alphabet_map=alphabet_hold.value)
                pw = percentage_words(is_word(ptext.split(' ')))
                if largest_pw < pw:
                    largest_pw = pw
                    largest_pw_i = i
            current_offset.set(largest_pw_i)
            run(n)
        
        ui.button('Run All Cycles', on_click=cycle_all)
        ui.button(icon='add', color='bg-gray-800', on_click=onadd)
        ui.button(icon='remove', color='bg-gray-800', on_click=onsub)
    
    with ui.row():
        ui.button('Remove whitespaces', color='bg-gray-700', on_click=lambda _: ciphertext.set((ciphertext.value or '').replace(' ','')))

    with ui.element('div').classes('flex items-start gap-3'):
        ui.slider(min=0, max=len(alphabet_hold.value)-1, on_change=run).bind_value(current_offset, current_offset.t())
        ui.label('Current scroll offset:')
        ui.label().bind_text(current_offset, current_offset.t())
    with ui.row():
        ui.label('Current alphabet rotation map:')
        ui.label(offset_alphabet_by_n(current_offset.value, alphabet_map=alphabet_hold.value)).bind_text(rotation_map, rotation_map.t())

    with ui.row().classes('w-full'):
        ui.input('Alphabet Map', on_change=run).classes('w-full').bind_value(alphabet_hold, alphabet_hold.t())
    
    with ui.row():
        ui.label('Percentage of recognised words:')
        ui.label().bind_text(pcalc, pcalc.t())
        ui.label('%')