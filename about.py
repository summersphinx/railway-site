from nicegui import ui

from background import props_content
from background import md_css

md_text = '''
# So

This is about me. I make stuff. I usually can't finish a single project, but really like to restart every project multiple times.
This is my 7th attempt at a website. The one project I've redone the most is Stools, which is on version 4 revision 2. I 
should probably see a doctor about that, but I think the next concussion might also fix it.

So far all of my projects are built with Python. My first project I published in 2021 called CodeRandom. Since then, I've 
revised it 4 times, with only the first actually production ready. I plan on adding a version of all my old projects here in 
the future, but I have many other projects to get out of the way first.
'''


def content():
    ui.add_css(md_css)
    with ui.card().classes(props_content):
        ui.markdown(md_text)