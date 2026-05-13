from utils.words import *
from utils.bindutils import *
from utils.expose import *
from copy import deepcopy
from nicegui import ui
import itertools

# def work_indices(depth:int, row_n: int):
#     indices_list = []
#     for i in range(2*depth -2):
#         indices_list.append( (depth - row_n - 2)*(2*i - 2) + row_n )
    
def all_possible_permutations(t_dim:int) -> list[tuple]:
    return list(itertools.permutations(range(t_dim)))

@expose_args({
    'transposition_dimension': Hold(5, {
        'range_min': 1,
        'range_max': 10
    }),
    'col_height_off_columns': Hold(5, {
        'range_min': 1,
        'range_max': 50
    }),
    'read_off_columns': Hold(False),
    'use_cols_for_blocks': Hold(False),
    'whitespace_separation': Hold(False),
    'conduct_auto_word_separation': Hold(False),
    'transposition_cycle': Hold(1),
    'stop_at': Hold(1000),
    'stop_at_word': Hold(''),
    'target_keyword': Hold(''),
})
def transposition_cipher(ciphertext:str, transposition_dimension:int, col_height_off_columns:int, stop_at:int, stop_at_word:str, use_cols_for_blocks:bool, read_off_columns:int, target_keyword:str, transposition_cycle:int, conduct_auto_word_separation:bool, whitespace_separation:bool, ui_row=None):
    # ? Transposition ciphers are grid-based ciphers that reorder columns based
    # ? on a re-ordering key. They can be applied multiple times to themselves.
    transposition_cycle = int(transposition_cycle or 5)
    stop_at = int(stop_at or 500)

    proc_ct = ''
    columns = []

    text = wash(ciphertext) # !p


    if use_cols_for_blocks:
        # use transposition dimension to rewrite text:
        # S E C R
        # E T S W
        # I T H U
        # We assume here the real text is read off by the columns after being transposed.
        # So we rewrite the text column-down.


        rows = [[] for _ in range(col_height_off_columns)]
        global row_ptr
        row_ptr = 0

        def ptr():
            global row_ptr
            row_ptr+=1
            if row_ptr >= col_height_off_columns: row_ptr = 0
        
        # for current_col in range(0, transposition_dimension):
        for index, char in enumerate(text):
            # if (index+1) % (current_col+1) != 0: continue
            rows[row_ptr].append(char)
            ptr() # move pointer onwards

            # 
            # new_text += char
        
        text = ''.join(''.join(row) for row in rows)
            

    
    for char in text:
        if char in ALPHABET:
            if len(columns) == 0:
                columns.append([char])
                continue

            if len(columns[-1]) < transposition_dimension:
                columns[-1].append(char)
            else:
                columns.append([char])
            
            proc_ct += char
    
    # pad any missing chars
    if len(columns) != 0:
        if len(columns[-1]) != transposition_dimension:
            columns[-1].extend(list(PLACEHOLDER_CHAR*(transposition_dimension - len(columns[-1]))))
    

    all_pos_perms = all_possible_permutations(transposition_dimension)

    
    if target_keyword.strip() != '':
        raw_keyword_map = [ALPHABET.find(x) for x in target_keyword.strip().upper()]
        sort = sorted(raw_keyword_map)
        
        kw_map = []
        for i, item in enumerate(raw_keyword_map):
            sorted_index = sort.index(item)
            kw_map.append(sorted_index)

        for i, cycle in enumerate(all_pos_perms):
            if len(kw_map) == 0: break
            # if list(cycle) == kw_map:
            #     transposition_cycle = i
            #     break

            found = False
            for j, x in enumerate(cycle):
                # print(j)
                if len(kw_map)-1 < j: break
                # print(cycle, x, kw_map[j])
                if x != kw_map[j]:
                    found = False
                    break
                found = True
            
            if not found: continue

            transposition_cycle = i
            break
        

    
    def work(whitespace_separation):
        print('d ',transposition_cycle)
        # Check if keyword exists


            
        # global columns
        transposed_columns = []
        for column in columns:
            tp_column = []
            for p in all_pos_perms[min(int(transposition_cycle),len(all_pos_perms)-1)]: # we use this transposition key for the specified cycle on all of them
                tp_column.append(column[p])
            transposed_columns.append(tp_column)
        
        if conduct_auto_word_separation:
            whitespace_separation = False

        if read_off_columns:
            # We read of the first index of all transposed columns, join them, and continue like so
            read_off_cols = ''
            for i in range(transposition_dimension):
                read_off_cols += ''.join(col[i] for col in transposed_columns)

            return read_off_cols
        
        return (' ' if whitespace_separation else '').join(''.join(x) for x in transposed_columns)
    
    if len(stop_at_word.strip()) > 0:
        print('ab to work it out ')
        # stop_at = transposition_cycle # !p
        transposition_cycle = 0
        for i in range(stop_at):
            print(i)
            transposition_cycle = i
            result = work(whitespace_separation=False)
            if stop_at_word.strip().upper() in result.upper():
                with ui_row:
                    ui.label('Best transposition cycle: ' + str(i+1))
                return work(whitespace_separation)



    # with ui_row:
    #     with ui.row():
    #         for col in transposed_columns:
    #             with ui.column():
    #                 for it in col:
    #                     with ui.list():
    #                         ui.label(it).classes('text-center')
    #                 ui.separator()
    # print(transposed_columns)
    # print(len(transposed_columns))
    
    


    # return work_out_unwhitespaced_words_percent(deciphered) if conduct_auto_word_separation else deciphered
    return work(whitespace_separation)

    # with ui_row: ui.label(proc_ct)