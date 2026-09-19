from nicegui import ui, app
from pathlib import Path

import numpy as np

import io
import wave
import base64
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


def folder_card(
        title: str,
        *,
        bg: str = '#252A41',
        border: str = '#70B77E',
        width: int = 400,
        height: int = 200,
        tab_width: int = 155,
        tab_height: int = 30,
        radius: int = 14,
        curve: int = 60,
        border_width: float = 0,
        title_color: str | None = None,
        padding: int = 16,
) -> ui.column:
    title_color = title_color or border

    path = (
        f'M {radius},0 '
        f'H {tab_width} '
        f'C {tab_width + curve * 0.6},0 {tab_width + curve * 0.4},{tab_height} {tab_width + curve},{tab_height} '
        f'H {width - radius} '
        f'Q {width},{tab_height} {width},{tab_height + radius} '
        f'V {height - radius} '
        f'Q {width},{height} {width - radius},{height} '
        f'H {radius} '
        f'Q 0,{height} 0,{height - radius} '
        f'V {radius} '
        f'Q 0,0 {radius},0 '
        f'Z'
    )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" style="position:absolute;inset:0;display:block;">'
        f'<path d="{path}" fill="{bg}" stroke="{border}" stroke-width="{border_width}"/>'
        f'</svg>'
    )

    wrapper = ui.element('div').style(
        f'position:relative; width:{width}px; height:{height}px;'
    ).classes('flex')
    with wrapper:
        ui.html(svg).style('position:absolute; inset:0; pointer-events:none;')

        with ui.element('div').style(
                f'position:absolute; top:0; left:0; width:{tab_width}px; height:{tab_height}px; '
                f'display:flex; align-items:center; padding-left:{padding}px; z-index:1; '
                f'box-sizing:border-box;'
        ):
            ui.label(title).style(
                f'color:{title_color}; font-family: "Trade Winds", system-ui; font-weight:600; font-size:24px; '
                f'white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'
            )

        content = ui.column().style(
            f'position:absolute; top:{tab_height}px; left:0; right:0; bottom:0; '
            f'padding:{padding}px; z-index:1; overflow:auto; gap:8px; '
            f'box-sizing:border-box;'
        ).classes('flex')

    return content

