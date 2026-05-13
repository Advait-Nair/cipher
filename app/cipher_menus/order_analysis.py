from utils.words import *
from utils.bindutils import *
from nicegui import ui

alphabet_hold = Hold(ALPHABET)

def order_analysis(ciphertext:str) -> str:
    most_common_single_char_mappings = {}

    for word in ciphertext.upper().split(' '):
        fmapped = order_map_word(word)
        extrapolated_words = get_words_from_omap(omap_to_get=fmapped)

        for possible_word in extrapolated_words:

            # Here, we will take each word and take the original word, and ciphered word and build
            # a partial translation table. Once the translation tables are complete, the most common conversion
            # entries are assumed to decode the final plaintext.

            possible_map = {}
            for cindex, char in enumerate(possible_word.upper()):
                possible_map[char] = word[cindex]
                mapping_id = f"{char}:{word[cindex]}"
                previously_mapped = most_common_single_char_mappings.get(mapping_id, False)

                if previously_mapped:
                    most_common_single_char_mappings[mapping_id] += 1
                else:
                    most_common_single_char_mappings[mapping_id] = 1
            
    
    chosen_mapping = {}
    for mapping, count in most_common_single_char_mappings.items():
        cipherchar, pchar = mapping.split(':')

        if chosen_mapping.get(cipherchar, {'count':0})['count'] > count: continue

        chosen_mapping[cipherchar] = {
            'plaintext': pchar,
            'count': count
        }


    deciphered_buffer = ''
    for char in ciphertext.upper():
        deciphered_buffer += chosen_mapping[char]['plaintext'] if char in chosen_mapping else char




    return deciphered_buffer




def OrderAnalysis():
    ciphertext = Hold('')
    plaintext = Hold('')
    pcalc = Hold(100*percentage_words(is_word(plaintext.value.split(' '))))
    

    def run(n):
        # SET ciphertext AND SUBMAP HERE
        print('running')
        plaintext.set(order_analysis(ciphertext=ciphertext.value))
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