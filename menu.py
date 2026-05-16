from nicegui import ui

def menu():
    ui.add_head_html('<script src="https://kit.fontawesome.com/ac723d76fa.js" crossorigin="anonymous"></script>')

    def toggle_ui(e):
        visible = e.value
        ui.run_javascript(f'''
            document.querySelectorAll(".ui-transition").forEach(function(el) {{
                el.classList.toggle("ui-hidden", {str(not visible).lower()});
            }});
        ''')

    hide_ui = ui.checkbox(value=True, on_change=toggle_ui).props('color=info size=100px checked-icon=visibility_off unchecked-icon=visibility dense').classes('fixed top-8 right-8 z-210')
    with hide_ui:
        ui.tooltip('Hide UI').classes('text-lg')

    with ui.header().classes('glass-card-bar justify-self-center ui-transition'):
        with ui.button(on_click=lambda: ui.navigate.to('/')).classes('grow h-full').props('flat'):
            ui.image('https://gitlab.com/xplus-studios/xplus-toolkit/-/raw/main/logo/xplus2.png').props('fit=scale-down').classes('h-16')
        header_links = {
            'Projects': lambda: ui.navigate.to('/projects'),
            'About': lambda: ui.navigate.to('/about'),
            'Contact': lambda: ui.navigate.to('/contact'),
        }
        for t, a in header_links.items():
            ui.button(t, on_click=a).classes('grow h-full text-2xl text-bold').props('flat color=indigo-11')

        header_ext_links = {
            'Gitlab': ['fa-brands fa-gitlab', 'https://gitlab.com/summersphinx/', 'text-orange-400'],
            'Discord': ['fa-brands fa-discord', 'https://discord.gg/kXdbByHCre', 'text-blue-500'],
            'Itch': ['fa-brands fa-itch-io', 'https://itch.io', 'text-red-400'],
        }
        with ui.row().classes('grow'):
            for t, d in header_ext_links.items():
                with ui.button(on_click=lambda url=d[1]: ui.navigate.to(url, new_tab=True)).classes('grow items-center justify-center').props('flat rounded'):
                    ui.icon(d[0]).classes(f'text-4xl text-center {d[2]}')
                    ui.tooltip(t).classes('text-lg')

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

