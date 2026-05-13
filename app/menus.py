from nicegui import ui
from utils.ngui_elements import *
from utils.bindutils import *

def display_selection_screen(possible_decipher_machines:dict):
    # title('Ciphertext Decoder')
    # ui.separator()

    current_machine = Hold()
    all_tabs = []
    associated_fn = []
    with ui.element('div').classes('p-1 w-full'):
        with ui.tabs(on_change=lambda n: current_machine.set(v=n.value)) as tabs:
            for machine in possible_decipher_machines:
                all_tabs.append(ui.tab(name=machine))
                associated_fn.append(possible_decipher_machines.get(machine))

        with ui.tab_panels(tabs, value=all_tabs[-1] or None):
            for i,t in enumerate(all_tabs):
                with ui.tab_panel(t).classes('w-full').bind_visibility_from(current_machine, current_machine.t()):
                    associated_fn[i]()

                    



            # for machine in possible_decipher_machines:
            #     menu = possible_decipher_machines.get(machine)
            #     with ui.tab_panel().bind_visibility_from(current_machine, current_machine.t()):
            #         menu()
                # with ui.element('div').classes('p-3 w-full').bind_visibility_from(current_machine, current_machine.t()):
    ui.run()