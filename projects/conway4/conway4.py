from nicegui import ui, app


def build_grid():
    image = ui.interactive_image(
        size=(1000, 1000), cross=True, sanitize=False,
        on_mouse=lambda e: e.sender.set_content(f'''
                <circle cx="{e.image_x}" cy="{e.image_y}" r="50" fill="orange" />
            '''),
    ).classes('w-1/2 bg-blue-50')


def handle_mouse(e):
    pass


def page():
    ui.label('test')

    with ui.row().classes('w-full'):
        with ui.column():
            pass
        with ui.column():

            image = ui.interactive_image(
                size=(10, 10), cross=True, sanitize=False,
                on_mouse=handle_mouse,
                events=['mousedown', 'mouseup', 'mousemove', 'mouseleave'],
            ).classes('w-1/2 bg-blue-50')

            gridlines = image.add_layer()
