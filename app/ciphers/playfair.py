from utils.words import ALPHABET, wash, work_out_unwhitespaced_words_percent, word_dict
from utils.bindutils import *
from utils.expose import *
from utils.generic import *
from copy import deepcopy
from nicegui import ui
from app.ciphers.caesar import *
from app.ciphers.frequency_analysis import *
import time
import itertools

join_targets = 'IJ'
JOIN_IDENTIFIER = 'I' # ! must be a single character, of length 1 !

# allow the matrix cell r,c locator to attribute join values to the correct letters
def work_alias_dict():
    a_dict = {}
    for target in join_targets:
        a_dict[target] = JOIN_IDENTIFIER
    return a_dict

alias_dict = work_alias_dict()

def build_playfair_matrix(key:str, r=5,c=5):
    global kw_map
    global target_join_dealt

    matrix = build_matrix(r=r,c=c, filler='_')
    
    # Build keyword map
    kw_map = ''
    target_join_dealt = False


    def deal_join(char:str):
        global kw_map
        global target_join_dealt

        if char in join_targets and not target_join_dealt:
            kw_map += JOIN_IDENTIFIER
            target_join_dealt = True
            return True
        elif char in join_targets: return True
        return False

    for letter in key.upper():
        if deal_join(letter): continue
        if not letter in kw_map:
            kw_map += letter
        
    for char in ALPHABET:
        if deal_join(char): continue
        if not char in kw_map:
            kw_map += char
    
    # print(kw_map)


    # Build the grid
    index = 0
    for r,c in MatrixRowIterator(matrix=matrix).iter():
        matrix[r][c] = kw_map[index]
        index += 1
    
    # print_matrix(matrix)
    return matrix

print_matrix(
    build_playfair_matrix(
        'drink'
    )
)

@expose_args({
    'key': Hold('monarchy'),
    'col_to_right_mode': Hold(False)
})
def playfair_cipher(ciphertext:str, key:str,col_to_right_mode:bool, ui_row=None) -> str:


    matrix = build_playfair_matrix(key=key)
    
    ciphertext = wash(ciphertext)

    plaintext = ''
    for i in range(0, len(ciphertext)-1, 2):
        char_1 = ciphertext[i]
        char_2 = ciphertext[i+1]
        char_1_loc = get_matrix_loc(matrix, char_1, aliases=alias_dict)
        char_2_loc = get_matrix_loc(matrix, char_2, aliases=alias_dict)

        if not char_1_loc or not char_2_loc: print('KEY FOR THIS INCIDENT: ', key, len(key))

        # ? Both instances use % to loop back up to the next value if they reach negatives, e.g. if no left letter, take the rightmost
        if char_1_loc[0] == char_2_loc[0]:
            # print(char_1, char_2, 'has triggered the same-column logic')
            # ? If they have the same row value, i.e. are in the same column
            # ?                  Keep rows same  Get the column above (+y down, so -y up)

            if not col_to_right_mode:
                decoded_char_1_loc = (char_1_loc[0], (char_1_loc[1]-1) % 5)
                decoded_char_2_loc = (char_2_loc[0], (char_2_loc[1]-1) % 5)

            # ! RIGHT COL MODE!
            if col_to_right_mode:
                decoded_char_1_loc = ((char_1_loc[0]+1) % 5, char_1_loc[1])
                decoded_char_2_loc = ((char_2_loc[0]+1) % 5, char_2_loc[1])

        elif char_1_loc[1] == char_2_loc[1]:
            # print(char_1, char_2, 'has triggered the same-row logic')
            # ? If they have the same column value, i.e. are in the same row
            # ?         Get row to the left, -x  Keep the cols same

            if not col_to_right_mode:
                decoded_char_1_loc = ((char_1_loc[0]-1) % 5, char_1_loc[1])
                decoded_char_2_loc = ((char_2_loc[0]-1) % 5, char_2_loc[1])

            # ! RIGHT COL MODE!
            if col_to_right_mode:
                # ? col above
                decoded_char_1_loc = ((char_1_loc[0]+1) % 5, char_1_loc[1])
                decoded_char_2_loc = ((char_2_loc[0]+1) % 5, char_2_loc[1])
                # decoded_char_1_loc = (char_1_loc[0], (char_1_loc[1]+1) % 5)
                # decoded_char_2_loc = (char_2_loc[0], (char_2_loc[1]+1) % 5)


        else:
            # ? If they are on different rows and columns, i.e. row1 ≠ row2 and col1 ≠ col2
            # ?                  Swap rows       Keep the cols same
            decoded_char_1_loc = (char_2_loc[0], char_1_loc[1])
            decoded_char_2_loc = (char_1_loc[0], char_2_loc[1])

        getter = matrix_get(matrix)

        decoded_char_1 = getter(decoded_char_1_loc)
        decoded_char_2 = getter(decoded_char_2_loc)

        plaintext += decoded_char_1 + decoded_char_2

        # print_matrix(
        #     matrix,
        #     highlight_targets=[char_1_loc, char_2_loc, decoded_char_1_loc, decoded_char_2_loc]
        # )
        # print(f'{char_1} -> {decoded_char_1}\n{char_2} -> {decoded_char_2}')



    return plaintext

@expose_args({
    'key_bank_file_name': Hold('acc21'),
    'look_for': Hold(''),
    'keyword_threshold': Hold(3),
    'ioc_mode': Hold(True),
    'cols_to_right_mode': Hold(False)
})
def playfair_brute_force(ciphertext:str, key_bank_file_name:str, cols_to_right_mode:bool, keyword_threshold:int, ioc_mode:bool, look_for:str, ui_row:ui.row=None):

    look_for = [x.strip() for x in wash(look_for.replace(',', ' '), wsp=True).split(' ')]
    ciphertext = wash(ciphertext)
    if not ciphertext:
        return ''
    text = getfile(key_bank_file_name)
    keys = []
    if not text:
        with ui_row:
            ui.notify(f'File "{key_bank_file_name}" does not exist!')
    else:
        text = text.replace(',',' ').replace('\n',' ').replace('.',' ')
        keys = wash(text, wsp=True).split(' ')
        
        # Clean out small words below 3 characters that likely won't be used as keywords, like the, as, a, etc.
        for index, key in enumerate(keys):
            if len(key) < keyword_threshold:
                keys.pop(index)

        # remove repeated words
        keys = list(set(keys))

        print(keys)
        
        



    results:dict = {}
    for key in keys:
        results[key] = playfair_cipher(ciphertext, key=key, col_to_right_mode=cols_to_right_mode)
    
    res_list = list(results.items())
    if ioc_mode:
        ioc_sort = order_dict_by_ioc(results)
        with ui_row.style('display:flex; flex-direction:column; align-items: flex-start; justify-content: flex-start'):
            ui_row.clear()
            best_ioc = get_n_item(ioc_sort, 0)
            second_best_ioc = get_n_item(ioc_sort, 1)

            ui.label(f'Best IoC: {best_ioc[0]} [displayed in main plaintext window]')
            ui.label(f'Second-best IoC: {second_best_ioc[0]} [first ~120 characters displayed below]:')
            ui.label(second_best_ioc[1][:120]+'...')
            return best_ioc[1]
    else:
        selected = ''
        for k,v in results.items():
            for token in look_for:
                if token in v:
                    selected = v
                    with ui_row.style('display:flex; flex-direction:column; align-items: flex-start; justify-content: flex-start'):
                        ui.label(f'{k} -> {v[:70]}')

        if len(res_list) == 0:
            with ui_row:
                ui.label('No Results!')
            return ''
        
        return selected or ''
        
