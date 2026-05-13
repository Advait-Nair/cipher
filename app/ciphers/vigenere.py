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



def work_ptchar(cipher_char, keyword_char):
    p_i = (ALPHABET.find(cipher_char.upper()) - ALPHABET.find(keyword_char.upper())) % len(ALPHABET)
    # print(
    #     cipher_char.ljust(2,' '),
    #     str(ALPHABET.find(cipher_char.upper())).ljust(4,' '),
    #     keyword_char.ljust(2,' '),
    #     str(ALPHABET.find(keyword_char.upper())).ljust(4,' '),
    #     p_i
    # )
    return ALPHABET[p_i-1]

def work_vigenere(ciphertext, key):
    solution = ''
    non_wsp = ciphertext.replace(' ','')

    wsp_added = 0
    for i in range(len(non_wsp)):
        if ciphertext[i + wsp_added] == ' ':
            wsp_added += 1
            solution += ' '
        solution += work_ptchar(cipher_char=non_wsp[i], keyword_char=(key[i % len(key)]))
    

    return solution

@expose_args({
    'keys': Hold('CHARLES'),
    'selected_key': Hold(1),
    'look_for': Hold('')
})
def vigenere_cipher(ciphertext:str, keys:str, selected_key:int, look_for:str, ui_row=None):
    # p_i = (c_i - k_i) mod 26
    
    key = keys.replace(' ','').split(',')[int(selected_key or 1)-1]

    if len(look_for.strip()) > 0:
        for word in word_dict:
            # print('word',look_for, word)
            result = work_vigenere(ciphertext=ciphertext, key=word)
            if look_for.strip().upper() in result.upper():
                # print(result)
                return result

    return work_vigenere(ciphertext=ciphertext, key=key)



def rebuild_subtexts(subtexts:list[list]):
    output = ''

    loop_flag = True
    ptr = 0
    while loop_flag:
        invocations = 0
        for subtext in subtexts:
            if len(subtext) > ptr:
                output += subtext[ptr]
            else:
                invocations += 1
        
        if invocations >= len(subtexts): break
        ptr += 1


    # total_chars = sum([len(x) for x in subtexts])
    # modulo = len(subtexts)
    # advancement = 0
    # for i in range(total_chars):
    #     chosen_list = i % modulo
    #     print(subtexts, chosen_list)
    #     output += subtexts[chosen_list][advancement]
    #     # advancement += 1 if chosen_list == 0 else 0
    # print(output)
    
    return output

@expose_args({
    'key_length': Hold(1),
    'caesar_frequency_leniency': Hold(3, {
        'range_min': 1,
        'range_max': 5
    }),
    'target_crib_CSV': Hold(''),
    'dictionary_brute_force': Hold(False),
    'best_ioc': Hold(False),
    'custom_map': Hold(''),
    'explicit_offset': Hold(False)

})
def vigenere_bruter(ciphertext:str, key_length:int, explicit_offset:bool, custom_map:str, dictionary_brute_force:bool, best_ioc:bool, target_crib_CSV:str, caesar_frequency_leniency:int=3, ui_row=None):
    key_length = int(key_length or 5)
    custom_map = custom_map.strip()
    default = [0 for x in range(key_length)]
    offset_choice = default if len(custom_map)==0 else [(0 if not (len(x.strip())>0) else int(x.strip()) ) for x in custom_map.split(',')]
    if len(default) != len(offset_choice): offset_choice = default

    ciphertext = wash(ciphertext)
    # get subtexts of each, i.e. modulus subtexts

    def work():
        # print(offset_choice)
        subtexts = []
        dc_subtexts = []
        for i in range(key_length):
            subtexts.append('')
            for j, char in enumerate(ciphertext):
                if (j) % key_length == 0:
                    subtexts[i] += ciphertext[min(i + j, len(ciphertext)-1)]
        

            # We are going to work out the shift caesar for each as well.

            # Now, we work the caesar shift amount.
            analysis = frequency_analysis(subtexts[i], is_letter=True)

            # Here, we look at the most common alphabets ordered by frequency, and get the ones most likely to be them.
            # If we define an explicit map, we don't do this. We will just pass the offset in

            if not explicit_offset:
                most_common = list(analysis)[offset_choice[i]]
                expected_offset = work_alphabet_offset(most_common, 'e', charset=ALPHABET)
            else:
                expected_offset = offset_choice[i]

            de_caesared = caesar_cipher(expected_offset, subtexts[i], alphabet_map=ALPHABET)
            # print(de_caesared)
            dc_subtexts.append(de_caesared)
        
        
        return rebuild_subtexts(dc_subtexts)



    best_result = work()
    second_best_result = ''

    if len(custom_map) != 0: return best_result
    start_time = time.time()
    best_result_score = 0
    best_configs = {
        "first": default,
        "second": default
    }

    all_pos_perms = allperms(caesar_frequency_leniency, key_length)
    # print(list(all_pos_perms))

    target_crib_CSV = [x.strip() for x in wash(target_crib_CSV).split(',')] if target_crib_CSV.strip() != '' else []

    for perm in all_pos_perms:
        offset_choice = perm
        result = work()
        if dictionary_brute_force:
            score = work_out_unwhitespaced_words_percent(result,negation_threshold=6).percent
            if score > best_result_score:
                best_result_score = score
                second_best_result = best_result
                best_result = result
                best_configs["second"] = best_configs["first"]
                best_configs["first"]  = offset_choice
        
        elif len(target_crib_CSV) > 0:
            score = 0
            for crib in target_crib_CSV:
                if crib in result: score += 1
            
            if score > best_result_score:
                best_result_score = score
                second_best_result = best_result
                best_result = result
                best_configs["second"] = best_configs["first"]
                best_configs["first"]  = offset_choice

            
        elif best_ioc:
            score = work_ioc(text=result)
            if score > best_result_score:
                best_result_score = score
                second_best_result = best_result
                best_result = result
                best_configs["second"] = best_configs["first"]
                best_configs["first"]  = offset_choice
        
    print('best result',
          best_result, 
          'second best',
          second_best_result,
          'best_configs',
          best_configs)
                    
    with ui_row:
        with ui.row().style('display: flex; align-items: flex-start; justify-content: flex-start; flex-direction: column'):
            ui.label('Best Offset Map                : ' + ', '.join(str(x) for x in best_configs['first']))
            ui.label('Second Best Offset Map         : ' + ', '.join(str(x) for x in best_configs['second']))
            ui.label('Second Best Result             : ' + second_best_result)
            ui.label('Total elapsed calculation time : ' + str(time.time() - start_time) + ' seconds')
    
    return best_result


    

