from nicegui import ui

def title(t:str):
    with ui.element('h1').classes('p-2 font-semibold text-3xl pb-5'): ui.label(t)
def subtitle(t:str):
    with ui.element('h2').classes('ml-2 font-normal py-2 text-xl'): ui.label(t)
def sep(): return ui.separator().classes('opacity-50')