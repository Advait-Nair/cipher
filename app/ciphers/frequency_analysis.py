from utils.expose import *
from utils.bindutils import *
from nicegui import ui
import matplotlib.pyplot as plot
import numpy as np
from utils.generic import digraph
from utils.words import *
from app.ciphers import Ciphers
from utils.ngui_elements import *


def frequency_analysis(sample:str, is_letter:bool=False) -> dict:
    ciphertext = wash(sample, wsp=True)
    frequency = {}
    arr = ciphertext.split(' ') if not is_letter else wash(ciphertext)
    for word in arr:
        if is_letter and word.strip() == '': continue
        if frequency.get(word):
            frequency[word] += 1
        else: frequency[word] = 1

    # Sort the frequency dict
    return dict(
        sorted(
            frequency.items(), key=lambda i: i[1], reverse=True
        )
    )

def plot_frequency_analysis(ciphertext_hold:Hold, plaintext_hold:Hold, util_space:ui.row, function_holds:dict) -> None:
    # global possible_substitution_map
    is_letter = Hold(True)
    is_digraph = Hold(False)

    with util_space:
        plotter = ui.row()
    def work():
        possible_substitution_map = {}
        plotter.clear()
        if not is_digraph.value:
            frequency = frequency_analysis(ciphertext_hold.value, is_letter.value)
            for i, letter in enumerate(frequency):
                possible_substitution_map[letter] = LETTER_FREQUENCY_ORDER[i]
            
            submap = ''
            for character in ALPHABET:
                submap += possible_substitution_map.get(character, character)
        else:
            print('digraph !',' '.join(digraph(wash(ciphertext_hold.value))))
            frequency = frequency_analysis(' '.join(digraph(wash(ciphertext_hold.value))))




        fkeys = list(frequency.keys())
        fvals = list(frequency.values())

        x = np.array((fkeys) [:24])
        y = np.array((fvals) [:24])
        
        with plotter:
            with ui.matplotlib(figsize=(15,4)).figure as fig:

                ax = fig.gca()
                
                ax.bar(x,y)
                ax.set_label('Frequency Analysis of Ciphertext')


        if possible_substitution_map:
            with plotter:
                ui.input(value=json.dumps(possible_substitution_map)).style('width: 100%;')
                ui.input(value=''.join(submap)).style('width: 100%;')

    
    with util_space:
        ui.separator()
        ui.checkbox('Is by letter').bind_value(is_letter).on_value_change(work)
        ui.checkbox('Is a digraph').bind_value(is_digraph).on_value_change(work)
        ui.separator()

    work()


