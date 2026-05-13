from multiprocessing import freeze_support
freeze_support() # noqa
# import sys
# sys.stdout = open('main.log','a')

from app.cipher_menus.caesar import ConductCaesarCipher
from app.cipher_menus.substitution_cipher import SubstitutionCipher
from app.cipher_menus.order_analysis import OrderAnalysis
from app.unified_cipher_tools import UnifiedTools

from app.menus import display_selection_screen
from nicegui import ui, app, native

ui.dark_mode(value=True)
ui.add_css('*:not(i) {font-family: "Inter", sans-serif}')

display_selection_screen({
    'Caesar Cipher': ConductCaesarCipher,
    'Substitution Cipher': SubstitutionCipher,
    'Order Analysis (unstable)': OrderAnalysis,
    'Unified Cipher Tools': UnifiedTools,
})



# ui.run(title='Cipheria', favicon='cipheria.png', reload=False, native=True)
ui.run(title='Cipheria', favicon='cipheria.png', reload=False)
