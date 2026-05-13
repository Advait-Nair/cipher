from utils.words import *
from utils.bindutils import *
from nicegui import ui
from app.ciphers import *
from copy import deepcopy
from utils.ngui_elements import *
from utils.generic import snake_to_natural_case
import asyncio


def time_notify(message, *args, **kwargs):
    print(f'TIME_NOTIFY {message}')
    return ui.notify(message=message, *args, **kwargs)
    # prevent_duplicate_calls('time-notify-duplicate-preventer', ui.notify, threshold=0.1, message=message, *args, **kwargs)

rerun_workers = []
recurse_running = False
on_arg_change_rerun = Hold(False)

class Status:
    RUNNING = 'Running Task...'
    AUTO_RUN = 'Auto-Run Mode'


statuses = []
def UnifiedTools():
    ciphertext = Hold('')
    plaintext = Hold('')
    chosen_cipher = Hold({})
    chosen_cipher_name = Hold('Choose a cipher')
    pcalc = Hold(100*percentage_words(is_word(plaintext.value.split(' '))))
    

    def get_fn():
        function = chosen_cipher.value.get('function')
        if not callable(function): return False
        if not chosen_cipher.value.get('function'): return False
        return function
    
    notify_drawer = ui.row()
    cipher_ui_row = ui.row().classes('w-full bg-neutral-800 p-3 empty:hidden')
    custom_ui_row = ui.row().classes('w-full')
    
    main_row = ui.row().classes('fixed bottom-0 gap-3 left-0 right-0 p-4 flex items-center justify-end w-full z-100')
    status_row = ui.row().classes('fixed top-2 gap-5 left-2 right-2 px-4 h-7 flex items-center justify-start w-full z-100 font-monospace')

    def set_status_row():
        with status_row:
            status_row.clear()
            for status in statuses:
                ui.label(status).classes('rounded-full bg-gray-800 px-2 py-1')

    def add_status(status: str):
        if not status in statuses:
            statuses.append(status)
        set_status_row()
    
    def remove_status(status: str):
        statuses.remove(status)
        set_status_row()

    # cycling_arg:Hold = None
    global recurse_running
    def render_fn_ui():
        global recurse_running
        async def no_recurse_run():
            if not on_arg_change_rerun.value: return
            await execute_task()
        
        async def execute_task():
            global recurse_running
            if recurse_running: return
            recurse_running = True
            add_status(Status.RUNNING)
            await run(no_recurse=True)
            recurse_running = False
            remove_status(Status.RUNNING)
        
        with main_row:
            main_row.clear()
            with ui.row().classes('py-3 px-8 bg-black rounded-full'):
                ui.checkbox('Auto-run enabled', on_change=lambda: add_status(Status.AUTO_RUN) if on_arg_change_rerun.value else remove_status(Status.AUTO_RUN)).classes('rounded-full text-white').bind_value(on_arg_change_rerun, on_arg_change_rerun.t())
            if get_fn() and len(wash(ciphertext.value)) > 0:
                ui.button('Execute Task', on_click=execute_task, color="#ffc400", icon='play_circle').classes('py-3 px-8 rounded-full text-black')

        function = get_fn()
        if not function: return
        custom_ui_row.clear()
        with custom_ui_row:
            # Get kwargs of function
            args = function(getexposed=True)
            for arg in args:
                arg_hold:Hold = args[arg]
                natural_name = snake_to_natural_case(arg)

                def set_carg():
                    global cycling_arg
                    print('Setting cycling_arg to',arg_hold)
                    cycling_arg = arg_hold

                # strings
                if arg_hold.type() == str:
                    ui.input(label=natural_name, on_change=no_recurse_run).classes('w-full').bind_value(arg_hold, arg_hold.t())
                
                # ranged ints
                if arg_hold.type() in (int, float) and arg_hold.sp_exists('range_min') and arg_hold.sp_exists('range_max'):
                    with ui.column():
                        with ui.row():
                            ui.label(natural_name)
                            ui.label().bind_text(arg_hold, arg_hold.t()).classes('font-bold')
                            ui.label(arg_hold.getsp('range_min')).classes('opacity-40')
                    with ui.column().classes('w-50'):
                        ui.slider(min=arg_hold.getsp('range_min'), max=arg_hold.getsp('range_max'), on_change=no_recurse_run).bind_value(arg_hold, arg_hold.t())
                    with ui.column():
                            ui.label(arg_hold.getsp('range_max')).classes('opacity-40')
                    
                    ui.button(f'Use {natural_name} as cycler', color='#2').on_click(set_carg)
                
                # unranged ints
                elif arg_hold.type() in (int, float):
                    ui.number(label=natural_name, on_change=no_recurse_run).classes('w-full').bind_value(arg_hold, arg_hold.t())
                    ui.button(f'Use {natural_name} as cycler', color='#2').on_click(set_carg)
                
                # booleans
                elif arg_hold.type() == (bool):
                    ui.checkbox(text=natural_name, on_change=no_recurse_run).classes('w-full').bind_value(arg_hold, arg_hold.t())
                
                # dicts/jsons
                elif arg_hold.type() == (dict):
                    print(arg_hold.value)
                    t_hold = Hold(json.dumps(arg_hold.value))
                    async def update(d):
                        actual_dict = d.content['json'] if d.content.get('json') else d.content['text']
                        # actual_dict = d.content.get('text', False)
                        # if not actual_dict: return
                        # arg_hold.set(json.loads(t_hold.value))
                        arg_hold.set((actual_dict))
                        # arg_hold.set(json.loads(actual_dict))
                        await no_recurse_run()
                    ui.json_editor({'content': {'text':arg_hold.value, 'json':arg_hold.value}}, on_change=update).classes('w-full')
                    # ui.input(label='Substitution Map').bind_value(t_hold).on_value_change(update)

            sep().classes('mt-10')


    async def configured_cipher(ciphertext:str, no_ui=False) -> str:

        def runner():
            function = get_fn()
            if not function: return ''

            rest_kwargs = deepcopy(function(getexposed=True))
            for kwarg in rest_kwargs:
                rest_kwargs[kwarg] = rest_kwargs[kwarg].value
            
            cipher_ui_row.clear()
            function = stopwatch(function) # apply stopwatch returner
            with notify_drawer:
                time_notify(f'Cipher processing has begun.')
            result, time_taken = function(ciphertext=ciphertext, ui_row=(cipher_ui_row), **rest_kwargs) or ''
            with notify_drawer:
                time_notify(f'Cipher processing took {round(time_taken)} seconds to complete.')
            return result

        return await asyncio.to_thread(runner)
        
    


    # THE UPDATERS
    def recalc_p():
        pcalc.set(100*percentage_words(is_word(plaintext.value.split(' ')), dp=3))

    
    async def run(n=None, no_recurse=False):
        # SET ciphertext AND SUBMAP HERE
        result = await configured_cipher(ciphertext=ciphertext.value, no_ui=no_recurse)
        plaintext.set(result)


        recalc_p()
        for worker in rerun_workers: worker()

        if not no_recurse: render_fn_ui()
    


    # THE TWO BASE INPUTS
    with ui.element('div').classes('w-full grid grid-cols-2 gap-4 max-md:grid-cols-1'):
        ui.textarea('Ciphertext', on_change=render_fn_ui).classes('w-full').bind_value(ciphertext)
        ui.textarea('Decoded plaintext', on_change=recalc_p).classes('w-full').bind_value_from(plaintext)
        

    # CONFIGURATORS
    with ui.row().classes('grid grid-cols-5 w-full max-md:grid-cols-3 max-sm:grid-cols-1'):
        with ui.dropdown_button('Choose a cipher').bind_text_from(chosen_cipher_name, chosen_cipher_name.t()):
            for pcipher in cipher_list:
                async def set_cipher(args):
                    ttext = args.sender.text
                    for item in cipher_list:
                        if item['name'] == ttext:
                            p = item
                            break
                    chosen_cipher.set(p)
                    chosen_cipher_name.set(p.get('name'))
                    global cycling_arg
                    cycling_arg = None

                    # await run(None)
                    render_fn_ui()
                
                ui.button(pcipher.get('name'), on_click=set_cipher, color='bg-gray-800').classes('w-full')

    
    sep().classes('mt-10')
    util_space = ui.row()
    with ui.row():
        for tool in tool_list:
            def onclick(args):
                ttext = args.sender.text
                for item in tool_list:
                        if item['name'] == ttext:
                            reqtool = item
                            break
                
                fn = reqtool.get('function')
                util_space.clear()
                function_holds = {} # Allow access to holds of cipher_list functions
                for pc in cipher_list:
                    function_holds[pc.get('name')] = pc.get('function')(getexposed=True)

                rww = fn(ciphertext_hold=ciphertext, plaintext_hold=plaintext, util_space=util_space, function_holds=function_holds)
                if callable(rww): rerun_workers.append(rww)

            
            ui.button(tool.get('name'), color='bg-gray-700', on_click=onclick)
        ui.button('Close tool', color="#2d005a", on_click=util_space.clear)



    
    with ui.row():
        ui.label('Percentage of recognised words:')
        ui.label().bind_text(pcalc, pcalc.t())
        ui.label('%')


    lower_limit = Hold(0)
    upper_limit = Hold(100)
    async def cycle():

        if not cycling_arg:
            print('Nothing to cycle!')
            return

        minimum = cycling_arg.subproperties.get('range_min', lower_limit.value)
        maximum = cycling_arg.subproperties.get('range_max', upper_limit.value)

        best_score = 0

        best_score_i = minimum
        for i in range (minimum, maximum):
            cycling_arg.set(i)
            result = await configured_cipher(ciphertext=ciphertext.value, no_ui=True)
            score = work_out_unwhitespaced_words_percent(result).count
            if score > best_score:
                best_score = score
                best_score_i = i
        
        cycling_arg.set(best_score_i)
        render_fn_ui()
        await run()

        

    ui.separator()
    with ui.row():
        ui.number(label='min').bind_value(lower_limit)
        ui.number(label='max').bind_value(upper_limit)

        ui.button('Execute cycling and land on best score').on_click(cycle)