def make_tone_wav(frequency=440, duration=0.5, volume=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(frequency * t * 2 * np.pi)
    audio = (tone * volume * 32767).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    b64 = base64.b64encode(buf.getvalue()).decode()
    return f'data:audio/wav;base64,{b64}'

# noinspection bad-index
def page():
    app.add_static_files('/static', Path(f'{path}/static'))

    # Variables

    ev_keys = {
        'EMF 5': 'emf5.svg',
        'D.O.T.S. Projector': 'dots.svg',
        'Ultraviolet': 'uv.svg',
        'Freezing Temperatures': 'freezing.svg',
        'Ghost Orbs': 'orbs.svg',
        'Ghost Writing': 'writing.svg',
        'Spirit Box': 'spirit.svg',
    }

    game_data = load_from_yaml()

    evidence_markers = {}

    for ev in game_data['Evidence']:
        smart = game_data['Evidence'][ev]
        evidence_markers[ev] = {
            'icon': f'https://gitlab.com/xplus-studios/xplus.dev-images/-/raw/main/projects/phas/icons/{smart['img']}?ref_type=heads',
            'state': None,
            'color': '#FFF'
        }

    ghost_folders = {}

    for ghost in game_data['Ghosts']:
        sg = game_data['Ghosts'][ghost]

        evidence_imgs = []
        for i in sg['Evidence']:
            evidence_imgs.append(f'https://gitlab.com/xplus-studios/xplus.dev-images/-/raw/main/projects/phas/icons/{ev_keys[i]}?ref_type=heads')

        ghost_folders[ghost] = {
            'name': ghost,
            'evidence': sg['Evidence'],
            'ev_imgs': evidence_imgs,
            'sanity': sg['Sanity'],
            'sanity_img': 'https://gitlab.com/xplus-studios/xplus.dev-images/-/raw/main/projects/phas/icons/brain.svg?ref_type=heads'
        }

    folders = ui.row().classes('justify-center')

    # Functions

    def handle_evidence():
        folders.clear()

        active = {}
        gathered = {}
        val_map = {'N': None, 'T': True, 'F': False}

        for evi in evidence_markers:
            se = evidence_markers[evi]
            gathered[evi] = val_map[se['state'].value]

        # Determine which ghosts are still active based on gathered evidence
        for ghost in ghost_folders:
            data = ghost_folders[ghost]
            ghost_evidence = data['evidence']

            mapped = [gathered[e] for e in ghost_evidence]

            if False in mapped:
                continue  # a required piece of evidence was ruled out

            non_none = [v for v in mapped if v is not None]
            if non_none and not all(v is True for v in non_none):
                continue  # some evidence is neither confirmed True nor still unknown

            # exclude if any evidence NOT in this ghost's list has been confirmed True
            outside_true = any(
                gathered[e] is True
                for e in gathered
                if e not in ghost_evidence
            )
            if outside_true:
                continue

            active[ghost] = data

        with folders:
            for ghost, data in active.items():
                with folder_card(ghost):
                    with ui.row().classes('w-full h-full'):
                        with ui.column().classes('w-1/2'): # Left side of folder
                            with ui.row(): # Evidence
                                for i in range(len(data['evidence'])):
                                    with ui.image(data['ev_imgs'][i]).classes('w-5 object-contain') as ev_icon:
                                        ev_icon.tooltip(data['evidence'][i])
                            with ui.column().classes('w-full h-24 justify-center bg-indigo-950 rounded-sm border-2 border-indigo-800 gap-0'): # Sanity thresholds

                                if type(data['sanity']) is float:
                                    with ui.row().classes('w-full'):
                                        ui.image(data['sanity_img']).classes('w-7 p-1')
                                        c_classes = 'ghost text-lg'
                                        if data['sanity'] > 0.65:
                                            c_classes += ' text-red-600'
                                        elif data['sanity'] < 0.5:
                                            c_classes += ' text-lime-400'
                                        ui.label(f'{round(data['sanity']*100)}%').classes(c_classes)
                                else:

                                    opt_key = {
                                        'Still': 0,
                                        'Walking': 1,
                                        'Weakened': 2,
                                        'Normal': 3,
                                        'Enraged': 4,
                                        'Movement': 5,
                                        'Light Switch On': 6,
                                        'Light Switch Off': 7,
                                        'Calm': 8,
                                        'Aggressive': 9,
                                        'Near Firelights': 10,
                                        'Ability': 11,
                                        'Active Equipment': 12,
                                        'Old': 13,
                                        'Young': 14,
                                        'Talking': 15,
                                        'Copies mimicked ghost': 16
                                    }

                                    for sanity in data['sanity']:
                                        print(ghost)
                                        sk, si = list(sanity.keys())[0], list(sanity.values())[0]

                                        with ui.row().classes('p-0 m-x-0 -m-y-4'):
                                            c_classes = 'ghost text-lg'
                                            if si > 0.65:
                                                c_classes += ' text-red-600'
                                            elif si < 0.5:
                                                c_classes += ' text-lime-400'

                                            ui.image(data['sanity_img']).classes('w-7 p-0 m-x-0 -m-y-4')
                                            ui.label(f'{round(si*100)}%').classes(c_classes)



    ui.colors(
        primary='#335A33',
        secondary='#E5E7F0',
        accent='#70B77E',
        dark_page='#3C4468',
        positive='#60D336 ',
        negative='#F50031',
        warning='#F0F600'
    )

    ui.add_head_html('''
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Trade+Winds&display=swap" rel="stylesheet">

        <style>.ghost {
            font-family: 'Trade Winds', system-ui;
            font-style: bold;
        }
        </style>
        ''')

    with ui.header():

        ui.button('Evidence', on_click=lambda: left_drawer.toggle(), icon='rule').props('color=amber-7 flat rounded dense').classes('ghost !text-md')
        ui.space()
        ui.label('Phasmobobia QRH').classes('ghost text-2xl')


    with ui.left_drawer(elevated=True, top_corner=True, value=True) as left_drawer:

        ui.label('Evidence').classes('ghost text-xl')

        for ev in evidence_markers:

            cd = ui.checkbox(on_change=lambda: handle_evidence(), value='N').props('color=pink dense toggle-indeterminate toggle-order=ft true-value=T false-value=N indeterminate-value=F modal-value=N')
            with cd:
                with ui.row().classes('w-full'):
                    ui.image(evidence_markers[ev]['icon']).classes('w-4 object-contain')
                    ui.label(ev).classes(f'color-{evidence_markers[ev]['color']}')
            evidence_markers[ev]['state'] = cd



        ui.separator()

        ui.label('Map').classes('ghost text-xl')
        map1 = ui.select(list(game_data['Maps']), on_change=lambda e: map_update(e)).classes('ghost w-full !text-sm').props('outlined dense')
        map2 = ui.select([], on_change=lambda: update_map_img()).props('outlined dense').classes('w-full').disable()

        with ui.dialog() as map_dialog, ui.card().classes('w-full md:scale-150 lg:scale-200'):
            dialog_map_img = ui.image().classes('w-full')

        with ui.row().classes('w-full'):

            with ui.column():
                map_info_classes = 'w-full rounded-md border -my-1 py-1 px-1'
                with ui.row().classes(map_info_classes) as map_info_box:
                    ui.label('Size:').classes('text-inherit')
                    ui.space()
                    map_size = ui.label('??')
                with ui.row().classes(map_info_classes):
                    ui.label('Rooms:')
                    ui.space()
                    room_count = ui.label('??')
                with ui.row().classes(map_info_classes):
                    ui.label('Floors:')
                    ui.space()
                    floor_count = ui.label('??')
            with ui.button('', on_click=lambda: open_map_dialog()).classes('grow').props('flat dense'):
                map_img = ui.image().classes('size-20 object-cover')
                ui.icon('link').classes('absolute top-1 right-1').props('color=positive')

        ui.separator()

        with ui.tabs().classes('w-full ghost') as tabs:
            metronome = ui.tab('Metronome')
            sanity = ui.tab('Sanity')
        with ui.tab_panels(tabs, value=metronome).classes('w-full'):

            with ui.tab_panel(metronome):

                with ui.row().classes('justify-center'):

                    def update_metro_time(negative=False):
                        temp = 0.1

                        if negative:
                            temp *= -1

                        old = float(metro_m_s.text)

                        metro_m_s.set_text(str(round(old + temp, 1)))


                    with ui.card().classes('').tight():
                        with ui.row().classes(''):
                            ui.button(icon='remove', on_click=lambda: update_metro_time(True)).props('tight padding=xs size=sm color=red')
                            ui.space()
                            metro_m_s = ui.label('1.7').classes('ghost p-x-2 text-lg')
                            ui.space()
                            ui.button(icon='add', on_click=lambda: update_metro_time()).props('tight padding=xs size=sm color=blue')

                    def play_tone():
                        audio_src = 'https://gitlab.com/xplus-studios/xplus.dev-images/-/raw/main/projects/phas/metronome/tick.wav?ref_type=heads'
                        ui.audio(audio_src).props('autoplay').classes('hidden')

                    metronome_timer = ui.timer(1/float(metro_m_s.text), play_tone, active=False)

                    ui.button(icon='play_arrow', on_click=lambda: metronome_timer.activate()) \
                        .bind_visibility_from(metronome_timer, 'active', value=False) \
                        .props('text-color=green-5 round outline size=sm')

                    ui.button(icon='stop', on_click=lambda: metronome_timer.deactivate()) \
                        .bind_visibility_from(metronome_timer, 'active', value=True) \
                        .props('text-color=red-5 round outline size=sm')




        def open_map_dialog():
            dialog_map_img.set_source(map_img.source)
            map_dialog.open()

        def update_map_img():

            # noinspection bad-argument-type
            def update_info(map, map2:int|None=None, map2r:bool=False):

                map2_check = type(map2) is int

                map_key = {
                    'Small': ['SM', 'green-500'],
                    'Medium': ['MD', 'yellow-500'],
                    'Large': ['LG', 'rose-500'],
                    '??': ['??', 'slate-500']
                }

                # One : {'size': 'Small', 'Rooms': 12, 'Floors': 2, 'Exits': 1, 'map': 'tanglewood.png'}
                # Two (m) : {'size': 'Medium', 'Rooms': [12, 12, 13, 13], 'Floors': [1, 1, 2, 2], 'Exits': [2, 2, 1, 1], 'map': ['brownstone_restricted_f1_left.png', 'brownstone_restricted_f1_right.png', 'brownstone_restricted_f2_left.png', 'brownstone_restricted_f2_right.png'], 'optional': ['F1 Left', 'F1 Right', 'F2 Left', 'F2 Right']}

                if map2_check is False and not map2r:
                    mc = map_key[map['size']][1]
                    ms = map_key[map['size']][0]
                    rc = map['Rooms']
                    fc = map['Floors']
                elif map2_check is False and map2r:
                    mc = map_key['??'][1]
                    ms = map_key['??'][0]
                    rc = '??'
                    fc = '??'
                elif type(map2) is int:
                    print(map_key[map['size']][0])
                    mc = map_key[map['size']][1]
                    ms = map_key[map['size']][0]
                    rc = map['Rooms'][map2]
                    fc = map['Floors'][map2]
                else:
                    mc, ms, rc, fc = None, None, None, None

                    ui.notify('Maps Not Defined!!!! HELP!!!!', type='negative')

                if None not in [mc, ms, rc, fc]:
                    map_size.set_text(ms)
                    room_count.set_text(rc)
                    floor_count.set_text(fc)
                    map_info_box.classes(replace=f'row nowrap w-full rounded-md border -my-1 py-1 px-1 text-{mc} border-{mc}')


            img_source = 'https://gitlab.com/xplus-studios/xplus.dev-images/-/raw/main/projects/phas/maps/'
            map_selection = game_data['Maps'][map1.value]
            a = map1.value
            b = map2.value

            if map_selection.get('optional') is None and b is None:
                # map_index = map_selection['optional'].index(b)
                print(f'Map has one option, attempting: {map_selection['map']}')
                update_info(map_selection)
                map_img.set_source(f'{img_source}{map_selection['map']}?ref_type=heads')
            elif map_selection.get('optional') is not None and b is not None:
                map_index = map_selection['optional'].index(b)
                ui.notify(f'Optional Selected: [{map_index}]')
                update_info(map_selection, map_index)
                map_img.set_source(f'{img_source}{map_selection['map'][map_index]}?ref_type=heads')
                print(f'Map and Map2 are set, attempting: {map_selection['map'][map_index]}')
            else:
                print(f'Multiple Maps, awaiting Map2 ... [Options]: {map2.options}')
                update_info(map2, map2r=True)
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


    handle_evidence()