from nicegui import ui

ui.label('Hello from Railway and NiceGUI!')

ui.run(
    host='0.0.0.0',
    port=8080,
    dark=True
)