# vigenere_bruter(
#     ciphertext="""XSFJD JMNRF RUDJV LMYFT GWWHP TUDIA HWRMS XXAHJ DNBRH
# QTOFF NWFGH GLDJJ ATQWH UEQEM DMHRH LMCGL ZAYBT HUWIC
# MHDJI CGFVZ TJHWR FYBXB HTTLX AHFLY MHDKM ZKTPS SUMRH
# FHLRU WATHU JVLTQ LZSGS NAFWL WUGXD UYCHS WZJWH SIAIY
# GYLSQ CMDDF IMXHX JNNRY REFEX NWHTM LNEDJ CYDRM HIGXL
# VJLXQ HUYLH SLUYL TSVSH NBTQK FHWTQ DNHXU DQRYG YVSQF
# MMRKJ QHZOV SIMGH HTMLN EDJQB YKGZN XSFJD JMNRF XUBIG
# JRUKP PSSOE NVSXY GNRJQ YVYXJ JLBSF JDJMT JJFJA DDLYB
# XZQAA YKXLL DIYXX JWYRF WAYML NPHQY LYHFH LRUWA THBXD
# DQUUT XLYLT SVXTL FNQYN HMJOD NABGO WSOFG HJXIK YHPYM
# HZQVX UGILE FAXXL FYITX WJJUF TIFTH LJQKJ NAJUW FLXRD
# FDGTS BOFSL YRHJL YTUEY BTYWJ FHLKR JRUMN RFXIF JVLWU
# BLKLK IKBDJ IUGIV GRYOJ UQHIF UOWCG HXWAS PHQYW XQTUS
# ASAEJ WLJLL KRJSO FGHJX UGIXK JGTYK KYIWT WZJNK FQKKI
# KRDLN IGMRO JPXWQ GRUMY HJBBB HKEJN ATGAX OLJGL MYKJV
# MQNBS JKHLT REDJX WFWSX NKJDE XBHZO VLCOJ QGMCG YVSGI
# NYKGB CMBDK JHVWB HYYWI XJNHZ BRJQX PFUAN NAJDD QCXXV
# UTLXI VGRYG TWSGF XALUY IKNHK FATNQ KYNAJ JWWGT SVTJW
# TZVWY BXNUW SWKDS LNIGX BKYYF XGAIH HYVMK ZBHLW SNEDV
# UWUFG OWRYL XDYJM KNJGW INXPS YBXRD LNWTQ DFFFR XLKGS
# TQOAJ XVTGW HLTHN WWMEF LVGUK JSSYN XWQKM CWIHF BCMML
# FYBXR HKXUZ JVSSX NXHVY BXRWG WYVWH SYYMM HEFWA NQWZM
# XIWGJ HVWBH YNAJP LMILJ FGIYL WHNTF OJGSW INSGL MYNXH
# GKMXH UWYEX DVLMU MBHJJ MAFUW IUFTQ YYBHX HOMIG JHVJX
# MTFGR GNSLU FNXXH UZLXQ BLMYL JDJJE GTZFF MLDPE JNKNF
# WSWKD SLNIG XBKYY FXDFI BTAHS BYTPQ WXMBS WZFNX AHJDI
# GJLFA IEAHV MULYR HTMLJ VKYBX XDEJM XYRXX YVWHL PYRX""",
# key_length=6,
# dictionary_brute_force=False,
# target_crib_CSV='ENCRYPT'
# )