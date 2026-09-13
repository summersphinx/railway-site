from nicegui import ui, app
from pathlib import Path

import yaml

path = Path(__file__).parent / ""

def load_from_yaml():
    """
    Parse seven.yaml to extract:
      - MOVE_LIST: ordered list of move names (series > data > name)
      - MOVE_COLORS: {name: hex color} (series > data > itemStyle > color)
      - WIN_MAP: {name: [names it beats]} (series > links, source beats target)
    Falls back to sensible defaults if the file isn't found.
    """
    yaml_path = Path(f'{path}/phas.yaml')
    if yaml_path.exists():
        data = yaml.safe_load(yaml_path.read_text())
        return data
    else:
        return 'Broken'

def page():
    app.add_static_files('/static', Path(f'{path}/static'))

    game_data = load_from_yaml()

    ui.add_head_html('''
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Trade+Winds&display=swap" rel="stylesheet">

        <style>.ghost {
            font-family: 'Trade Winds', system-ui;
            font-size: 24px;
            font-style: bold;
        }
        </style>
        ''')

    with ui.header():

        ui.button('Evidence', on_click=lambda: left_drawer.toggle(), icon='rule').props('color=deep-purple-14 flat rounded dense')
        ui.space()
        ui.label('Phasmobobia QRH').classes('ghost')
        ui.space()
        ui.button('Ghosts', on_click=lambda: right_drawer.toggle(), icon='rule').props('color=deep-purple-14 flat rounded dense')

    with ui.left_drawer(elevated=True, top_corner=True) as left_drawer:
        ui.label('Evidence').classes('ghost')
        for ghost in game_data['Evidence']:
            with ui.checkbox(ghost).props('toggle-indeterminate toggle-order=ft dense'):
                ui.tooltip(game_data['Evidence'][ghost]['description'])
        ui.separator()
        ui.label('Map').classes('ghost')
        map1 = ui.select(list(game_data['Maps']), on_change=lambda e: map_update(e)).classes('ghost w-full !text-sm').props('outlined dense')
        map2 = ui.select([], on_change=lambda: update_map_img()).props('outlined dense').classes('w-full').disable()

        with ui.dialog() as map_dialog, ui.card().classes('w-full md:scale-150 lg:scale-200'):
            dialog_map_img = ui.image().classes('w-full')

        with ui.row().classes('w-full h-8'):

            with ui.column():
                map_info_classes = ''
                with ui.row().classes('w-full rounded-md border py-2 px-1'):
                    ui.label('Size:')
                    ui.space()
                    map_size = ui.label('??')
                with ui.row().classes('w-full rounded-md border py-2 px-1'):
                    ui.label('Rooms:')
                    ui.space()
                    room_count = ui.label('??')
                with ui.row().classes('w-full rounded-md border py-2 px-1'):
                    ui.label('Floors:')
                    ui.space()
                    floor_count = ui.label('??')
            with ui.button('', on_click=lambda: open_map_dialog()).classes('grow').props('flat dense'):
                with ui.image().classes('size-20 object-cover') as map_img:
                    ui.icon('link').classes('relative top-1 right-1')

        def evidence_update(e):
            print(e.value)

        def open_map_dialog():
            dialog_map_img.set_source(map_img.source)
            map_dialog.open()

        def update_map_img():
            img_source = 'https://gitlab.com/xplus-studios/xplus.dev-images/-/raw/main/projects/phas/'
            map_selection = game_data['Maps'][map1.value]
            a = map1.value
            b = map2.value

            if map_selection.get('optional') is None and b is None:
                # map_index = map_selection['optional'].index(b)
                print(f'Map has one option, attempting: {map_selection['map']}')
                map_img.set_source(f'{img_source}{map_selection['map']}?ref_type=heads')
            elif map_selection.get('optional') is not None and b is not None:
                # map_img.set_source(map_selection['map'])
                map_index = map_selection['optional'].index(b)
                map_img.set_source(f'{img_source}{map_selection['map'][map_index]}?ref_type=heads')
                print(f'Map and Map2 are set, attempting: {map_selection['map'][map_index]}')
            else:
                print(f'Multiple Maps, awaiting Map2 ... [Options]: {map2.options}')
                map_img.set_source('https://gitlab.com/xplus-studios/xplus-toolkit/-/raw/main/logo/Icon-maintenence.png?ref_type=heads')

        def map_update(e):
            if game_data['Maps'][e.value].get('optional') is not None:
                map2.enable()
                map2.set_options(game_data['Maps'][e.value].get('optional'))
            else:
                map2.set_options([], value='')
                map2.disable()
            ui.update()
            update_map_img()



    with ui.right_drawer(elevated=True, top_corner=True) as right_drawer:
        ui.label('Ghosts').classes('ghost')
        for ghost in game_data['Ghosts']:
            ui.checkbox(ghost).props('toggle-indeterminate toggle-order=ft dense')


    with ui.row().classes('w-full'):
        ghosts = game_data['Ghosts']
    ui.label('This is a WIP, will be updated soon!')