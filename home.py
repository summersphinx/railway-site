from nicegui import ui

from background import props_content

def content():
    with ui.card().classes(props_content):
        ui.label('Hello ' *500)

    with ui.card().classes(props_content):
        for i in range(20):
            ui.label('uwu')