def omap_finder(ciphertext_hold:Hold, plaintext_hold:Hold, util_space:ui.row, function_holds:dict) -> None:
    words_to_flag_csv = Hold('')
    # possible_match_show = Hold('')
    in_mode = Hold(False)
    cb_analysis = Hold(False)

    smap_hold:Hold = function_holds.get(Ciphers.Substitution).get('substitution_map')
    
    def work():
        smap_mapping = smap_hold.value # get substitution_map Hold
        deformatted = ciphertext_hold.value.replace(',','').replace('.','')
        flagged_words = [x.strip().upper() for x in words_to_flag_csv.value.split(',')]
        # highlighted_text = ''
        rv.clear()
        if ciphertext_hold.value.strip().__len__() == 0: return


        
        # match_pointed_buffer = ''
        if cb_analysis.value:
            with rv.classes('gap-0'):
                # ? Character-based order analysis
                unified = deformatted.replace(' ','')

                for flagged_word in flagged_words:
                    if len(flagged_word) < 2:
                        with rv:
                            with ui.row().classes('flex ml-2 items-center justify-center'):
                                ui.icon('warning').classes('text-red-400 text-lg')
                                ui.label(f'Flagged word {flagged_word} is less than 2 characters!').classes('text-red-300')
                        continue
                    return_pointer_trackers = []
                    for cindex in range(len(unified)):
                        # if cindex > len(unified) - len(flagged_word):
                            # match_pointed_buffer += unified[cindex:]
                            # print(return_pointer_trackers, len(unified))
                            # for c in unified[cindex:]:
                            #     ui.label(c)
                            #     if cindex in return_pointer_trackers:
                            #         ui.label('◄')
                            # break
                        if not cindex > len(unified) - len(flagged_word):
                            word_find = unified[cindex:cindex+len(flagged_word)]
                            if order_map_word(word_find) == order_map_word(flagged_word):
                                # ? local match
                                ui.label('►').classes('text-red-400')
                                # match_pointed_buffer += '►'
                                return_pointer_trackers.append(cindex + len(flagged_word))
                        
                        if cindex in return_pointer_trackers:
                            ui.label('◄').classes('text-red-400')
                            # match_pointed_buffer += '◄'
                        
                        # in_match = False
                        # for ptr in return_pointer_trackers:
                        #     if cindex+1 < ptr and ptr-len(flagged_word) > cindex+1:
                        #         ui.label(unified[cindex]).classes('text-red-400')
                        #         in_match = True
                        #         break
                        # if not in_match: ui.label(unified[cindex])
                        ui.label(unified[cindex])

                    if len(unified) in return_pointer_trackers:
                        ui.label('◄').classes('text-red-400')
                        # match_pointed_buffer += unified[cindex]
                
                # ui.label(match_pointed_buffer)

        else:
            for cipher_token in deformatted.split(' '):
                for flagged_word in flagged_words:
                    with rv:
                        omapped_flagged_word = order_map_word(flagged_word)
                        omapped_ctext = order_map_word(cipher_token)
                        if (omapped_ctext == omapped_flagged_word) if not in_mode.value else (omapped_flagged_word in omapped_ctext):

                            # ? We need to check if a word also matches to what's mapped on the dictionary
                            # ? We do not count items on the dictionary that map to themselves, like A:A

                            match_level = Matches.NONE
                            downgraded = False


                            # Loop through each character in the ciphered word
                            for cindex, cipherchar in enumerate(cipher_token):

                                # We convert the cipherchar to it decoded form; check if it doesnt match flagged_word[cindex
                                if smap_mapping.get(cipherchar, False).strip().upper() == cipherchar: continue # ignore if it maps to self
                                if not smap_mapping.get(cipherchar, False).strip().upper() == flagged_word[cindex]:
                                    # There is an unmatching word; downgrade a complete match to a partial one
                                    match_level = Matches.PARTIALLY if match_level == Matches.COMPLETELY else Matches.NONE
                                    downgraded = True
                                    continue
                                # If we haven't downgraded (found non-matching)
                                if not downgraded: match_level = Matches.COMPLETELY
                                else: 
                                    match_level = Matches.PARTIALLY # We've downgraded, so max is partial
                                    break # We know it's partial; so we break out. We can't do this for the other states.
                            
                            
                            

                            
                            
                            ui.label(f"{cipher_token} / {flagged_word}?").classes(f'text-{match_level.value}-400 font-bold')
                            continue

                        # highlighted_text += pmatches + ' '
                        ui.label(cipher_token)
            
            # possible_match_show.set(highlighted_text)
    smap_hold.bind_fn(work)


    

    with util_space.classes('w-full flex flex-col'):
        with ui.row().classes('w-full'):
            ui.input(label='Look for order analysis matches (CSV)', on_change=work).bind_value(words_to_flag_csv, words_to_flag_csv.t()).classes('w-full')
            ui.checkbox(text='Switch to lenient incomplete matching mode', on_change=work).bind_value(in_mode, in_mode.t())
            ui.checkbox(text='Switch to character-based analysis', on_change=work).bind_value(cb_analysis, cb_analysis.t())
            
        # ui.label().bind_text(possible_match_show, possible_match_show.t())
        with util_space.classes('w-full'):
            rv = ui.row().classes('flex gap-1 wrap') # Render the text in a nice highlight view

        # with ui.row():
        #     for find in individual_finds:
        #         with ui.row(): ui.label(find)

    work()

    return work