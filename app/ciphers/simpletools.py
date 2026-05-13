from utils.bindutils import Hold
from utils.words import *
from nicegui import ui
from utils.generic import past_significance_threshold, sig_test_type, get_closest

# An example of what a tool might look like
def whitespace_remover(ciphertext_hold:Hold, plaintext_hold:Hold, util_space:ui.row, function_holds:dict):
    ciphertext_hold.set((ciphertext_hold.value or '').replace(' ',''))

# An example of what a tool might look like
def length_worker(ciphertext_hold:Hold, plaintext_hold:Hold, util_space:ui.row, function_holds:dict):
    text = ciphertext_hold.value
    with util_space:
        with ui.row():
            ui.label('Raw Length')
            ui.label(len(text))
        with ui.row():
            ui.label('Whitespace-excluded length')
            ui.label(len(text.replace(' ','')))


negation_threshold_hold = Hold(6)
def work_unwhitespaced_words_percentage(ciphertext_hold:Hold, plaintext_hold:Hold, util_space:ui.row, function_holds:dict):
    text = plaintext_hold.value


    with util_space:
        with ui.row():
            subspace = ui.row()
        ui.separator()

    def work():
        subspace.clear()
        findings = work_out_unwhitespaced_words_percent(text=text, negation_threshold=negation_threshold_hold.value)

        with subspace:
            findings.percent *= 100
            findings.rename('percent','Percentage of found words relative to dictionary')
            findings.rename('count','Found words occurence total')
            findings.rename('used_word_size','Words used in dictionary to match')
            findings.rename('words_in_dict','Total size of downloaded dictionary')
            findings.rename('ignored_count','Words under negation threshold')
            as_a_table = findings.as_table(key_header='Data Label',value_header='Finding')
            
            # ui.table(rows=as_a_table, columns={})
            for row in as_a_table:
                if row['Data Label'] == 'Flagged Words': continue
                with ui.column().style('display: flex; align-items: flex-start; justify-content: center'):
                    ui.label(row['Data Label']).style('opacity: 0.6')
                    ui.label(row['Finding'])
            
            ui.separator().style('width: 100%')
            with ui.row().style('display: flex; align-items: flex-start; justify-content: center'):
                ui.label('Flagged Words').style('opacity: 0.6')
                ui.label(', '.join(findings.flagged_words))


            # with ui.row():
            #     ui.label('Detected words')
            #     ui.label(', '.join(findings.flagged_words))

    with util_space:
        with ui.row():
            with ui.column():
                ui.label('Negation Threshold')
            with ui.column().style('width: 5rem'):
                ui.slider(min=0, max=10).bind_value(negation_threshold_hold, negation_threshold_hold.t()).on_value_change(work)
            with ui.column():
                ui.label('Awaiting negation_threshold').bind_text(negation_threshold_hold, negation_threshold_hold.t())
    
    work()

SIG_1 = 40
SIG_2 = 40.8
PO_SCALE = 100
def ioc_eng_match_threshold(text_ioc:float) -> bool:
    return past_significance_threshold(
        lam=math.ceil(IOC_ENG*PO_SCALE),
        test=math.ceil(text_ioc*PO_SCALE),
        significance=SIG_1/100,
        significance_2=SIG_2/100,
        testing=sig_test_type.BOTH
    )



def get_ioc(ciphertext_hold:Hold, plaintext_hold:Hold, util_space:ui.row, function_holds:dict):
    text = wash(ciphertext_hold.value)

    # IOC of the whole text
    text_ioc = work_ioc(text)
    with util_space:
        doesnt_match_english = ioc_eng_match_threshold(text_ioc)
        ui.label('Generic IOC: ' + str(text_ioc)).style(f'color: {'#f55' if doesnt_match_english else '#5f5'}')
        ui.label('The Index of Coincidence measures the possibility of two random letters in a text being the same. In English, some letter combinations are more likely than others. By working out the similarity of a text\'s IOC to English, we can work out the nature of a cipher, and possible polyalphabetic keyword lengths. Polyalphabetic ciphers shift columns and manipulate plaintext in such a manner that the IOC is disrupted.')

        if text_ioc == 0:
            ui.label('Text IOC is zero. Assuming not enough text has been provided to analyse.')
            return

        ui.label(f'Poisson distribution at {PO_SCALE}x rounded scale, X~Po({math.ceil(IOC_ENG*PO_SCALE)}) at {SIG_1}% significance when P(X≤{math.ceil(text_ioc*PO_SCALE)}) and {SIG_2}% when P(X≥{math.ceil(text_ioc*PO_SCALE)}) has revealed insight:').style('color: #77f')
        if doesnt_match_english:
            if IOC_ENG > text_ioc:
                ui.label('Text does not seem to match the IOC of English. As the IOC is much lower, this is possibly a polyalphabetic cipher.').style('color: #99f')
            elif text_ioc > IOC_ENG:
                ui.label('Text does not seem to match the IOC of English. As the IOC is much higher, this is possibly a polyalphabetic cipher.').style('color: #99f')
        else:
            ui.label('Text seems to be close to the IOC of English. This means a subsitution, transposition, shift, keyword cipher or other cipher is possible.').style('color: #99f')

        ui.separator()
    # IOC of columns based on rows off keyword

    ioc_table = {}
    with util_space:
        l = ui.list()

    maximum = 20
    for k in range(2, maximum+1):
        # k is length of key. We take every kth multiple in the text and get record the IOC.
        testing_column = ''
        for index, char in enumerate(text):
            # print(index, k, index % k, char)
            if index % k != 0: continue
            testing_column += char

        # print(testing_column)
        col_ioc = work_ioc(testing_column)
        ioc_table[k] = col_ioc
        
        with l:
            ui.label(f'k={k} -> '+ str(col_ioc)).style(f'color: {'#f55' if ioc_eng_match_threshold(col_ioc) else '#5f5'}')
    
    closest_value = get_closest([ioc_table[x] for x in ioc_table], IOC_ENG)
    best_keys = [str(k) for k,v in ioc_table.items() if v==closest_value]
    with util_space:
        ui.separator()
        with ui.row():
            ui.label(f'Best key lengths: {', '.join(best_keys[:maximum//2])}, with an IOC of {str(closest_value)} - closest to the IOC of English, which is {IOC_ENG}').style('color: #77f')


def get_pt_ioc(ciphertext_hold:Hold, plaintext_hold:Hold, util_space:ui.row, function_holds:dict):
    return get_ioc(plaintext_hold, ciphertext_hold, util_space, function_holds)


# for x in range(0, 100, 2):
#     print(
#         'PAST THRESHOLD:',
#         past_significance_threshold(
#         lam=math.ceil(IOC_ENG*100),
#         test=math.ceil(x/10),
#         significance=40/100,
#         significance_2=40.8/100,
#         testing=sig_test_type.BOTH
#         ),
#         x/100,
#         IOC_ENG,
#         # x,
#         # IOC_ENG*100
#     )