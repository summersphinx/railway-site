from nicegui import ui
from pathlib import Path

import yaml

DIR = Path(__file__).parent / ""

def menu():

    with open(Path(f'{DIR}/menu.yaml'), 'r') as fh:
        tmp = yaml.safe_load(fh)
        styling = tmp['styling']
        header = tmp['header']
        footer = tmp['footer']

    ui.add_head_html('<script src="https://kit.fontawesome.com/ac723d76fa.js" crossorigin="anonymous"></script>')

    def toggle_ui(e):
        visible = e.value
        ui.run_javascript(f'''
            document.querySelectorAll(".ui-transition").forEach(function(el) {{
                el.classList.toggle("ui-hidden", {str(not visible).lower()});
            }});
        ''')

    hide_ui = ui.checkbox(value=True, on_change=toggle_ui) \
        .props(styling['ui_toggle']['props']).classes(styling['ui_toggle']['style'])
    with hide_ui:
        ui.tooltip('Hide UI').classes('text-lg')

    with ui.header().classes('bg-slate-900/90 rounded-xl border-2 mt-2 bg max-sm:hidden justify-self-center ui-transition'):
        for item in header:
            t = list(item.keys())[0]
            if t == 'btn':
                btn = ui.button()

                tmp_p = item[t]['props']
                tmp_s = item[t]['style']

                p = styling[tmp_p]['props']
                s = styling[tmp_p]['style']

                if 'ext_link' in tmp_s:
                    tmp_lnk = tmp_s.split('/')[1]
                    s = s[tmp_lnk]

                btn.props(p)
                btn.classes(s)
                if item[t].get('text', None):
                    btn.set_text(item[t]['text'])
                if item[t].get('link', None):
                    btn.on_click(lambda e=item[t]['link']: ui.navigate.to(e))
                if item[t].get('img', None):
                    with btn:
                        ui.image(item[t]['img']).classes('w-24 object-scale-down! m-0 p-0')
                if item[t].get('icon', None):
                    btn.set_icon(item[t]['icon'])


def footer():
    with ui.footer(fixed=False).classes('bg-transparent w-full h-16 items-center'):
        footer_content = [
            ["Created with ", "NiceGUI", "https://nicegui.io"],
            ["Hosted on ", "Railway.app", "https://railway.com?referralCode=CN9B5I"],
        ]
        with ui.grid(columns=1).classes('w-full items-center justify-center text-center'):
            ui.label('© 2026 X+ Studios. All rights reserved.').classes('text-md  text-gray-400 bg-transparent justify-self-center')
            for item in footer_content:
                with ui.row().classes('justify-center'):
                    ui.label(item[0]).classes('text-md  text-gray-400 bg-transparent justify-self-center')
                    ui.link(item[1], item[2])

            [ui.label() for i in range(3)]

