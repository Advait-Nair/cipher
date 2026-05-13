# Imports for the example whitespace remover
from utils.expose import *
from utils.bindutils import *

class Ciphers:
    Caesar = 'Caesar Cipher'
    Substitution = 'Substitution Cipher'
    Affine = 'Affine Cipher'
    Transposition = 'Transposition Cipher'
    Vigenere = 'Vigenère Cipher'
    VigenereBrute = 'Vigenère Brute Force'
    Playfair = 'Playfair Cipher'
    PlayfairBrute = 'Playfair Brute Force'
    FourSquareCipher = 'Four Square Cipher'

# ? Cipher Imports
from app.ciphers.caesar import *
from app.ciphers.substitution import *
from app.ciphers.frequency_analysis import *
from app.ciphers.affine import *
from app.ciphers.transposition import *
from app.ciphers.vigenere import *
from app.ciphers.playfair import *
from app.ciphers.foursquare import *



cipher_list = [
    {
        'name': Ciphers.Caesar,
        'function': caesar_cipher
    },
    {
        'name': Ciphers.Substitution,
        'function': substitution_cipher
    },
    {
        'name': Ciphers.Affine,
        'function': affine_cipher
    },
    {
        'name': Ciphers.Transposition,
        'function': transposition_cipher
    },
    {
        'name': Ciphers.Vigenere,
        'function': vigenere_cipher
    },
    {
        'name': Ciphers.VigenereBrute,
        'function': vigenere_bruter
    },
    {
        'name': Ciphers.Playfair,
        'function': playfair_cipher
    },
    {
        'name': Ciphers.PlayfairBrute,
        'function': playfair_brute_force
    },
    {
        'name': Ciphers.FourSquareCipher,
        'function': foursquare_cipher
    },
]


# ? Dedicated Tools Imports
from app.ciphers.simpletools import *

tool_list = [
    {
        'name': 'Frequency Analysis Chart',
        'function': plot_frequency_analysis
    },
    {
        'name': 'Whitespace Remover',
        'function': whitespace_remover
    },
    {
        'name': 'Length Finder',
        'function': length_worker
    },
    {
        'name': 'Brute-force Affine',
        'function': brute_force_affine
    },
    {
        'name': 'Find Matches by Order Mapping',
        'function': omap_finder
    },
    {
        'name': 'Work Out Percentage of Recognised Words',
        'function': work_unwhitespaced_words_percentage # can also work for whitespaced words
    },
    {
        'name': 'Calculate IoC for Ciphertext',
        'function': get_ioc
    },
    {
        'name': 'Calculate IoC for Plaintext',
        'function': get_pt_ioc
    },
]