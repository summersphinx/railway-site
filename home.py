from nicegui import ui

from background import props_content
from background import md_css


content_buttons = [
    {
        'index': 0,
        'text': 'Try it out!',
        'link': '/projects/phas',
        'icon': 'double_arrow',
        'props': 'push align="right"',
        'styling': 'absolute bottom-4 right-4 text-bold text-lg'
    },
]

contents = [
    '''
    # Phasmophobia QRH Complete
    
    `Oct 13, 2026`
    
    While not my original plan to finish next, working on this project that has multiple filters has
    been a lot of fun. I am working on 2 more projects, so stay tuned for those to be announced and released!
    '''
]

def content():
    ui.add_css(md_css)
    for c_count in range(len(contents)):
        with ui.card().classes(props_content).classes(add='relative'):
            ui.markdown(contents[c_count])
            for btn in [b for b in content_buttons if b['index'] == c_count]:
                with ui.button(
                    text=str(btn['text']),
                    on_click=lambda e=btn['link']: ui.navigate.to(e),
                ).props(btn['props']).classes(btn['styling']):
                    ui.icon(btn['icon'])
