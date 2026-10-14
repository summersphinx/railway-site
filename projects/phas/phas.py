from nicegui import ui, app
from pathlib import Path

import numpy as np

import io
import wave
import base64
import yaml
import re
import time

path = Path(__file__).parent / ""

# Distance between ghost footprints/footsteps, in metres. speed = steps/second * STEP_LENGTH_M.
# This is an approximation (~100 taps/min == 1.7 m/s); tune it if your readings are consistently off.
STEP_LENGTH_M = 1.02
DEFAULT_SPEED_TOLERANCE = 0.15  # m/s, adjustable in the Speed tab

# Ghosts whose two listed speeds are the ends of a continuous range rather than two discrete speeds.
RANGE_SPEED_GHOSTS = {'Deogen'}


def sanity_thresholds(sanity) -> list[float]:
    """Flatten a ghost's 'Sanity' entry (float, list of floats, or list of {label: float}) to floats."""
    if not isinstance(sanity, list):
        sanity = [sanity]
    out = []
    for item in sanity:
        if isinstance(item, dict):
            item = list(item.values())[0]
        if isinstance(item, (int, float)):
            out.append(float(item))
    return out


def passes_sanity(sanity, selected_pct: float) -> bool:
    """True if the ghost has at least one hunt threshold above the selected sanity (%)."""
    return any(round(t * 100, 6) > selected_pct or t >= 1 for t in sanity_thresholds(sanity))


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
        f'viewBox="0 0 {width} {height}" style="position:absolute;inset:0;display:block;overflow:visible;">'
        f'<path d="{path}" fill="{bg}" stroke="{border}" stroke-width="{border_width}"/>'
        f'</svg>'
    )

    wrapper = ui.element('div').style(
        f'position:relative; width:{width}px; height:{height}px;'
    ).classes('flex')
    with wrapper:
        svg_holder = ui.html(svg).classes('folder-svg').style('position:absolute; inset:0; pointer-events:none;')

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

    content.svg_holder = svg_holder  # lets callers toggle the highlight border without a re-render
    return content


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
    ghost_tests = {}
    for ghost in game_data['Ghosts']:
        ghost_tests[ghost] = []

    for ghost in game_data['Ghosts']:
        sg = game_data['Ghosts'][ghost]

        evidence_imgs = []
        for i in sg['Evidence']:
            evidence_imgs.append(
                f'https://gitlab.com/xplus-studios/xplus.dev-images/-/raw/main/projects/phas/icons/{ev_keys[i]}?ref_type=heads')

        for test in game_data['Tests']:

            test_gp = game_data['Tests'][test]  # eg. Equipment
            for sub_test in test_gp:
                sub_test_gp = test_gp[sub_test]  # eg. Incense
                if sub_test_gp.get(ghost):
                    ghost_tests[ghost].append({'type': test, 'name': sub_test, 'text': sub_test_gp.get(ghost)})

        speed_table_vals = game_data.get('GhostSpeedTables', {}).get(sg.get('SpeedTable'))
        if speed_table_vals:
            speed_vals = [v for k, v in speed_table_vals.items() if k != 'Metrics']
        elif isinstance(sg['Speed'], list):
            speed_vals = list(sg['Speed'])
        else:
            speed_vals = []  # e.g. Mimic: 'Any'
        speed_vals = [float(v) for v in speed_vals if isinstance(v, (int, float))]

        ghost_folders[ghost] = {
            'name': ghost,
            'evidence': sg['Evidence'],
            'ev_imgs': evidence_imgs,
            'sanity': sg['Sanity'],
            'sanity_img': 'https://gitlab.com/xplus-studios/xplus.dev-images/-/raw/main/projects/phas/icons/brain.svg?ref_type=heads',
            'speed': sg['Speed'],
            'speed_tt': sg.get('SpeedTooltip'),
            'speed_t': sg.get('SpeedTable'),
            'ghost_tests': ghost_tests[ghost],
            'speed_vals': speed_vals,
        }

    # State

    crossed = set()  # (test_type, sub_test, ghost) entries the user has crossed out
    ev_rows = {}  # key -> row in the Evidence Tests panel (built once)
    folder_rows = {}  # key -> row inside a ghost folder (rebuilt with the folders)
    folder_svgs = {}  # ghost -> folder svg holder
    folder_match = {}  # ghost -> whether its border is currently highlighted
    ev_groups = []  # (container element, [keys]) for sub-test blocks and test-type cards
    taps = []  # monotonic timestamps of the current speed test window
    suspend = {'evidence': False}

    # Functions

    def is_complete(ghost):
        tests = ghost_folders[ghost]['ghost_tests']
        return bool(tests) and all((t['type'], t['name'], ghost) in crossed for t in tests)

    def set_crossed(row, is_crossed):
        if is_crossed:
            row.classes(add='test-crossed')
        else:
            row.classes(remove='test-crossed')

    def toggle_test(key):
        ghost = key[2]
        was_complete = is_complete(ghost)
        crossed.symmetric_difference_update({key})
        is_crossed = key in crossed
        for row in (ev_rows.get(key), folder_rows.get(key)):
            if row is not None:
                set_crossed(row, is_crossed)
        if is_complete(ghost) != was_complete:
            handle_evidence()  # reorder folders / recolor the name

    def current_speed():
        if len(taps) < 2 or taps[-1] <= taps[0]:
            return None
        return STEP_LENGTH_M * (len(taps) - 1) / (taps[-1] - taps[0])

    def speed_matches(ghost, speed, tol):
        vals = ghost_folders[ghost]['speed_vals']
        if not vals:
            return False
        if ghost in RANGE_SPEED_GHOSTS and len(vals) >= 2:
            return min(vals) - tol <= speed <= max(vals) + tol
        return any(abs(v - speed) <= tol for v in vals)

    def update_speed_matches():
        speed = current_speed()
        tol = tolerance.value if tolerance.value is not None else DEFAULT_SPEED_TOLERANCE
        for ghost, holder in folder_svgs.items():
            match = speed is not None and speed_matches(ghost, speed, tol)
            if folder_match.get(ghost) != match:
                folder_match[ghost] = match
                if match:
                    holder.classes(add='folder-match')
                else:
                    holder.classes(remove='folder-match')

    def refresh_speed():
        speed = current_speed()
        speed_lbl.set_text(f'{speed:.2f} m/s' if speed is not None else ' _._ m/s')
        tap_lbl.set_text(f'Taps: {len(taps)}')
        update_speed_matches()

    def tap_speed():
        taps.append(time.monotonic())
        refresh_speed()

    def new_test():
        taps.clear()
        refresh_speed()

    def reset_all():
        suspend['evidence'] = True
        for marker in evidence_markers.values():
            marker['state'].set_value('N')
        suspend['evidence'] = False
        crossed.clear()
        for row in ev_rows.values():
            set_crossed(row, False)
        taps.clear()
        speed_lbl.set_text(' _._ m/s')
        tap_lbl.set_text('Taps: 0')
        handle_evidence()

    def on_evidence_change():
        if not suspend['evidence']:
            handle_evidence()

    def on_key(e):
        if not e.action.keydown or e.action.repeat:
            return
        if e.modifiers.ctrl or e.modifiers.alt or e.modifiers.meta:
            return
        key = (e.key.name or '').lower()
        if key == 'f':
            tap_speed()
        elif key == 'n':
            new_test()
        elif key == 'r':
            reset_all()

    def update_ev_visibility(active):
        """Show Evidence Tests only for ghosts still possible; hide emptied blocks/cards."""
        for key, row in ev_rows.items():
            row.set_visibility(key[2] in active)
        for container, keys in ev_groups:
            container.set_visibility(any(k[2] in active for k in keys))

    def build_ev_tests():
        with ev_tests:
            with ui.row().classes('justify-center'):
                for test_type in game_data['Tests']:
                    type_keys = []
                    type_card = ui.card().classes('w-136')
                    ev_groups.append((type_card, type_keys))
                    with type_card:
                        ui.label(test_type).classes('ghost text-xl')
                        ui.separator()
                        for sub_test in game_data['Tests'][test_type]:
                            sub_keys = []
                            sub_block = ui.element('div').classes('border-l-2 px-2 rounded-r-lg bg-slate-200/10')
                            ev_groups.append((sub_block, sub_keys))
                            with sub_block:
                                ui.label(sub_test).classes('ghost text-lg')
                                for ghost_test, text in game_data['Tests'][test_type][sub_test].items():
                                    key = (test_type, sub_test, ghost_test)
                                    row = ui.row().classes('text-sm my-2 cursor-pointer test-item')
                                    row.on('click', lambda _, k=key: toggle_test(k))
                                    with row:
                                        ui.label(ghost_test).classes('iceberg text-sm text-gray-200 w-36')
                                        ui.label(text).classes('overlock text-sm text-gray-400 w-64')
                                    ev_rows[key] = row
                                    sub_keys.append(key)
                                    type_keys.append(key)

    def handle_evidence():
        folders.clear()
        folder_rows.clear()
        folder_svgs.clear()
        folder_match.clear()

        active = {}
        gathered = {}
        tested = {}
        val_map = {'N': None, 'T': True, 'F': False}

        for evi in evidence_markers:
            se = evidence_markers[evi]
            gathered[evi] = val_map[se['state'].value]

        # Determine which ghosts are still active based on gathered evidence
        for ghost in ghost_folders:
            data = ghost_folders[ghost]
            ghost_evidence = data['evidence']

            if not passes_sanity(data['sanity'], sanity_select.value or 0):
                continue  # no hunt threshold above the selected sanity

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
            ordered = sorted(active.items(), key=lambda kv: is_complete(kv[0]))  # stable: finished ghosts last
            for ghost, data in ordered:
                with folder_card(ghost, title_color='#EF4444' if is_complete(ghost) else None) as fcard:
                    folder_svgs[ghost] = fcard.svg_holder
                    with ui.row().classes('w-full h-full'):
                        with ui.column().classes('w-36 p-0'):  # Left side of folder
                            with ui.row():  # Evidence
                                for i in range(len(data['evidence'])):
                                    with ui.image(data['ev_imgs'][i]).classes('w-5 object-contain') as ev_icon:
                                        ev_icon.tooltip(data['evidence'][i])
                            with ui.scroll_area().classes(
                                    'w-full h-24 justify-center bg-indigo-950 rounded-sm border-2 border-indigo-800 gap-0'):  # Sanity thresholds

                                if type(data['sanity']) is float:
                                    with ui.row().classes('w-full'):
                                        ui.image(data['sanity_img']).classes('w-7 p-1')
                                        c_classes = 'ghost text-lg'
                                        if data['sanity'] > 0.65:
                                            c_classes += ' text-red-600'
                                        elif data['sanity'] < 0.5:
                                            c_classes += ' text-lime-400'
                                        ui.label(f'{round(data['sanity'] * 100)}%').classes(c_classes)

                                elif type(data['sanity']) is list:
                                    if type(data['sanity'][0]) is dict:
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
                                            sk, si = list(sanity.keys())[0], list(sanity.values())[0]

                                            with ui.row().classes('p-0 m-x-0 -m-y-4'):
                                                c_classes = 'ghost text-lg'
                                                if si > 0.65:
                                                    c_classes += ' text-red-600'
                                                elif si < 0.5:
                                                    c_classes += ' text-lime-400'

                                                ui.image(data['sanity_img']).classes('w-7 p-0 m-x-0 -m-y-4')
                                                ui.label(f'{round(si * 100)}%').classes(c_classes)
                                    else:
                                        for si in data['sanity']:
                                            with ui.row().classes('p-0 m-x-0 -m-y-4'):
                                                c_classes = 'ghost text-lg p-0 m-y-0 m-x-2'
                                                if si > 0.65:
                                                    c_classes += ' text-red-600'
                                                elif si < 0.5:
                                                    c_classes += ' text-lime-400'

                                                ui.image(data['sanity_img']).classes('w-7 p-0 -m-x-3 -m-y-4')
                                                ui.label(f'{round(si * 100)}%').classes(c_classes)

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
                                        sk, si = list(sanity.keys())[0], list(sanity.values())[0]

                                        with ui.row().classes('p-0 m-x-0 -m-y-4'):
                                            c_classes = 'ghost text-lg'
                                            if si > 0.65:
                                                c_classes += ' text-red-600'
                                            elif si < 0.5:
                                                c_classes += ' text-lime-400'

                                            ui.image(data['sanity_img']).classes('w-7 p-0 m-x-0 -m-y-4')
                                            ui.label(f'{round(si * 100)}%').classes(c_classes)

                        with ui.column().classes('w-48 p-0'):
                            speed_card = ui.card() \
                                .classes(
                                'relative w-full h-8 p-0 m-0 bg-cyan-100/10 rounded-md border-2 border-cyan-200') \
                                .props('')
                            with speed_card:
                                if data['speed_tt']:
                                    ui.icon('search').classes('absolute top-0 right-0')
                                if data['speed_t']:
                                    ui.icon('table_view').classes('absolute bottom-0 right-0')
                                speeds = data['speed']
                                with ui.row().classes('w-full'):
                                    ui.icon('directions_run').classes('absolute left-2 top-1').props(
                                        'size=sm color=cyan-4')
                                    if type(speeds) is list and len(speeds) > 1:
                                        speed_label = ui.label(
                                            f'{min(speeds)} - {max(speeds)}'
                                        )
                                    elif type(speeds) is list and len(speeds) == 1:
                                        speed_label = ui.label(speeds)
                                    else:
                                        speed_label = ui.label(
                                            'Unknown Speed'
                                        )

                                speed_label.classes(
                                    'absolute ghost text-lg top-1 left-10 text-cyan-500 text-bold'
                                )

                                if data['speed_tt']:
                                    with speed_card:
                                        ui.tooltip(
                                            data['speed_tt']
                                        ) \
                                            .classes(
                                            'text-lg w-128 bg-grey-950'
                                        ) \
                                            .props(
                                            'anchor="bottom middle" self="bottom middle'
                                        )

                            if data['speed_t'] in game_data[
                                'GhostSpeedTables']:  # Thaye names a table that doesn't exist
                                # data['speed_t'] is the table's name; the rows live in GhostSpeedTables
                                speed_table = game_data['GhostSpeedTables'][data['speed_t']]
                                metric = speed_table.get('Metrics', '')

                                def build_rows(temp='c', speed_table=speed_table, metric=metric):
                                    rows = []
                                    for k, v in speed_table.items():
                                        if k == 'Metrics':  # not a data row; used as the column header
                                            continue
                                        k = str(k)
                                        if metric == 'Temperature':  # '>15', '12-15', '<0'
                                            def convert(m):
                                                if m.isdigit():
                                                    m = int(m)
                                                    return str(round(m * 9 / 5 + 32, 1)) + '°' if temp == 'f' else str(
                                                        m) + '°'
                                                return f' {m} '

                                            label = ''.join(convert(x) for x in re.findall(r'\d+|\D', k))
                                        elif metric == 'Sanity':  # '.45-1' -> '45% - 100%'
                                            label = ' - '.join(f'{round(float(p) * 100)}%' for p in k.split('-'))
                                        else:  # Items
                                            label = k
                                        rows.append({'metric': label, 'speed': v})
                                    return rows

                                with ui.dialog() as speed_dialog, ui.card().classes('w-80 max-h-[80vh]'):
                                    ui.label(f'{ghost} Speed').classes('ghost text-xl text-cyan-500')

                                    speed_tbl = ui.table(
                                        columns=[
                                            {'name': 'metric', 'label': metric, 'field': 'metric', 'align': 'left'},
                                            {'name': 'speed', 'label': 'Speed (m/s)', 'field': 'speed',
                                             'align': 'right'},
                                        ],
                                        rows=build_rows(),
                                    ).props('flat bordered virtual-scroll dense').classes('w-full max-h-[55vh]')

                                    if metric == 'Temperature':
                                        ui.toggle(
                                            {'c': '°C', 'f': '°F'},
                                            value='c',
                                            # bind this ghost's table and row builder; the loop would otherwise
                                            # leave them pointing at the last ghost
                                            on_change=lambda e, tbl=speed_tbl, rows_fn=build_rows: tbl.update_rows(
                                                rows_fn(temp=e.value)
                                            ),
                                        )

                                    ui.button('Close', on_click=speed_dialog.close).props('flat')

                                speed_card.classes('cursor-pointer').on('click', speed_dialog.open)

                            test_card = ui.card() \
                                .classes(
                                'relative w-full h-24 p-0 m-0 bg-yellow-100/10 rounded-md border-2 border-yellow-200') \
                                .props('')

                            with test_card:
                                with ui.scroll_area().classes('w-full h-full'):
                                    if not data['ghost_tests']:
                                        ui.label('No tests right now!').classes('text-bold iceberg')
                                    for test in data['ghost_tests']:
                                        key = (test['type'], test['name'], ghost)
                                        row = ui.element('div').classes(
                                            'rounded-lg text-sm p-0 m-0 cursor-pointer test-item')
                                        row.on('click', lambda _, k=key: toggle_test(k))
                                        with row:
                                            ui.label(test['name']).classes('iceberg')
                                            ui.label(test['text']).classes('overlock')
                                        set_crossed(row, key in crossed)
                                        folder_rows[key] = row

        update_ev_visibility(active)
        update_speed_matches()

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
        <link href="https://fonts.googleapis.com/css2?family=Iceberg&family=Overlock:ital,wght@0,400;0,700;0,900;1,400;1,700;1,900&display=swap" rel="stylesheet">


        <style>.ghost {
            font-family: 'Trade Winds', system-ui;
            font-style: bold;
        }
        .iceberg {
            font-family: "Iceberg", sans-serif;
        }
        .overlock {
            font-family: "Overlock", sans-serif;
        }
        .test-item:hover { background: rgba(255, 255, 255, 0.06); }
        .test-crossed { opacity: 0.35; }
        .test-crossed, .test-crossed * { text-decoration: line-through; }
        .folder-match path { stroke: #FFFFFF !important; stroke-width: 4px !important; }
        </style>
        ''')

    with ui.header():

        ui.button('Evidence', on_click=lambda: evidence_drawer.toggle(), icon='rule').props(
            'color=amber-7 flat rounded dense').classes('ghost !text-md')
        ui.space()
        ui.label('Phasmobobia QRH').classes('ghost text-2xl')

    with ui.left_drawer(elevated=True, fixed=True, top_corner=True, value=True) as evidence_drawer:

        ui.label('Evidence').classes('ghost text-xl')

        for ev in evidence_markers:
            cd = ui.checkbox(on_change=lambda: on_evidence_change(), value='N').props(
                'color=pink dense toggle-indeterminate toggle-order=ft true-value=T false-value=N indeterminate-value=F modal-value=N')
            with cd:
                with ui.row().classes('w-full'):
                    ui.image(evidence_markers[ev]['icon']).classes('w-4 object-contain')
                    ui.label(ev).classes(f'color-{evidence_markers[ev]['color']}')
            evidence_markers[ev]['state'] = cd

        ui.separator()

        ui.label('Map').classes('ghost text-xl')
        map1 = ui.select(list(game_data['Maps']), on_change=lambda e: map_update(e)).classes(
            'ghost w-full !text-sm').props('outlined dense')
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
            metronome = ui.tab('Speed')
            sanity = ui.tab('Sanity')
        with ui.tab_panels(tabs, value=metronome).classes('w-full'):

            with ui.tab_panel(metronome):
                speed_btn = ui.button(on_click=tap_speed).classes('ghost w-full h-16 p-0 text-xl')

                with speed_btn:
                    with ui.column().classes('p-0 m-0'):
                        ui.label('Speed (F):').classes('text-inherit p-0')
                        speed_lbl = ui.label(' _._ m/s').classes('text-sm p-0')

                tap_lbl = ui.label('Taps: 0').classes('text-xs text-gray-400')

                tolerance = ui.number(
                    'Tolerance (m/s)', value=DEFAULT_SPEED_TOLERANCE, min=0.01, max=1, step=0.05, format='%.2f',
                    on_change=lambda: update_speed_matches(),
                ).classes('w-full').props('outlined dense')

                with ui.button_group().classes('w-full'):
                    ui.button('New (N)', on_click=new_test).classes('grow').props('color=accent')
                    ui.button('Reset (R)', on_click=reset_all).props('color=negative')

            with ui.tab_panel(sanity):
                sanity_select = ui.select(
                    options=[i for i in range(0, 105, 5)],
                    value=0,
                    label="Highest Hunt Sanity",
                    on_change=lambda: handle_evidence(),
                ) \
                    .classes('w-full justify-center') \
                    .props('rounded outlined color=pink-3')

        def open_map_dialog():
            dialog_map_img.set_source(map_img.source)
            map_dialog.open()

        def update_map_img():

            # noinspection bad-argument-type
            def update_info(map, map2: int | None = None, map2r: bool = False):

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
                    map_info_box.classes(
                        replace=f'row nowrap w-full rounded-md border -my-1 py-1 px-1 text-{mc} border-{mc}')

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
                map_img.set_source(
                    'https://gitlab.com/xplus-studios/xplus-toolkit/-/raw/main/logo/Icon-maintenence.png?ref_type=heads')

        def map_update(e):
            if game_data['Maps'][e.value].get('optional') is not None:
                map2.enable()
                map2.set_options(game_data['Maps'][e.value].get('optional'))
            else:
                map2.set_options([], value='')
                map2.disable()
            ui.update()
            update_map_img()

    with ui.expansion('Evidence Tests').classes('w-full ghost text-xl justify-center bg-slate-600 rounded-lg'):
        ev_tests = ui.column().classes('justify-center')

    with ui.element('div').classes('grow'):
        folders = ui.row().classes('justify-center')

    build_ev_tests()
    handle_evidence()
    ui.keyboard(on_key=on_key, repeating=False, ignore=['input', 'textarea'])