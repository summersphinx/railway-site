from nicegui import ui

from background import props_content
from background import md_css


content_buttons = [
    {
        'index': 0,
        'text': 'Play it here!',
        'link': '/projects/cr5',
        'icon': 'double_arrow',
        'props': 'push align="right"',
        'styling': 'absolute bottom-4 right-4 text-bold text-lg'
    },
]

contents = [
    '''
    # New Project Released!
    
    `Jul 17, 2026`
    
    CodeRandom5 is now available! A cryptographic puzzle game with a new puzzle every day!(UTC+00) Current
    cryptographic methods are Atbash, Caesar, and Autokey.
    ''',
    '''
    # Next Project
    
    The next project I am working on is a cellular automation with similar rules to [RPS7](https://xplus.dev/projects/rps7).
    More details to come soon!
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
